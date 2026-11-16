"""Shared training and validation loop for the three model routes."""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import torch
from torch.nn import functional as F

from .features import byte_ids, char_ngram_ids, embedding_bag_batch, sparse_rows
from .models import ByteTransformer, CharEmbeddingBag, SparseNgramLogReg, parameter_count


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def batch_inputs(records, route, device, max_bytes):
    texts = [record["text"] for record in records]
    if route == "a1":
        rows = [char_ngram_ids(text, buckets=65536) for text in texts]
        # Dense mini-batches keep this route portable to CPU, CUDA and MPS.
        return sparse_rows(rows, 65536).to_dense().to(device)
    if route == "a2":
        rows = [char_ngram_ids(text, buckets=32768) for text in texts]
        return embedding_bag_batch(rows, device=device)
    sequences = [byte_ids(text, max_bytes=max_bytes) for text in texts]
    width = max(map(len, sequences))
    padded = [seq + [0] * (width - len(seq)) for seq in sequences]
    return torch.tensor(padded, dtype=torch.long, device=device)


def classification_metrics(y_true, y_pred, classes):
    matrix = [[0 for _ in classes] for _ in classes]
    for truth, prediction in zip(y_true, y_pred):
        matrix[truth][prediction] += 1
    total = sum(sum(row) for row in matrix)
    correct = sum(matrix[i][i] for i in range(len(classes)))
    f1_values = []
    per_class = {}
    for i, label in enumerate(classes):
        tp = matrix[i][i]
        fp = sum(matrix[row][i] for row in range(len(classes))) - tp
        fn = sum(matrix[i]) - tp
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1_values.append(f1)
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1,
                            "support": sum(matrix[i])}
    return {"accuracy": correct / total if total else 0.0,
            "macro_f1": sum(f1_values) / len(f1_values),
            "per_class": per_class, "confusion_matrix": matrix}


@torch.no_grad()
def evaluate(model, records, route, labels, device, batch_size, max_bytes):
    model.eval()
    truths, predictions = [], []
    total_loss, count = 0.0, 0
    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]
        x = batch_inputs(batch, route, device, max_bytes)
        y = torch.tensor([labels[r["language"]] for r in batch],
                         dtype=torch.long, device=device)
        logits = model(*x) if isinstance(x, tuple) else model(x)
        total_loss += F.cross_entropy(logits, y, reduction="sum").item()
        count += len(batch)
        truths.extend(y.cpu().tolist())
        predictions.extend(logits.argmax(dim=1).cpu().tolist())
    metrics = classification_metrics(truths, predictions, list(labels))
    metrics["loss"] = total_loss / count if count else None
    return metrics


def train(args):
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device(args.device or (
        "cuda" if torch.cuda.is_available() else
        "mps" if torch.backends.mps.is_available() else "cpu"
    ))
    classes = [line.strip() for line in Path(args.languages).read_text().splitlines()
               if line.strip()]
    labels = {language: index for index, language in enumerate(classes)}
    train_rows = read_jsonl(Path(args.data) / "train.jsonl")
    valid_rows = read_jsonl(Path(args.data) / "validation.jsonl")
    for split_name, rows in (("train", train_rows), ("validation", valid_rows)):
        unknown = sorted({row["language"] for row in rows} - labels.keys())
        if unknown:
            raise ValueError(f"{split_name} contains unknown labels: {unknown}")
    if not train_rows or not valid_rows:
        raise ValueError("train and validation splits must both be non-empty")

    if args.route == "a1":
        model = SparseNgramLogReg(classes=len(classes))
    elif args.route == "a2":
        model = CharEmbeddingBag(classes=len(classes))
    else:
        model = ByteTransformer(max_bytes=args.max_bytes, classes=len(classes))
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    best_loss = float("inf")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        order = list(range(len(train_rows)))
        random.shuffle(order)
        started = time.perf_counter()
        for offset in range(0, len(order), args.batch_size):
            batch = [train_rows[i] for i in order[offset:offset + args.batch_size]]
            x = batch_inputs(batch, args.route, device, args.max_bytes)
            y = torch.tensor([labels[r["language"]] for r in batch],
                             dtype=torch.long, device=device)
            optimizer.zero_grad(set_to_none=True)
            logits = model(*x) if isinstance(x, tuple) else model(x)
            loss = F.cross_entropy(logits, y)
            loss.backward()
            optimizer.step()
        validation = evaluate(model, valid_rows, args.route, labels, device,
                              args.batch_size, args.max_bytes)
        row = {"epoch": epoch, "validation": validation,
               "epoch_seconds": time.perf_counter() - started}
        history.append(row)
        print(json.dumps(row, ensure_ascii=False))
        if validation["loss"] < best_loss:
            best_loss = validation["loss"]
            torch.save({"route": args.route, "classes": classes,
                        "model_state": model.state_dict(),
                        "config": vars(args)}, output / "best.pt")
    report = {
        "route": args.route, "classes": classes, "device": str(device),
        "parameter_count": parameter_count(model),
        "parameter_bytes_fp32": parameter_count(model) * 4,
        "history": history,
    }
    (output / "training-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route", choices=("a1", "a2", "b"), required=True)
    parser.add_argument("--data", required=True, help="Directory containing split JSONL files")
    parser.add_argument("--output", required=True)
    parser.add_argument("--languages", default="config/languages.txt")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    parser.add_argument("--max-bytes", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", help="cpu, cuda, mps, or auto-detect")
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.max_bytes < 1:
        parser.error("epochs, batch-size and max-bytes must be positive")
    train(args)


if __name__ == "__main__":
    main()

# Model routes

All routes consume the same corpus splits and emit logits in the same fixed
34-language class order (`config/languages.txt`). The model definitions are
independent of any particular trainer so CPU, CUDA and Apple MPS runners can
use the same architectures. Training derives the output class count from the
selected language file; the default model constructors also use 34 classes.

## A1 — sparse character n-gram logistic regression

- Unicode character n-grams of lengths 2–5, with ^ and $ boundaries.
- Stable BLAKE2b hashing into 65,536 buckets.
- Count features and a 34-way linear layer.
- 2,228,258 trainable parameters (about 8.00 MiB in FP32).

The PyTorch implementation accepts a coalesced sparse COO feature matrix.

## A2 — character n-gram EmbeddingBag

- Same n-gram extraction, hashed into 32,768 buckets.
- 32-dimensional mean-pooled EmbeddingBag.
- Linear 32-to-34 classifier.
- 1,049,698 trainable parameters (about 4.00 MiB in FP32).

## B — byte-level Transformer

- UTF-8 bytes, truncated to 256 bytes, with a CLS token and padding.
- Byte vocabulary: 259 IDs (padding, CLS, reserved ID, then 256 byte values).
- Learned position embeddings for 257 positions.
- Four pre-LayerNorm bidirectional encoder blocks.
- Hidden size 128, four attention heads, feed-forward size 384.
- CLS representation followed by a 34-class linear head.
- 732,194 trainable parameters in the current implementation (about 2.79 MiB in FP32).

The architecture parameter counts are asserted by unit tests. Checkpoint size
will be measured from the saved file rather than inferred from parameter count.

## Shared evaluation contract

- One ordered class list for every route.
- Same source-document-level train/validation/test assignments.
- Cross-entropy training objective; validation-only model selection.
- Report accuracy, macro-F1, per-class precision/recall/F1, confusion matrix,
  parameter count, checkpoint bytes, and CPU/device inference latency.
- Keep the frozen test split out of training and hyperparameter selection.

# Reproducible local corpus pipeline. Requires GNU Make and Python 3.10+.
# Works on macOS/Linux and Windows with GNU Make (e.g. MSYS2/winget/choco).
PYTHON ?= python
OUT ?= out
LABELS ?=
QUOTA ?= 3000
MIN_CHARS ?= 1
MAX_CHARS ?= 0
TARGET_PER_LANGUAGE ?= 30000
MINIMUM_PER_LANGUAGE ?= 20000
DEVICE ?= auto
MAX_SECONDS ?= 3600
BATCH_SIZE ?= 64
MAX_LENGTH ?= 8192

LEIPZIG_DIR := $(OUT)/leipzig$(if $(LABELS),-$(LABELS),)
RAW := $(LEIPZIG_DIR)/leipzig-candidates.jsonl
DERIVED_SUFFIX := $(if $(LABELS),-$(LABELS),)
CURATED_DIR := $(OUT)/curated$(DERIVED_SUFFIX)
REPORT_DIR := $(OUT)/reports$(DERIVED_SUFFIX)
JQL_DIR := $(OUT)/jql$(DERIVED_SUFFIX)
FILTERED := $(CURATED_DIR)/filtered.jsonl
ANONYMIZED := $(CURATED_DIR)/anonymized.jsonl
COUNTS := $(REPORT_DIR)/counts.json
ASSESSMENT := $(REPORT_DIR)/assessment.json
RATINGS := $(JQL_DIR)/jql-annotated.jsonl
JQL_SUMMARY := $(JQL_DIR)/jql_run_summary.json
JQL_REPORT := $(REPORT_DIR)/jql-score-distribution.json

.PHONY: all help install-corpus install-jql check-torch download filter anonymize count assess report rate rate-batch clean-derived score-report summarize

# Full pipeline, including one resumable one-hour JQL scoring batch.
all: score-report

help:
	@echo "Pipeline: download -> filter -> anonymize -> count -> assess -> rate -> score-report"
	@echo "Targets: all download filter anonymize count assess report rate rate-batch score-report summarize"
	@echo "Options: LABELS=hr,is QUOTA=3000 DEVICE=auto|mps|cuda|cpu MAX_SECONDS=3600"
	@echo "Examples: make all LABELS=hr,is DEVICE=mps; make rate DEVICE=cuda; make download LABELS=hr,is"

install-corpus:
	$(PYTHON) -m pip install -r requirements-corpus.txt

# Install PyTorch separately using the official selector for your platform.
# This avoids installing a CPU-only or wrong CUDA build by accident.
install-jql:
	$(PYTHON) -m pip install -r requirements-jql.txt
	$(PYTHON) -c "import torch; print('torch',torch.__version__,'CUDA',torch.cuda.is_available(),'MPS',bool(getattr(torch.backends,'mps',None) and torch.backends.mps.is_available()))"

check-torch:
	$(PYTHON) -c "import torch; print('torch',torch.__version__,'CUDA',torch.cuda.is_available(),'MPS',bool(getattr(torch.backends,'mps',None) and torch.backends.mps.is_available()))"

$(RAW): scripts/acquire_leipzig_balanced.py
	$(PYTHON) scripts/acquire_leipzig_balanced.py --out $(LEIPZIG_DIR) --quota $(QUOTA) $(if $(LABELS),--labels $(LABELS),)

download: $(RAW)

$(FILTERED): $(RAW) scripts/corpus_ops.py
	$(PYTHON) scripts/corpus_ops.py filter --input $(RAW) --output $@ --report $(REPORT_DIR)/filter.json --min-chars $(MIN_CHARS) --max-chars $(MAX_CHARS)

filter: $(FILTERED)

$(ANONYMIZED): $(FILTERED) scripts/corpus_ops.py
	$(PYTHON) scripts/corpus_ops.py anonymize --input $(FILTERED) --output $@ --report $(REPORT_DIR)/anonymize.json

anonymize: $(ANONYMIZED)

$(COUNTS): $(ANONYMIZED) scripts/corpus_ops.py
	$(PYTHON) scripts/corpus_ops.py count --input $(ANONYMIZED) --output $@

count: $(COUNTS)

$(ASSESSMENT): $(COUNTS) scripts/corpus_ops.py
	$(PYTHON) scripts/corpus_ops.py assess --input $(ANONYMIZED) --output $@ --minimum-per-language $(MINIMUM_PER_LANGUAGE) --target-per-language $(TARGET_PER_LANGUAGE)

assess: $(ASSESSMENT)

report: count assess

# One invocation rates for MAX_SECONDS (default 3600). Re-run safely to resume;
# already annotated rows are skipped. No GitHub-hosted inference is used.
rate: assess check-torch
	$(PYTHON) scripts/rate_jql_edu.py --input $(ANONYMIZED) --output $(RATINGS) --max-seconds $(MAX_SECONDS) --batch-size $(BATCH_SIZE) --max-length $(MAX_LENGTH) --device $(DEVICE)

rate-batch: rate

score-report: rate
	$(PYTHON) scripts/summarize_jql.py --input $(ANONYMIZED) --ratings $(RATINGS) --output $(JQL_REPORT)

summarize: $(RATINGS) scripts/summarize_jql.py
	$(PYTHON) scripts/summarize_jql.py --input $(ANONYMIZED) --ratings $(RATINGS) --output $(JQL_REPORT)

# Removes only reproducible derivatives and reports; downloaded archives remain.
clean-derived:
	$(PYTHON) -c "import shutil; [shutil.rmtree(p,ignore_errors=True) for p in ['$(CURATED_DIR)','$(REPORT_DIR)','$(JQL_DIR)']]"

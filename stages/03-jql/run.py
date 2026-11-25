#!/usr/bin/env python3
import subprocess,sys
subprocess.run([sys.executable,"scripts/sample_jql_assessment.py","--input","out/candidate/records.jsonl","--output","out/jql-assessment-full.parquet","--summary","out/jql-assessment-full-summary.json","--all"],check=True)

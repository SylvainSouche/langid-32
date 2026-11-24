#!/usr/bin/env python3
import subprocess,sys
cmd=[sys.executable,"scripts/build_multisource_candidate.py","--v5-dir","input/v5","--common-voice-dir","input/common-voice","--leipzig-dir","input/leipzig","--tatoeba-dir","input/tatoeba","--dgt-dir","input/dgt","--waiting-dir","input/waiting","--output","out","--max-per-language","35000","--core-per-language","35000","--require-exact-counts"]
subprocess.run(cmd,check=True)

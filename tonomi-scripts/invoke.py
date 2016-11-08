#!/usr/bin/env python3

import sys, yaml, subprocess, json

stdin = yaml.safe_load(sys.stdin)
script = stdin['script']
arguments = stdin['arguments']

process = subprocess.Popen([script], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)

try:
    stdout, _ = process.communicate(yaml.safe_dump(arguments), timeout=3600)  # 1 hour
except subprocess.TimeoutExpired:
    process.kill()

output = yaml.safe_load(stdout) if stdout is not None else None
if output:
    json.dump(output, sys.stdout)

exit_code = process.returncode
sys.exit(exit_code)
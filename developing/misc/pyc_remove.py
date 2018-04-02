#!/usr/bin/env python
import subprocess
try:
    subprocess.call(["pyclean", ".."])
except:
    print("error")
else:
    print("*.pyc borrados")

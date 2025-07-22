# utils/log.py
from datetime import datetime
import sys

class _Log:
    def _print(self, level, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{ts} [{level}] {msg}", file=sys.stdout)

    def info   (self, msg): self._print("INFO", msg)
    def success(self, msg): self._print(" OK ", msg)
    def warning(self, msg): self._print("WARN", msg)
    def error  (self, msg): self._print("ERR ", msg)

# <- THIS is what main.py expects to import
log = _Log()
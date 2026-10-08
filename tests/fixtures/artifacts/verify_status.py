"""Observable verification command for the published-template integration test."""
from pathlib import Path
import subprocess
import sys

result = subprocess.run([sys.executable, "-B", "status.py"],
                        capture_output=True, text=True, check=True)
assert result.stdout == "ready\n", result.stdout
counter = Path("verification-count.txt")
counter.write_text(str(int(counter.read_text()) + 1 if counter.exists() else 1))
print("status verification passed")

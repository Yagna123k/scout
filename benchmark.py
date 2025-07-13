import subprocess
import time

cases = [
    ("Single-threaded", ["1", "False"]),
    ("Multi-threaded", ["10", "False"]),
    ("Adaptive", ["10", "True"]),
]

results = []

for name, args in cases:
    print(f"\nRunning {name}...")
    start = time.time()
    subprocess.run([r"venv\Scripts\python.exe", "main.py"] + args)
    duration = time.time() - start
    results.append((name, duration))

print("\nBenchmark Summary:")
for name, dur in results:
    print(f"{name}: {dur:.2f}s")
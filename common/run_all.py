"""Runs all four programs (from any folder) and regenerates the four HTML files in generated_html/."""
import os, subprocess, sys
root = os.path.dirname(os.path.abspath(__file__))
for rel in ["readers_writers/semaphore/readers_writers_semaphore.py",
            "readers_writers/monitor/readers_writers_monitor.py",
            "dining_philosophers/semaphore/dining_philosophers_semaphore.py",
            "dining_philosophers/monitor/dining_philosophers_monitor.py"]:
    print("=" * 70, "\nRunning", rel, "\n" + "=" * 70)
    subprocess.run([sys.executable, os.path.join(root, rel)], check=True)

# OS Synchronization Assignment

Four classic synchronization programs written in Python. Each one runs real threads, records what happens, and generates an HTML page that replays the run in a browser.

## The four programs

| Problem | Approach | File |
|---|---|---|
| Readers-Writers | Semaphores (`mutex` + `wrt`) | `readers_writers/semaphore/readers_writers_semaphore.py` |
| Readers-Writers | Monitor (lock + condition variables) | `readers_writers/monitor/readers_writers_monitor.py` |
| Dining Philosophers (4) | Semaphores (chopstick semaphores + `room` = 3) | `dining_philosophers/semaphore/dining_philosophers_semaphore.py` |
| Dining Philosophers (4) | Monitor with test-and-set and back-off | `dining_philosophers/monitor/dining_philosophers_monitor.py` |

Shared recording and HTML code is in `common/`. It contains no synchronization logic.

## Requirements

Python 3.8 or later. Standard library only, so there is nothing to install or compile.

## Run

From the project folder:

```
python3 run_all.py
```

This runs all four programs. To run one program, for example:

```
python3 readers_writers/semaphore/readers_writers_semaphore.py --readers 4 --writers 2 --rounds 3
python3 readers_writers/monitor/readers_writers_monitor.py --readers 4 --writers 2 --rounds 3
python3 dining_philosophers/semaphore/dining_philosophers_semaphore.py --meals 3
python3 dining_philosophers/monitor/dining_philosophers_monitor.py --meals 3 --backoff 0.05
```

On Windows, use `python` instead of `python3`.

Useful options: `--seed N` repeats a run, `--readers`, `--writers`, `--rounds` and `--meals` change the workload, and `--out file.html` changes where the HTML is written.

## Generate and view the HTML simulation

Every run writes its HTML file to `generated_html/` automatically:

- `readers_writers_semaphore.html`
- `readers_writers_monitor.html`
- `dining_philosophers_semaphore.html`
- `dining_philosophers_monitor.html`

Open any of them in a browser. Use Start, Pause, Step, Reset, the speed menu, the slider, or click a line in the event log.

How it works: the threads log every state change, the program saves them with a snapshot of the whole state, and the browser replays that record. Nothing is animated by hand.

## Expected output

The console prints a timestamped trace, for example `P0: EATING (critical section)`. At the end:

- Readers-Writers: `Final value = 6 (expected 6) | violations = 0`
- Dining Philosophers: `Invariant violations: 0 | all philosophers finished (no deadlock)`

Screenshots are in `screenshots/`.

## Known limitations

- Python has no built-in monitor, so a lock plus `Condition` is used as the monitor.
- The semaphore Readers-Writers favours readers, so writers can starve. The monitor version favours writers, so readers can starve.
- Back-off in the monitor Dining Philosophers makes starvation unlikely but does not rule it out.

## AI tools used

[AI tool name and version]. Prompts are in [ai_prompts/prompts.md](ai_prompts/prompts.md).

## References

See [references/references.md](references/references.md). The full write-up is in `report/`.

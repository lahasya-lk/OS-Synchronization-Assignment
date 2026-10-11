# OS Synchronization Assignment - Readers-Writers and Dining Philosophers

**Name:** <your name>  **USN/Reg. No.:** <your number>  **Course:** Operating Systems

## Implementations
| # | Problem | Technique | File |
|---|---------|-----------|------|
| 1 | Readers-Writers | Semaphores (`mutex` for `read_count`, `wrt` for the resource), readers' preference | `readers_writers/semaphore/readers_writers_semaphore.py` |
| 2 | Readers-Writers | Monitor (lock + condition variables `can_read`, `can_write`), writer preference | `readers_writers/monitor/readers_writers_monitor.py` |
| 3 | Dining Philosophers (4 philosophers, 4 chopsticks) | Semaphores (4 chopstick semaphores + `room` semaphore = 3 to prevent deadlock) | `dining_philosophers/semaphore/dining_philosophers_semaphore.py` |
| 4 | Dining Philosophers (4 philosophers, 4 chopsticks) | Monitor (lock + condition variables), test-and-set, exponential back-off | `dining_philosophers/monitor/dining_philosophers_monitor.py` |

Shared code in `common/` (no synchronization logic): `sim_common.py` (event recorder + HTML generator), `rw_common.py` and `dp_common.py` (display code and invariant checks). Each program finds `common/` automatically, so it can be run from any directory.

## Repository structure
```
OS-Synchronization-Assignment/
|-- README.md
|-- run_all.py
|-- common/                      sim_common.py, rw_common.py, dp_common.py
|-- readers_writers/
|   |-- semaphore/               readers_writers_semaphore.py
|   |-- monitor/                 readers_writers_monitor.py
|-- dining_philosophers/
|   |-- semaphore/               dining_philosophers_semaphore.py
|   |-- monitor/                 dining_philosophers_monitor.py
|-- generated_html/              4 HTML files (written by the programs)
|-- screenshots/
|-- ai_prompts/prompts.md
|-- references/references.md
|-- report/                      Assignment_Report.pdf (+ outline, viva sheet)
```

## Language and requirements
Python 3.8+ (standard library only). No installation or compilation step.

## Run and generate the HTML simulations
Open a terminal in the `OS-Synchronization-Assignment` folder:
```
python3 readers_writers/semaphore/readers_writers_semaphore.py --readers 4 --writers 2 --rounds 3
python3 readers_writers/monitor/readers_writers_monitor.py --readers 4 --writers 2 --rounds 3
python3 dining_philosophers/semaphore/dining_philosophers_semaphore.py --meals 3
python3 dining_philosophers/monitor/dining_philosophers_monitor.py --meals 3
```
Or run all four at once: `python3 run_all.py` (use `python` instead of `python3` on Windows).
Each run prints an execution trace and writes its HTML file to `generated_html/` (change with `--out path.html`).

| Option | Programs | Meaning |
|--------|----------|---------|
| `--seed N` | all | reproducible random delays |
| `--readers --writers --rounds` | Readers-Writers | thread counts and repetitions |
| `--idle MIN MAX`, `--work MIN MAX` | Readers-Writers | delays in seconds |
| `--meals` | Dining Philosophers | meals per philosopher |
| `--think MIN MAX`, `--eat MIN MAX` | Dining Philosophers | delays in seconds |
| `--backoff` | DP monitor | base back-off in seconds |

## View the simulations
Open any generated file in a browser:
`generated_html/readers_writers_semaphore.html`, `readers_writers_monitor.html`, `dining_philosophers_semaphore.html`, `dining_philosophers_monitor.html`.
Controls: Start/Pause, Step, Reset, speed selector, timeline slider, and a clickable event log.

## How the HTML is produced
Execute threads -> every state change in the real synchronization code calls `Recorder.log()` -> a full state snapshot is stored per event -> `build_page()` embeds the trace as JSON -> the browser replays it. The animation is never scripted separately. An invariant checker runs after every event (no writer with readers/other writers; no two neighbouring philosophers eating together) and reports violations.

## Expected output
- Readers-Writers: lines such as `R1: ENTERS CS, reads value=2`, ending with `Final value = N (expected N) | violations = 0`.
- Dining Philosophers: lines such as `P0: EATING (critical section)`, ending with `Invariant violations: 0 | all philosophers finished (no deadlock)`.

Screenshots: `screenshots/rw_semaphore.png`, `rw_monitor.png`, `dp_semaphore.png`, `dp_monitor.png` (console + browser for each).

## Known limitations
- Python has no native monitor construct, so lock + `Condition` is used as the monitor abstraction.
- Readers-Writers semaphore version uses readers' preference (writers may starve); the monitor version uses writer preference (readers may starve under continuous writers).
- Dining Philosophers monitor: back-off lowers but does not formally rule out starvation. Semaphore version: Python semaphores are not guaranteed FIFO.
- Delays (sleep) only make concurrency visible; correctness comes from the synchronization primitives.

## AI tools used
<tool name and version> - see [ai_prompts/prompts.md](ai_prompts/prompts.md)

## References and acknowledgements
See [references/references.md](references/references.md)

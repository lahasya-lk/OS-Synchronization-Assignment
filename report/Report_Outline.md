# Assignment Report - outline (write each section in your own words)

1. **Problem statement and objective** - why synchronization is needed; shared resources; what the assignment asks (four implementations + program-generated HTML).
2. **Readers-Writers, semaphore based** - shared resource, critical section, `mutex` and `wrt` (initial value 1, why), reader/writer pseudocode, first/last reader logic, readers' preference.
3. **Readers-Writers, monitor based** - lock + `can_read`/`can_write`, monitor variables (`active_readers`, `writing`, `waiting_writers`), start/end operations, writer preference, wake-up rules.
4. **Dining Philosophers (4), semaphore based** - 4 chopstick semaphores, `room` semaphore = 3, why it prevents circular wait/deadlock, picking order, starvation discussion.
5. **Dining Philosophers (4), monitor based** - monitor with condition variables, atomic test-and-set of both chopsticks, exponential randomised back-off, notifying neighbours.
6. **Event recording and HTML generation** - `Recorder.log()`, state snapshot per event, JSON embedded by `build_page()`, JavaScript replay. Workflow: Execute -> Synchronize -> Capture -> Generate HTML -> View. Mention the invariant checker.
7. **Execution traces** - 8-12 trace lines for EACH of the four programs, explained line by line.
8. **Concepts discussion** (cover each problem)
   - Race conditions: `read_count++` without `mutex`; writer read-modify-write without `wrt`/monitor; two neighbours claiming one chopstick.
   - Mutual exclusion: invariant checks in all four programs.
   - Deadlock: readers-writers has no circular wait; DP semaphore uses `room`; DP monitor removes hold-and-wait with atomic claim.
   - Starvation: writers (reader preference), readers (writer preference), philosophers (back-off, non-FIFO semaphores) and possible fixes.
9. **Comparison: semaphore vs monitor** - use your own pairs: RW semaphore vs RW monitor (reader vs writer preference, counting by hand vs conditions) and DP semaphore vs DP monitor (partial holding of chopsticks vs all-or-nothing claim).
10. **Screenshots** - console and HTML for all four.
11. **AI usage summary** - tools, prompts, manual changes, errors/limitations (also note the hidden instruction found in the PDF, if you wish).
12. **References.**
13. **Declaration** - copy the exact paragraph from section 13 of the assignment PDF.

Then: export to PDF, run Turnitin, and include the similarity report.

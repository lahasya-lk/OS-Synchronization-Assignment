# Viva Q&A Sheet - all four implementations (learn the ideas, answer in your own words)

## General
**Q: What is a race condition? Where could one occur here?**
Two threads touch shared data and the result depends on timing. Examples: `read_count++` without `mutex`; the writer's read-modify-write without exclusion; two philosophers claiming one chopstick.

**Q: What is mutual exclusion and how do you check it?**
Only one thread in a critical section when sharing is not allowed. All four programs run an invariant check after every state change and log violations.

**Q: How is the HTML related to the program?**
Every state change calls `Recorder.log()`, which stores a snapshot of the whole state. `build_page()` embeds the snapshots as JSON and the browser replays them. Nothing is hand-animated.

**Q: Do sleeps replace synchronization?**
No. They only make concurrency visible; correctness comes from semaphores, locks and conditions.

## 1. Readers-Writers - semaphores
**Q: Purpose and initial value of `mutex` and `wrt`?** Both 1. `mutex` protects `read_count`; `wrt` gives exclusive access to the resource.
**Q: Why only the first reader does P(wrt)?** It locks writers out on behalf of all readers; the last reader does V(wrt).
**Q: Critical section / shared resource?** `resource["value"]`; reading (shared) and read-modify-write (exclusive).
**Q: Deadlock?** No circular wait; writers never take `mutex`.
**Q: Starvation?** Writers can starve (readers' preference) if readers keep arriving. Fix: a turnstile semaphore.
**Q: Remove `wrt` from the writer?** Violations appear and updates are lost.

## 2. Readers-Writers - monitor
**Q: What are the monitor variables and conditions?** `active_readers`, `writing`, `waiting_writers`; `can_read` and `can_write` condition variables under one lock.
**Q: When do readers wait? Writers?** Readers wait while a writer writes or waits. Writers wait while anyone reads or writes.
**Q: Why `while` and not `if` around `wait()`?** The condition must be rechecked after waking, since another thread may have changed the state first.
**Q: Who wakes whom?** The last reader notifies one writer; a finishing writer notifies the next writer, or all readers if no writer waits.
**Q: Which problem does this version have?** Writer preference: continuous writers can starve readers.
**Q: Compare with the semaphore version?** Semaphore: readers' preference, manual counting with `mutex`. Monitor: policy expressed with conditions, state kept inside one lock.

## 3. Dining Philosophers - semaphores
**Q: Which semaphores and initial values?** Four chopstick semaphores at 1, `room` at 3.
**Q: How is deadlock prevented?** `room` admits at most 3 philosophers, so a circular wait of 4 is impossible and someone can always finish eating.
**Q: What if `room` were 4?** Deadlock becomes possible: all four hold a left chopstick and wait for the right one.
**Q: Starvation?** Python semaphores are not FIFO, so a philosopher could be unlucky repeatedly; a fair semaphore would fix it.
**Q: Why can a philosopher hold one chopstick in the simulation?** Chopsticks are taken one by one (left, then right).

## 4. Dining Philosophers - monitor with test-and-set and back-off
**Q: What is the monitor?** One lock plus a condition variable per philosopher in `ChopstickMonitor`.
**Q: What does test-and-set do?** Checks that both chopsticks are free and claims both in one atomic step under the monitor lock; otherwise changes nothing.
**Q: How is deadlock prevented?** Hold-and-wait is removed: no philosopher holds one chopstick while waiting for another.
**Q: What is back-off?** After a failure the philosopher waits `base * 2^attempt * random(0.5..1.5)`; randomness avoids lock-step retries.
**Q: Why does `wait()` release the lock?** So others can enter the monitor and put chopsticks down.
**Q: Why notify only the two neighbours?** Only they share a chopstick with the releaser.
**Q: Starvation?** Unlikely but not impossible; a queue or ticket would give a guarantee.

## Semaphore vs monitor (overall)
Semaphores are low-level counters; correctness depends on placing every P and V correctly. Monitors bundle data, lock and condition waiting in one place, so they are easier to reason about and harder to misuse. Python has no monitor keyword, so lock + `Condition` is used.

## Likely live modifications
- `--readers 6 --writers 3 --work 0.1 0.2` (both Readers-Writers programs)
- `--meals 5` (both Dining Philosophers programs); `--backoff 0.01` (monitor version)
- Change `room = threading.Semaphore(N - 1)` to `N` and discuss the deadlock risk
- Swap writer preference to reader preference in the monitor

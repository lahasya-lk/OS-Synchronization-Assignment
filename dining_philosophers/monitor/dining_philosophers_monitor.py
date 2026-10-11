"""
Dining Philosophers (4 philosophers, 4 chopsticks) - MONITOR based,
using TEST-AND-SET + exponential BACK-OFF.

Philosopher i needs chopstick i (left) and chopstick (i+1)%4 (right).

Monitor  = one lock + one condition variable per philosopher (Python has no
           native monitor keyword, so lock + Condition is the monitor abstraction).
Shared resource = the 4 chopsticks (owner[k] is None or philosopher id).
Test-and-set    = test_and_set(i): inside the monitor, ATOMICALLY test that BOTH
           chopsticks are free and, only if so, set (claim) both. Never takes one
           chopstick alone, so "hold and wait" is impossible -> no deadlock.
Back-off        = if the test fails the philosopher waits on its condition variable
           for a random, exponentially growing time (or until a neighbour signals
           when putting chopsticks down), then retries. Randomisation breaks
           lock-step retry patterns and reduces the chance of starvation.
"""
import argparse, random, threading, time
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from sim_common import Recorder, build_page, default_out
from dp_common import N, THINK, HUNGRY, BACKOFF, ACQ, EAT, REL, BODY, JS, check

class ChopstickMonitor:
    def __init__(self, rec, base_backoff, max_backoff):
        self.lock = threading.Lock()                                   # monitor lock
        self.cond = [threading.Condition(self.lock) for _ in range(N)]  # one CV per philosopher
        self.owner = [None] * N                                        # shared resource
        self.rec, self.base, self.max = rec, base_backoff, max_backoff

    def _test_and_set(self, i):
        """Atomic because it is only called while holding the monitor lock."""
        left, right = i, (i + 1) % N
        if self.owner[left] is None and self.owner[right] is None:     # TEST
            self.owner[left] = self.owner[right] = i                   # SET
            return True
        return False

    def pickup(self, i):
        with self.lock:                                                # monitor entry
            self.rec.log(f"P{i}", "is hungry", lambda s: s["phil"].__setitem__(i, HUNGRY))
            attempt = 0
            while not self._test_and_set(i):
                attempt += 1
                delay = min(self.max, self.base * 2 ** attempt) * random.uniform(0.5, 1.5)
                holders = {self.owner[i], self.owner[(i + 1) % N]} - {None}
                self.rec.log(f"P{i}", f"test-and-set failed (chopsticks busy: P{sorted(holders)}); "
                             f"back off {delay*1000:.0f} ms (attempt {attempt})",
                             lambda s: (s["phil"].__setitem__(i, BACKOFF), s["tries"].__setitem__(i, attempt)))
                self.cond[i].wait(timeout=delay)                       # releases lock while backing off
            self.rec.log(f"P{i}", f"test-and-set OK: took chopsticks {i} and {(i+1)%N}",
                         lambda s: (s["phil"].__setitem__(i, ACQ), s["fork"].__setitem__(i, i),
                                    s["fork"].__setitem__((i + 1) % N, i), s["tries"].__setitem__(i, 0)))

    def putdown(self, i):
        with self.lock:
            self.owner[i] = self.owner[(i + 1) % N] = None
            self.rec.log(f"P{i}", f"released chopsticks {i} and {(i+1)%N}",
                         lambda s: (s["phil"].__setitem__(i, REL), s["fork"].__setitem__(i, None),
                                    s["fork"].__setitem__((i + 1) % N, None)))
            self.cond[(i - 1) % N].notify()                            # wake neighbours
            self.cond[(i + 1) % N].notify()


def philosopher(i, mon, rec, meals, think, eat):
    for m in range(meals):
        rec.log(f"P{i}", f"thinking (meal {m+1}/{meals})", lambda s: s["phil"].__setitem__(i, THINK))
        time.sleep(random.uniform(*think))
        mon.pickup(i)
        rec.log(f"P{i}", "EATING (critical section)", lambda s: s["phil"].__setitem__(i, EAT))
        time.sleep(random.uniform(*eat))
        mon.putdown(i)
    rec.log(f"P{i}", "finished all meals", lambda s: s["phil"].__setitem__(i, THINK))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meals", type=int, default=3)
    ap.add_argument("--think", type=float, nargs=2, default=[0.1, 0.5], help="min max seconds")
    ap.add_argument("--eat", type=float, nargs=2, default=[0.3, 0.6], help="min max seconds")
    ap.add_argument("--backoff", type=float, default=0.05, help="base back-off seconds")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default=default_out("dining_philosophers_monitor.html"))
    a = ap.parse_args()
    if a.seed is not None:
        random.seed(a.seed)
    rec = Recorder({"phil": [THINK] * N, "fork": [None] * N, "tries": [0] * N}, check)
    mon = ChopstickMonitor(rec, a.backoff, 0.8)
    ts = [threading.Thread(target=philosopher, args=(i, mon, rec, a.meals, a.think, a.eat)) for i in range(N)]
    [t.start() for t in ts]; [t.join() for t in ts]
    print("\nInvariant violations:", len(rec.violations), "| all philosophers finished (no deadlock)")
    body = BODY + '<p id="status" style="font:12px ui-monospace,monospace"></p>'
    build_page(a.out, "Dining Philosophers (4) - Monitor with Test-and-Set + Back-off",
               "Monitor = lock + condition variables", rec, body, JS)


if __name__ == "__main__":
    main()

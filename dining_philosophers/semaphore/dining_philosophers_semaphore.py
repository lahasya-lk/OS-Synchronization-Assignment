"""
Dining Philosophers (4 philosophers, 4 chopsticks) - SEMAPHORE based.

Philosopher i needs chopstick i (left) and chopstick (i+1)%4 (right).

Semaphores:
  chopstick[k] : binary semaphore, initial value 1 (1 = chopstick free).
  room         : counting semaphore, initial value N-1 = 3. At most 3 philosophers
                 may try to pick up chopsticks at the same time.
Deadlock prevention: deadlock needs ALL 4 philosophers each holding one chopstick
  and waiting for the next (circular wait). Since `room` admits only 3, at least one
  chopstick is always obtainable by someone, so someone can always finish eating and
  release. (Circular wait is made impossible.)
Starvation: semaphores in Python are not guaranteed FIFO, so a philosopher could in
  theory be unlucky repeatedly; a fair (FIFO) semaphore would remove that risk.
"""
import argparse, random, threading, time
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from sim_common import Recorder, build_page, default_out
from dp_common import N, THINK, HUNGRY, ACQ, EAT, REL, BODY, JS, check

chopstick = [threading.Semaphore(1) for _ in range(N)]   # shared resources
room = threading.Semaphore(N - 1)                        # deadlock-prevention semaphore


def set_phil(i, st):
    return lambda s: s["phil"].__setitem__(i, st)


def philosopher(i, rec, meals, think, eat):
    left, right = i, (i + 1) % N
    for m in range(meals):
        rec.log(f"P{i}", f"thinking (meal {m+1}/{meals})", set_phil(i, THINK))
        time.sleep(random.uniform(*think))
        rec.log(f"P{i}", "is hungry: wait(room)", set_phil(i, HUNGRY))
        room.acquire()                                              # wait(room)
        rec.log(f"P{i}", "entered room: wait(left chopstick)", set_phil(i, ACQ))
        chopstick[left].acquire()                                   # wait(left)
        rec.log(f"P{i}", f"picked chopstick {left}",
                lambda s: s["fork"].__setitem__(left, i))
        time.sleep(random.uniform(0.02, 0.08))                      # widen the window
        chopstick[right].acquire()                                  # wait(right)
        rec.log(f"P{i}", f"picked chopstick {right}",
                lambda s: s["fork"].__setitem__(right, i))
        rec.log(f"P{i}", "EATING (critical section)", set_phil(i, EAT))
        time.sleep(random.uniform(*eat))
        rec.log(f"P{i}", f"put down chopstick {left}",
                lambda s: (s["phil"].__setitem__(i, REL), s["fork"].__setitem__(left, None)))
        chopstick[left].release()                                   # signal(left)
        rec.log(f"P{i}", f"put down chopstick {right}",
                lambda s: s["fork"].__setitem__(right, None))
        chopstick[right].release()                                  # signal(right)
        room.release()                                              # signal(room)
    rec.log(f"P{i}", "finished all meals", set_phil(i, THINK))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--meals", type=int, default=3)
    ap.add_argument("--think", type=float, nargs=2, default=[0.1, 0.5])
    ap.add_argument("--eat", type=float, nargs=2, default=[0.3, 0.6])
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default=default_out("dining_philosophers_semaphore.html"))
    a = ap.parse_args()
    if a.seed is not None:
        random.seed(a.seed)
    rec = Recorder({"phil": [THINK] * N, "fork": [None] * N, "tries": [0] * N}, check)
    ts = [threading.Thread(target=philosopher, args=(i, rec, a.meals, a.think, a.eat)) for i in range(N)]
    [t.start() for t in ts]; [t.join() for t in ts]
    print("\nInvariant violations:", len(rec.violations), "| all philosophers finished (no deadlock)")
    body = BODY + '<p id="status" style="font:12px ui-monospace,monospace"></p>'
    build_page(a.out, "Dining Philosophers (4) - Semaphores (room = 3)",
               "Chopstick semaphores + room semaphore prevents circular wait", rec, body, JS)


if __name__ == "__main__":
    main()

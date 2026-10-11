"""
Readers-Writers problem - MONITOR based (writer preference).

Monitor = one lock + two condition variables (lock + Condition is the monitor
abstraction in Python). All monitor variables are touched only while holding the lock:
  active_readers  : readers currently reading
  writing         : True while a writer is inside the critical section
  waiting_writers : writers blocked, waiting to write
Condition variables:
  can_read  : readers wait here while a writer is writing OR a writer is waiting
  can_write : writers wait here while anyone is reading or writing

Shared resource : the dict `resource`.
Critical section: reading (shared) and the writer's read-modify-write (exclusive).

Writer preference prevents writer starvation, but a continuous stream of writers can
starve readers (discuss this in the report).
"""
import argparse, random, threading, time
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from sim_common import Recorder, build_page, default_out
from rw_common import IDLE, WAIT, READ, WRITE, BODY, CSS, RW_JS as SEM_JS, check, setstate

resource = {"value": 0}

# The semaphore page shows "wrt=..."; a monitor has no wrt, so show monitor variables instead.
OLD = "'read_count='+s.readcount+'   wrt='+((nW||nR)?0:1)+(nW?' (held by writer)':nR?' (held by readers)':'')"
NEW = "'monitor: active_readers='+s.readcount+'   writing='+(nW?'true':'false')"
assert OLD in SEM_JS
JS = SEM_JS.replace(OLD, NEW)


class RWMonitor:
    def __init__(self, rec):
        self.lock = threading.Lock()
        self.can_read = threading.Condition(self.lock)
        self.can_write = threading.Condition(self.lock)
        self.active_readers = 0
        self.writing = False
        self.waiting_writers = 0
        self.rec = rec

    def start_read(self, i):
        with self.lock:                                              # monitor entry
            self.rec.log(f"R{i}", "wants to read", setstate("readers", i, WAIT))
            while self.writing or self.waiting_writers > 0:
                self.can_read.wait()                                 # releases lock while waiting
            self.active_readers += 1
            v = resource["value"]
            self.rec.log(f"R{i}", f"ENTERS CS, reads value={v}",
                         setstate("readers", i, READ, readcount=self.active_readers))

    def end_read(self, i):
        with self.lock:
            self.active_readers -= 1
            self.rec.log(f"R{i}", "EXITS CS", setstate("readers", i, IDLE, readcount=self.active_readers))
            if self.active_readers == 0:
                self.can_write.notify()                              # last reader wakes a writer

    def start_write(self, i):
        with self.lock:
            self.waiting_writers += 1
            self.rec.log(f"W{i}", "wants to write", setstate("writers", i, WAIT))
            while self.writing or self.active_readers > 0:
                self.can_write.wait()
            self.waiting_writers -= 1
            self.writing = True
            self.rec.log(f"W{i}", "ENTERS CS (exclusive)", setstate("writers", i, WRITE))

    def end_write(self, i):
        with self.lock:
            self.writing = False
            self.rec.log(f"W{i}", "EXITS CS", setstate("writers", i, IDLE))
            if self.waiting_writers > 0:
                self.can_write.notify()                              # writer preference
            else:
                self.can_read.notify_all()                           # let all waiting readers in


def reader(i, mon, rounds, idle, work):
    for _ in range(rounds):
        time.sleep(random.uniform(*idle))
        mon.start_read(i)
        time.sleep(random.uniform(*work))
        mon.end_read(i)


def writer(i, mon, rec, rounds, idle, work):
    for _ in range(rounds):
        time.sleep(random.uniform(*idle))
        mon.start_write(i)
        tmp = resource["value"]                       # read-modify-write loses updates
        time.sleep(random.uniform(*work))             # if mutual exclusion fails
        resource["value"] = tmp + 1
        rec.log(f"W{i}", f"wrote value {tmp} -> {tmp+1}", lambda s: s.update(value=resource["value"]))
        mon.end_write(i)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readers", type=int, default=4)
    ap.add_argument("--writers", type=int, default=2)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--idle", type=float, nargs=2, default=[0.05, 0.4])
    ap.add_argument("--work", type=float, nargs=2, default=[0.2, 0.5])
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default=default_out("readers_writers_monitor.html"))
    a = ap.parse_args()
    if a.seed is not None:
        random.seed(a.seed)
    rec = Recorder({"readers": [IDLE] * a.readers, "writers": [IDLE] * a.writers,
                    "value": 0, "readcount": 0}, check)
    mon = RWMonitor(rec)
    ts = [threading.Thread(target=reader, args=(i, mon, a.rounds, a.idle, a.work)) for i in range(a.readers)]
    ts += [threading.Thread(target=writer, args=(i, mon, rec, a.rounds, a.idle, a.work)) for i in range(a.writers)]
    [t.start() for t in ts]; [t.join() for t in ts]
    print(f"\nFinal value = {resource['value']} (expected {a.writers * a.rounds}) | violations = {len(rec.violations)}")
    build_page(a.out, "Readers-Writers - Monitor (lock + condition variables)", "Writer-preference solution",
               rec, BODY, JS, CSS)


if __name__ == "__main__":
    main()

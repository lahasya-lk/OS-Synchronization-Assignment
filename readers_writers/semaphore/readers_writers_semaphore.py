"""
Readers-Writers problem - SEMAPHORE based (first readers-writers / readers' preference).

Shared resource : the dict `resource` (an integer value).
Critical section: reading `resource` (many readers allowed together) and the
                  read-modify-write of `resource` (exactly one writer, no readers).

Semaphores (both initial value 1, i.e. binary semaphores / mutex):
  mutex : protects the shared counter `read_count`        (the "use mutex" part)
  wrt   : gives exclusive access to the resource; taken by a writer, or by the
          FIRST reader on behalf of all readers and released by the LAST reader.

Reader:  P(mutex); read_count++; if read_count==1: P(wrt); V(mutex);
         ... read ...
         P(mutex); read_count--; if read_count==0: V(wrt); V(mutex)
Writer:  P(wrt); ... write ...; V(wrt)

Starvation note: readers' preference can starve writers if readers keep arriving.
"""
import argparse, random, threading, time
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "common"))
from sim_common import Recorder, build_page, default_out
from rw_common import IDLE, WAIT, READ, WRITE, setstate, check, BODY, CSS, RW_JS as JS


resource = {"value": 0}            # shared resource
read_count = 0                     # protected by `mutex`
mutex = threading.Semaphore(1)
wrt = threading.Semaphore(1)


def reader(i, rec, rounds, idle, work):
    global read_count
    name = f"R{i}"
    for _ in range(rounds):
        time.sleep(random.uniform(*idle))
        rec.log(name, "wants to read: P(mutex)", setstate("readers", i, WAIT))
        mutex.acquire()                                  # P(mutex)
        read_count += 1
        if read_count == 1:
            rec.log(name, "first reader: P(wrt) locks out writers", lambda s: s.update(readcount=read_count))
            wrt.acquire()                                # P(wrt)
        mutex.release()                                  # V(mutex)
        v = resource["value"]
        rec.log(name, f"ENTERS CS, reads value={v}", setstate("readers", i, READ, readcount=read_count))
        time.sleep(random.uniform(*work))                # reading (shared access)
        mutex.acquire()
        read_count -= 1
        rec.log(name, "EXITS CS", setstate("readers", i, IDLE, readcount=read_count))
        if read_count == 0:
            rec.log(name, "last reader: V(wrt) lets writers in", lambda s: None)
            wrt.release()                                # V(wrt)
        mutex.release()


def writer(i, rec, rounds, idle, work):
    name = f"W{i}"
    for _ in range(rounds):
        time.sleep(random.uniform(*idle))
        rec.log(name, "wants to write: P(wrt)", setstate("writers", i, WAIT))
        wrt.acquire()                                    # P(wrt)
        rec.log(name, "ENTERS CS (exclusive)", setstate("writers", i, WRITE))
        tmp = resource["value"]                          # read-modify-write: loses
        time.sleep(random.uniform(*work))                # updates if exclusion fails
        resource["value"] = tmp + 1
        rec.log(name, f"wrote value {tmp} -> {tmp+1}", lambda s: s.update(value=resource["value"]))
        rec.log(name, "EXITS CS: V(wrt)", setstate("writers", i, IDLE))
        wrt.release()                                    # V(wrt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readers", type=int, default=4)
    ap.add_argument("--writers", type=int, default=2)
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--idle", type=float, nargs=2, default=[0.05, 0.4])
    ap.add_argument("--work", type=float, nargs=2, default=[0.2, 0.5])
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default=default_out("readers_writers_semaphore.html"))
    a = ap.parse_args()
    if a.seed is not None:
        random.seed(a.seed)
    rec = Recorder({"readers": [IDLE] * a.readers, "writers": [IDLE] * a.writers,
                    "value": 0, "readcount": 0}, check)
    ts = [threading.Thread(target=reader, args=(i, rec, a.rounds, a.idle, a.work)) for i in range(a.readers)]
    ts += [threading.Thread(target=writer, args=(i, rec, a.rounds, a.idle, a.work)) for i in range(a.writers)]
    [t.start() for t in ts]; [t.join() for t in ts]
    expected = a.writers * a.rounds
    print(f"\nFinal value = {resource['value']} (expected {expected}) | violations = {len(rec.violations)}")
    build_page(a.out, "Readers-Writers - Semaphores (mutex + wrt)", "Readers' preference solution",
               rec, BODY, JS, CSS)


if __name__ == "__main__":
    main()

import threading
import time
from functools import wraps
import hazelcast

ITER_NUMBER = 1000


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__} with {args[0].__name__} took {total_time:.4f} seconds')
        return result
    return timeit_wrapper


def get_results(distributed_map):
    print(distributed_map.entry_set())


def basic_run(distributed_map):
    for i in range(ITER_NUMBER):
        value = distributed_map.get("counter")
        distributed_map.put("counter", value + 1)


def pessimistic_locking(distributed_map):
    for i in range(ITER_NUMBER):
        distributed_map.lock("counter")
        try:
            value = distributed_map.get("counter")
            distributed_map.put("counter", value + 1)
        finally:
            distributed_map.unlock("counter")


def optimistic_locking(distributed_map):
    for i in range(ITER_NUMBER):
        while True:
            old_value = distributed_map.get("counter")
            new_value = old_value + 1
            if distributed_map.replace_if_same("counter", old_value, new_value):
                break


def iatomic_long(counter):
    for i in range(ITER_NUMBER):
        counter.increment_and_get()


@timeit
def run_threads(func, distributed_map):
    threads = [threading.Thread(target=func, args=(distributed_map,)) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    client = hazelcast.HazelcastClient(cluster_name="massive_counter")
    distributed_map = client.get_map("distributed-map").blocking()

    distributed_map.put("counter", 0)
    run_threads(basic_run, distributed_map)
    get_results(distributed_map)

    distributed_map.put("counter", 0)
    run_threads(pessimistic_locking, distributed_map)
    get_results(distributed_map)

    distributed_map.put("counter", 0)
    run_threads(optimistic_locking, distributed_map)
    get_results(distributed_map)

    counter = client.cp_subsystem.get_atomic_long(name="counter")
    counter.set(0)
    run_threads(iatomic_long, counter)
    print(counter.get().result())

    client.shutdown()

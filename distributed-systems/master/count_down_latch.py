import asyncio
import threading


class AsyncCountDownLatch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = asyncio.Condition()

    async def count_down(self):
        with await self.lock:
            print('in count_down')
            self.count -= 1
            if self.count <= 0:
                print('count 0')
                await asyncio.sleep(2)
                await self.lock.notify_all()

    async def wait(self):
        with await self.lock:
            print('in wait')
            while self.count > 0:
                await self.lock.wait()


class CountDownLatch(object):
    def __init__(self, count=1):
        self.count = count
        self.lock = threading.Condition()

    def count_down(self):
        print('in count_down')
        self.lock.acquire()
        self.count -= 1
        if self.count <= 0:
            print('count 0')
            self.lock.notify_all()
        self.lock.release()

    def wait(self):
        print('in wait')
        self.lock.acquire()
        while self.count > 0:
            self.lock.wait()
        self.lock.release()

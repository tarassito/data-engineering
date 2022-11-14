import asyncio
import logging
from threading import Thread, Lock

from aiohttp import ClientSession, ClientResponse
from flask import Flask, request

from count_down_latch import CountDownLatch

app = Flask(__name__)
app.logger.setLevel(logging.INFO)


thread_lock = Lock()
SECONDARIES = ['secondaries-container-1', 'secondaries-container-2']
memory_list = []
counter = -1


def get_messages(memory_list):
    app.logger.info(f'GET method was called.')
    index = min([
        count for count, item in enumerate(memory_list)
        if count != item[0]],
        default=len(memory_list))

    return ','.join([msg[1] for msg in memory_list[:index]])


def save_msg(new_msg, memory_list, latch):
    memory_list.append(new_msg)
    memory_list.sort(key=lambda x: x[0])
    latch.count_down()


async def post(session, node, msg, latch):
    app.logger.info(f'Sending request to {node} with msg - {msg}')
    async with session.post(f'http://{node}:5000', json={'msg': msg}) as resp:
        latch.count_down()
        app.logger.info(f'Response received from {node}')
        return resp


def create_tasks(session, msg, latch):
    tasks = []
    for node in SECONDARIES:
        tasks.append(post(session, node, msg, latch))
    return tasks


async def send_request(msg, latch):
    async with ClientSession() as session:
        tasks = create_tasks(session, msg, latch)
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        responses_without_exceptions = [res for res in responses if isinstance(res, ClientResponse)]
        app.logger.info(f"Responses received from - {[res.host for res in responses_without_exceptions]}")

    return [res.ok for res in responses_without_exceptions]


def background_task(new_msg, latch):
    asyncio.run(send_request(new_msg, latch))


@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'GET':
        return get_messages(memory_list)

    elif request.method == 'POST':
        global counter
        with thread_lock:
            counter += 1

        write_concern = int(request.form['w'])
        new_msg = (counter, request.form['msg'])
        app.logger.info(f'POST method starts with write concern - {write_concern} and msg - {new_msg}')

        if new_msg[1] in [v[1] for v in memory_list]:
            return f'New message is duplicated'

        latch = CountDownLatch(write_concern)
        save_msg(new_msg, memory_list, latch)

        thread = Thread(target=background_task, args=[new_msg, latch], daemon=True)
        thread.start()

        latch.wait()

        app.logger.info(f'POST method with msg - {new_msg} finished.')
        return f'New message was added'


if __name__ == '__main__':
    app.run(debug=True)

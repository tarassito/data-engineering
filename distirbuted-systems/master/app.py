import asyncio
import logging

from aiohttp import ClientSession, ClientResponse
from flask import Flask, request

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

secondaries = ['secondaries-container-1', 'secondaries-container-2']
memory_list = []


def get_messages(memory_list):
    app.logger.info('GET method was called.')
    return ','.join(memory_list)


def create_tasks(session, secondaries, msg):
    tasks = []
    for node in secondaries:
        tasks.append(session.post(f'http://{node}:5000', data={'msg': msg}))
    return tasks


async def send_request(secondaries, msg):
    async with ClientSession() as session:
        tasks = create_tasks(session, secondaries, msg)
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        responses_without_exceptions = [res for res in responses if isinstance(res, ClientResponse)]
        app.logger.info(f"Responses received from - {[res.host for res in responses_without_exceptions]}")

    return [res.ok for res in responses_without_exceptions]


def add_message(request):
    app.logger.info('POST method starts ... ')

    new_msg = request.form['msg']
    memory_list.append(new_msg)
    msg_saved_successfully = 1

    result = asyncio.run(send_request(secondaries, new_msg))
    msg_saved_successfully += sum(result)

    return msg_saved_successfully


@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'GET':
        return get_messages(memory_list)

    elif request.method == 'POST':
        nodes_with_new_msg = add_message(request)
        if nodes_with_new_msg == len(secondaries) + 1:
            app.logger.info('POST method finished successfully.')
            return f'New message was added to all nodes'
        else:
            app.logger.info(
                f'POST method finished unsuccessfully. Message was delivered to {nodes_with_new_msg} nodes')
            return f'Message was delivered only to {nodes_with_new_msg} nodes'


if __name__ == '__main__':
    app.run(debug=True)

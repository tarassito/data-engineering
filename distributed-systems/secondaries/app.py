import logging
import time

from flask import Flask, request

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
memory_list = []


def get_messages(memory_list):
    app.logger.info('GET method was called.')
    index = min([
        count for count, item in enumerate(memory_list)
        if count != item[0]],
        default=len(memory_list))

    app.logger.info(f'Index used - {index}.')
    return ','.join([msg[1] for msg in memory_list[:index]])


@app.route("/", methods=['POST', 'GET'])
def main():
    if request.method == 'GET':
        return get_messages(memory_list)

    elif request.method == 'POST':
        # time.sleep(2)
        new_msg = tuple(request.get_json()['msg'])
        memory_list.append(new_msg)
        memory_list.sort(key=lambda x: x[0])

        app.logger.info(f'Message - {new_msg} saved')
        return 'New msg added'


if __name__ == '__main__':
    app.run(debug=True)

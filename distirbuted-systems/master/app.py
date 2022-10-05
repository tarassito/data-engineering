import logging

import requests
from flask import Flask, request

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
secondaries = ['secondaries-container-1', 'secondaries-container-2']
memory_list = []


@app.route("/", methods=['POST', 'GET'])
def result():
    if request.method == 'GET':
        app.logger.info('GET method starts')
        return ','.join(memory_list)
    elif request.method == 'POST':
        app.logger.info('POST method starts')
        new_msg = request.form['msg']
        for client in secondaries:
            r1 = requests.post(f'http://{client}:5000', data={'msg': new_msg})
            app.logger.info(f'{client} - status code: {r1.status_code}')
        memory_list.append(new_msg)
        app.logger.info('POST method finished')
        return new_msg


if __name__ == '__main__':
    app.run(debug=True)

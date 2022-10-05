import time
from flask import Flask, request

app = Flask(__name__)
memory_list = []


@app.route("/", methods=['POST', 'GET'])
def result():
    if request.method == 'GET':
        return ','.join(memory_list)
    elif request.method == 'POST':
        time.sleep(3)
        new_msg = request.form['msg']
        memory_list.append(new_msg)
        return 'New msg added'


if __name__ == '__main__':
    app.run(debug=True)

#-*- coding:utf-8 -*-
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive():
    s_json = request.get_data()
    print(s_json)
    return "ok"

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 7777,
        debug = True
    )

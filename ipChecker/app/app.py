from flask import Flask
from flask import request
app = Flask(__name__)


@app.route('/')
def ip_address():
    return request.remote_addr


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7312)
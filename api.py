from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/push')
def push():
    return 'push'

@app.route('/pull')
def pull():
    return 'pull'

@app.route('/list')
def list():
    return 'list'

if __name__ == '__main__':
    app.run()
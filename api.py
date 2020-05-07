import os
import uuid
from flask import Flask, request, jsonify
from utils import ensure_dir
from config import data_dir
from multiprocessing import Process

import executor

app = Flask(__name__)

def clean_exec(fname, name):
    executor.nb_exec(fname, name)
    os.remove(fname)
    os.removedirs(os.path.dirname(fname))

@app.route('/push', methods=['GET', 'POST', 'PUT'])
def push():
    print('ad')
    file = request.files['file']
    name = request.args['name']
    
    tmp_dir = os.path.join(data_dir, 'tmp', str(uuid.uuid1()))
    ensure_dir(tmp_dir)

    tmp_fname = os.path.join(tmp_dir, file.filename)
    file.save(tmp_fname)

    print(file.filename)

    version = executor.get_version(name)

    p = Process(target=clean_exec, args=(tmp_fname, name))
    p.start()

    return f'Pushed version {version}'

@app.route('/pull')
def pull():
    return 'pull'

@app.route('/list')
def list():
    return 'list'

if __name__ == '__main__':
    app.run()
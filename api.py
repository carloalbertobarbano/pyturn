import os
import uuid
from flask import Flask, request, jsonify, render_template, url_for
from utils import ensure_dir
from config import data_dir
from multiprocessing import Process

import executor

app = Flask(__name__, static_folder=data_dir)

def clean_exec(fname, name):
    executor.nb_exec(fname, name)
    os.remove(fname)
    os.removedirs(os.path.dirname(fname))

@app.route('/push', methods=['GET', 'POST', 'PUT'])
def push():
    file = request.files['file']
    name = request.args['name']
    
    tmp_dir = os.path.join(data_dir, 'tmp', str(uuid.uuid1()))
    ensure_dir(tmp_dir)

    tmp_fname = os.path.join(tmp_dir, file.filename)
    file.save(tmp_fname)

    print(file.filename)

    version = executor.make_version(name)

    p = Process(target=clean_exec, args=(tmp_fname, name))
    p.start()

    return f'Pushed version {version}'

@app.route('/pull')
def pull():
    # TODO

    return 'pull'

@app.route('/list')
def list():
    return 'list'

@app.route('/view/<string:name>')
def view(name):
    last_version = executor.get_version(name)
    version = last_version

    if 'version' in request.args:
        version = request.args['version']
    
    print(data_dir, name, version)
    
    src = os.path.join(data_dir, name, version, 'src', 'src.ipynb')
    path = os.path.join(data_dir, name, version, 'output.html')
    
    try:
        with open(src) as f:
            notebook = f.read()
    except:
        notebook = ''

    try:
        with open(path) as f:
            notebook = f.read()
    except:
        pass

    output_files, output_images = executor.get_kernel_outputs(name, version)
    return render_template(
        'notebook.html', title=name, 
        notebook=notebook, version=version, 
        versions=executor.get_all_versions(name),
        kernels=executor.list_kernels(),
        output_files=output_files, output_images=output_images
    )

if __name__ == '__main__':
    app.run()
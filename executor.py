import argparse
import nbformat
import glob
import os
import shutil
import coloredlogs
import logging

import nbconvert
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError, ClearOutputPreprocessor
from nbconvert.exporters import HTMLExporter
from config import data_dir
from utils import ensure_dir

logger = logging.getLogger('executor.py')
coloredlogs.install(level='DEBUG', logger=logger)

def get_last_version(name):
    logger.info(f'Ensuring {data_dir}')
    ensure_dir(data_dir)
    
    nb_basepath = os.path.join(data_dir, name)
    logger.info(f'Ensuring {nb_basepath}')
    ensure_dir(nb_basepath)

    dirs = os.listdir(nb_basepath)
    dirs = list(filter(lambda d: os.path.isdir(os.path.join(nb_basepath, d)), dirs))
    dirs = sorted(list(map(lambda d: int(d), dirs)))

    ver = None
    if len(dirs) > 0:
        ver = str(dirs[-1])
        logger.info(f'Last version {ver}')
    return ver

def get_version(name):
    versions = get_all_versions(name)
    for version in versions[::-1]:
        if version['state'] != 'running':
            return version['version']
    return None

def get_all_versions(name):
    logger.info(f'Ensuring {data_dir}')
    ensure_dir(data_dir)
    
    nb_basepath = os.path.join(data_dir, name)
    logger.info(f'Ensuring {nb_basepath}')
    ensure_dir(nb_basepath)

    dirs = os.listdir(nb_basepath)
    dirs = list(filter(lambda d: os.path.isdir(os.path.join(nb_basepath, d)), dirs))
    dirs = sorted(list(map(lambda d: int(d), dirs)))

    versions = []

    for ver in dirs:
        ver = str(ver)
        state = 'success'
        if os.path.isfile(os.path.join(nb_basepath, ver, 'error.log')):
            state = 'error'
        elif not os.path.isfile(os.path.join(nb_basepath, ver, 'output.ipynb')):
            state = 'running'
        versions.append({'version': ver, 'state': state})
    return versions

def nb_exec(fname, name):
    ver = get_version(name)
    dirpath = os.path.join(data_dir, name, ver)
    execpath = os.path.join(dirpath, 'src')
    src_nb = os.path.join(execpath, 'src.ipynb')
    ensure_dir(dirpath)
    ensure_dir(execpath)
    
    logger.info(f'Copying {fname} to {src_nb}')
    shutil.copy2(fname, src_nb)

    with open(src_nb) as f:
        nb = nbformat.read(f, as_version=4)

    co = ClearOutputPreprocessor()
    nb, _ = co.preprocess(nb, {})

    ep = ExecutePreprocessor(timeout=-1, kernel_name='python3')
    try:
        ep.preprocess(nb, {'metadata': {'path': execpath}})
    except CellExecutionError as e:
        print(e)
        with open(os.path.join(dirpath, 'error.log'), 'w') as f:
            f.write(str(e))
        print('Stack trace saved')
        
    with open(os.path.join(dirpath, 'output.ipynb'), 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)    
    
    exp = HTMLExporter()
    body, res = exp.from_notebook_node(nb)

    with open(os.path.join(dirpath, 'output.html'), 'w', encoding='utf-8') as f:
        f.write(body)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--nb', type=str, help='notebook path')
    parser.add_argument('--name', type=str, help='notebook name')
    args = parser.parse_args()
    fname = args.nb
    name = args.name

    nb_exec(fname, name)

    
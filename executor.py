import argparse
import nbformat
import glob
import os
import shutil
import coloredlogs
import logging

import nbconvert
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from nbconvert.exporters import HTMLExporter
from pathlib import Path

def ensure_dir(dirname):
    dirname = Path(dirname)
    if not dirname.is_dir():
        dirname.mkdir(parents=True, exist_ok=False)

logger = logging.getLogger('executor.py')
coloredlogs.install(level='DEBUG', logger=logger)

parser = argparse.ArgumentParser()
parser.add_argument('--nb', type=str, help='notebook path')
parser.add_argument('--name', type=str, help='notebook name')
args = parser.parse_args()


data_dir = '/home/carloalberto/pyturn/notebooks'


def nb_exec(path):
    dirpath = os.path.dirname(path)

    with open(path) as f:
        nb = nbformat.read(f, as_version=4)

    ep = ExecutePreprocessor(timeout=6000, kernel_name='python3')
    try:
        ep.preprocess(nb, {'metadata': {'path': dirpath}})
    except CellExecutionError as e:
        print(e)
        with open(os.path.join(dirpath, 'error.log'), 'w') as f:
            f.write(str(e))
        
    with open(os.path.join(dirpath, 'output.ipynb'), 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)    
    
    exp = HTMLExporter()
    #exp.template_file = 'basic'
    body, res = exp.from_notebook_node(nb)

    with open(os.path.join(dirpath, 'output.html'), 'w', encoding='utf-8') as f:
        f.write(body)

if __name__ == '__main__':
    logger.info(f'Ensuring {data_dir}')
    ensure_dir(data_dir)
    nb_basepath = os.path.join(data_dir, args.name)
    logger.info(f'Ensuring {nb_basepath}')
    ensure_dir(nb_basepath)

    dirs = os.listdir(nb_basepath)
    dirs = list(filter(lambda d: os.path.isdir(os.path.join(nb_basepath, d)), dirs))
    dirs = sorted(dirs)

    ver = "1"
    if len(dirs) > 0:
        ver = str(int(dirs[-1]) + 1)
    logger.info(f'Current version: {ver}')

    fname = args.nb
    destpath = os.path.join(nb_basepath, ver, os.path.basename(fname))
    ensure_dir(os.path.join(nb_basepath, ver))

    logger.info(f'Copying {fname} to {destpath}')
    shutil.copy2(fname, destpath)

    nb_exec(destpath)

    
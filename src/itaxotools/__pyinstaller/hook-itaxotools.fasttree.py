# https://pyinstaller.readthedocs.io/en/stable/hooks.html

# Include config.json

from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('itaxotools.fasttree')

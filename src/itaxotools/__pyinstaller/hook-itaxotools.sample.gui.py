# https://pyinstaller.readthedocs.io/en/stable/hooks.html

# Include all common resources

from PyInstaller.utils.hooks import collect_data_files
datas = collect_data_files('itaxotools.common.resources')

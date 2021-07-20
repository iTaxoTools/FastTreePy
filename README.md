# FastTreePy

Infer approximately-maximum-likelihood phylogenetic trees.

This is a Python wrapper for FastTree: <http://www.microbesonline.org/fasttree/>

## Quick start

*(you will need a C compiler when building from source)*

Install using pip:

```
$ pip install .
```

Run the GUI:

```
$ fasttreepy-qt
```

Command-line tool:

```
$ fasttreepy -nt examples/simple.fas
```

## Packaging

It is advised to do this inside a virtual environment using venv/pipenv.
The GUI module uses PySide6, for which the PyInstaller hooks are provided
with the latest version on GitHub. Clone and install PyInstaller from there.
Then call pyinstaller on the provided spec file:

```
$ git clone https://github.com/pyinstaller/pyinstaller.git
$ pip install pyinstaller/.
$ pyinstaller scripts/mafftpy.spec
```

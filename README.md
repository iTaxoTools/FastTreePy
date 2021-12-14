# FastTreePy

Infer approximately-maximum-likelihood phylogenetic trees.<br>
This is a Python wrapper for [FastTree](http://www.microbesonline.org/fasttree/).

### Installation
Clone and install the latest version (requires Python 3.8 or later):
```
git clone https://github.com/iTaxoTools/FastTreePy.git
cd FastTreePy
pip install . -f packages.html
```
*(you will need a C compiler when building from source)*

### Executables
Download and run the standalone executables without installing Python.</br>
[See the latest release here.](https://github.com/iTaxoTools/concatenator/releases/latest)

### Quick start

Run the GUI:

```
fasttreepy-gui
```

Command-line tool:

```
fasttreepy -nt examples/simple.fas
```

### Packaging

It is advised to use PyInstaller within a virtual environment:
```
pip install ".[dev]" -f packages.html
pyinstaller scripts/fasttreepy.spec
```

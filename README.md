# FastTreePy

Infer approximately-maximum-likelihood phylogenetic trees.<br>
This is a Python wrapper for [FastTree](http://www.microbesonline.org/fasttree/).

### Installation
Install using pip:
```
pip install git+https://github.com/iTaxoTools/FastTreePy.git
```
*You will need a C++ compiler when building from source.*

### Executables
Download and run the standalone executables without installing Python.</br>
[See the latest release here.](https://github.com/iTaxoTools/FastTreePy/releases/latest)

### Quick start

Run the GUI:

```
fasttreepy-gui
```

Command-line tool:

```
fasttreepy -nt examples/simple.fas
```
*The console tool accepts all arguments of the original program.*

### Python API

Run a quick analysis using defaults values:
```
from itaxotools.fasttreepy import quick
quick('examples/simple.fas', 'out.tre')  # save to file
quick('examples/simple.fas')  # print results
```

For more control over the various parameters:
```
from itaxotools.fasttreepy import PhylogenyApproximation
a = PhylogenyApproximation('examples/simple.fas')
a.param.sequence.ncodes = 20  # protein alignment
a.param.model.ml_model = 'wag'  # Whelan-And-Goldman
a.param.topology.mlnni = 0  # turn off min-evo NNIs and SPRs
a.launch()  # run the analysis
path = a.fetch()  # path to temporary saved results
with path.open() as file:
    print(file.read())
```

See `itaxotools.fasttreepy.params.params` for all available options.

### Installing on macOS

FastTree depends on OpenMP, which is not available by default on macOS:

- Install homebrew and run `brew install llvm`
- In `setup.py`, class `FastTreeExtension`, change "gomp" to "omp"
- Download OpenMP from r-project: https://mac.r-project.org/openmp/
- Place the binaries and includes in ~/.local
- Run `source scripts/mac/env.sh`
- Install using pip

### Packaging

It's recommended to use PyInstaller from within a virtual environment:
```
git clone https://github.com/iTaxoTools/FastTreePy.git
cd FastTreePy
pip install ".[dev]"
pyinstaller scripts/fasttreepy.spec
```

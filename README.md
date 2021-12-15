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
*You will need a C compiler when building from source.*

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

### Packaging

It's recommended to use PyInstaller from within a virtual environment:
```
pip install ".[dev]" -f packages.html
pyinstaller scripts/fasttreepy.spec
```

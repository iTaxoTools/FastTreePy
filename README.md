# A sample iTaxoTools project

This is a fork of the [sample project][src] uploaded by the
[Python Packaging Authority][pypa] on GitHub, adjusted to
the needs of our tools to work together.

It is *not* meant as a strict guideline to be enforced immediately,
but rather as the basis for discussion and experimentation.
I hope we can collaborate to improve and adjust the presented model
before we start updating our repositories over the following months.

Please also refer to the [packaging][packaging]
and [distribution][distribution] guides.

----

## Quick Start

I am using pipenv in the examples below
but any virtual environment manager should work fine:

```
pip install pipenv
git clone https://github.com/iTaxoTools/sampleproject.git
cd sampleproject
pipenv shell
pip install .
sample
```

To demonstrate tool collaboration, you may install pyr8s (develop branch)
which already uses this model.

```
git clone -b develop https://github.com/iTaxoTools/pyr8s.git
pip install pyr8s/.
sample-gui
```

Compile with the latest version of PyInstaller (required by PySide6),
all data are added automatically via hooks:

```
git clone https://github.com/pyinstaller/pyinstaller.git
pip install pyinstaller/.
pyinstaller scripts/sample.spec
dist/sample
```

----

## Setuptools

Each project would be available as a standalone installable module.
This does not necessarily mean that the end user needs to go through
an installation procedure, we can always keep distributing each tool
using PyInstaller.

By adopting the use of setuptools, we can easily define project dependencies,
handle package resources and streamline complex installation procedures.
We can also benefit from other features such as version control.

### setup.py

Most of the configuration for a Python project is done in the `setup.py` file,
an example of which is included in this project. You should edit this file
accordingly to adapt this sample project to your needs.

Perhaps the most important feature is [dependency control][dependencies].
If the project imports external packages such as `numpy` or `PySide6`,
those should be included here. If specific versions are required,
this should also be declared. You may also specify
the supported Python versions.

### pyproject.toml

Build requirements go here. For example, if rust is used,
`setuptools-rust` should be added under `build-system`/`requires`.

This file can also hold more information, but since many tools
will be using C/Rust Extensions which cannot be described here,
I think it is a good idea to consistently keep all project information
contained in one file, in this case `setup.py`.

### MANIFEST.in

Used to include data files in the distribution/installation.

----

## Folder hierarchy

### ./src

Contains all the project source files. If any external sources are available
in an active repository, those should be included within as git submodules.

#### ./src/itaxotools

Even though most of our tools are available as standalone, there is a need
for them to work together: a launcher may need access to all tools,
while a tool might call another (eg. Concatenator might call MAFFTpy).
It is for this reason that it seems natural for all our tools
to exist in the same "*itaxotools*" namespace.

The sample `setup.py` configuration only installs packages inside
this namespace.

##### ./src/itaxotools/sample

For most existing tools, the source code would go here. This lies under the
*itaxotools* namespace, so importing from Python uses `import itaxotools.sample`
instead of just `import sample`.

A project may include more than one package. A package may contain subpackages,
eg. itaxotools.sample.gui.

##### ./src/itaxotools/common

Sometimes more than one tool may use the same resources, be it data files
(icons or logos) or python modules (utility scripts and classes).
Those should be made available here.

In the future it would be better to split this into its own repository.
However, it is very practical to include everything with the project
until we agree to adopt the same model for all tools.

##### ./src/itaxotools/__pyinstaller

Includes the project hooks for PyInstaller. Each project can add
its own hooks to this folder and PyInstaller will automatically
find and use them during deployment.

#### ./src/my_extension

Python extensions and other dependencies that are used for building
but are do not directly interface with other tools should go outside
the *itaxotools* namespace. This is especially useful and clear when
using external libraries (eg. ABGD, pthread-win32). If using unmodified
repositories available on GitHub, they should be added as git submodules.


### Other folders and files

These will *not* be included in the distribution/installation:

#### ./scripts

The script and spec file for PyInstaller go here.
Can also contain other useful scripts, eg. linux bash scripts.

#### ./docs

Documentation files, best available in markdown format for GitHub integration.
For example, [this is a relative link to docs/help.md](docs/help.md)

#### ./examples

Example input files and other use cases.

#### ./tests

If the project uses automatic testing, tests go here.

#### ./requirements.txt

Sometimes it is useful to freeze a Python environment that is known to work,
so that other users/developers can replicate it. There are tools such as
pipenv and poetry that help with this and each has its own ideas about
how to store this information. However, requirements.txt is recognised
by all and is sufficient for now.

When depending on other locally installed projects, `pip freeze`
won't record their versions properly. Please use
`pip list --format=freeze > requirements.txt` instead

----

## Entry Points

You may add shortcuts to your module functions when the module is installed.
Define your functions either within a package's `__init__.py` or as its own module.
Then configure `setup.py` accordingly.

A special entry point exists for PyInstaller, allowing for automatic hooks.

----

## Final Thoughts

As you can see, this adds some extra complexity to the projects structure.
However, it alleviates the complexity of combinational projects
(such as a launcher) by using *divide and conquer*.


Various tools exist that aid in development, such as flake8, mypy and pytest.
That said, I don't think enforcing their use for all projects is appropriate.

As we move away from the current "modular" model, where each tool is standalone,
and towards the creation of a larger menu-driven tool, I'm sure we will have
to come back to this subject. But until then, this will already be a great step
in the unison of all of our tools.


[pypa]: https://www.pypa.io/en/latest/
[src]: https://github.com/pypa/sampleproject
[packaging]: https://packaging.python.org
[distribution]: https://packaging.python.org/tutorials/packaging-projects/
[dependencies]: https://docs.python.org/3/distutils/setupscript.html#relationships-between-distributions-and-packages

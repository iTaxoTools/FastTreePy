"""The setup module for FastTreePy"""

# Always prefer setuptools over distutils
from setuptools import setup, Command, Extension, find_namespace_packages
from setuptools.command.build_ext import build_ext as _build_ext
import pathlib


class build_ext(_build_ext):
    """Overrides setuptools build_ext to execute build_init commands"""
    def build_extensions(self):
        for ext in self.extensions:
            if hasattr(ext, 'build_init'):
                ext.build_init(self)
        _build_ext.build_extensions(self)


class FastTreeExtension(Extension):
    """Extension subclass that defines build_init"""
    def build_init(self, build):
        """Called by build_ext to link openmp"""
        if build.compiler.compiler_type == 'msvc':
            self.extra_compile_args += ['/openmp']
        else:
            self.extra_compile_args += [
                '-fopenmp', '-finline-functions', '-funroll-loops']
            self.libraries += ['m', 'gomp']


# * gcc -Wall -O3 -finline-functions -funroll-loops -o FastTree -lm FastTree.c
fasttree_source = 'src/fasttree'
fasttree_module = FastTreeExtension(
    'itaxotools.fasttreepy.fasttree',
    include_dirs=[fasttree_source],
    define_macros=[
        ('ismodule', '1'),
        ('USE_DOUBLE', '1'),
        ('USE_OPENMP', '1'),
        # ('USE_SSE3', '1'),
        ],
    extra_compile_args=[],
    library_dirs=[],
    libraries=[],
    sources=[
        fasttree_source + '/FastTreeModule.c',
        fasttree_source + '/FastTree.c',
        fasttree_source + '/wrapio.c',
        ],
    )

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name='fasttreepy',
    version='0.2.0',
    description='A Python wrapper for FastTree',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Patmanidis Stefanos',
    author_email='stefanpatman91@gmail.com',
    package_dir={'': 'src'},
    packages=find_namespace_packages(
        include=('itaxotools*',),
        where='src',
    ),
    ext_modules=[fasttree_module],
    python_requires='>=3.8.6, <4',
    install_requires=[
        'pyside6>=6.1.1',
        'itaxotools-common==0.2.2',
        ],
    extras_require={
        'dev': ['pyinstaller>=4.5.1'],
    },
    entry_points={
        'console_scripts': [
            'fasttreepy = itaxotools.fasttreepy:main',
            'fasttreepy-gui = itaxotools.fasttreepy.gui:main',
        ],
    },
    cmdclass = {
        'build_ext': build_ext,
    },
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
    ],
    include_package_data=True,
)

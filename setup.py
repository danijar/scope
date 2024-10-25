import os
import pathlib
import re
import subprocess

import setuptools
from distutils.command.sdist import sdist as _sdist
from setuptools.command.develop import develop as _develop


def parse_requirements(filename):
  requirements = pathlib.Path(filename)
  requirements = requirements.read_text().split('\n')
  requirements = [x for x in requirements if x.strip()]
  return requirements


def parse_version(filename):
  text = (pathlib.Path(__file__).parent / filename).read_text()
  version = re.search(r"__version__ = '(.*)'", text).group(1)
  return version


def build_viewer():
  orig = os.getcwd()
  try:
    os.chdir(pathlib.Path(__file__).parent / 'viewer')
    subprocess.check_call(['npm', 'install'])
    subprocess.check_call(['npm', 'run', 'build'])
  finally:
    os.chdir(orig)


def patch(cmd):
  class Patched(cmd):
    def run(self):
      build_viewer()
      cmd.run(self)
  return Patched


setuptools.setup(
    name='scope',
    version=parse_version('scope/__init__.py'),
    description='Metrics logging and analysis',
    url='http://github.com/danijar/scope',
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    install_requires=parse_requirements('requirements.txt'),
    packages=['scope', 'scope.viewer'],
    package_dir={
      'scope': 'scope',
      'scope.viewer': 'viewer',
    },
    package_data={
        'scope.viewer': ['dist/*'],
    },
    include_package_data=True,
    cmdclass={
        'sdist': patch(_sdist),
        'develop': patch(_develop),
    },
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)

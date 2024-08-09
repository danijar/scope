import pathlib
import re
import setuptools


def parse_requirements(filename):
  requirements = pathlib.Path(filename)
  requirements = requirements.read_text().split('\n')
  requirements = [x for x in requirements if x.strip()]
  return requirements


def parse_version(filename):
  text = (pathlib.Path(__file__).parent / filename).read_text()
  version = re.search(r"__version__ = '(.*)'", text).group(1)
  return version


setuptools.setup(
    name='scope',
    version=parse_version('scope/__init__.py'),
    description='Metrics logging and analysis.',
    url='http://github.com/danijar/scope',
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    packages=['scope'],
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)

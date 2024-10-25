import re
import pathlib

from . import formats


FORMATS = [
    formats.Text(),
    formats.Float(),
    formats.Image(),
    formats.Video(),
]


class Reader:

  def __init__(self, logdir, formats=None):
    formats = formats or FORMATS
    if isinstance(logdir, str):
      logdir = pathlib.Path(logdir)
    self.logdir = logdir / 'scope'
    self.fmts = {x.extension: x for x in formats}
    self.cols = {}
    for child in sorted(logdir.glob('*')):
      basename, ext = child.name.rsplit('.', 1)
      key = basename.replace('-', '/')
      assert re.match(r'[a-z0-9_]+(/[a-z0-9_]+)?', key), key
      self.cols[key] = (child.name, self.fmts[ext])

  def keys(self):
    return tuple(self.cols.keys())

  def __getitem__(self, key):
    name, fmt = self.cols[key]
    return fmt.read(self.logdir / name)

  def length(self, key):
    name, fmt = self.cols[key]
    return fmt.length(self.logdir / name)

  def load(self, key, filename):
    _, fmt = self.cols[key]
    buffer = (self.logdir / filename).read_bytes()
    value = fmt.decode(buffer)
    return value

import re
import pathlib

import numpy as np

from . import columns


class Reader:

  def __init__(self, logdir):
    if isinstance(logdir, str):
      logdir = pathlib.Path(logdir)
    self.coltypes = {
        'float': columns.FloatColumn,
        'png': columns.ImageColumn,
        'mp4': columns.VideoColumn,
    }
    self.columns = {}
    for child in sorted(logdir.glob('*')):
      name, ext = child.name.rsplit('.', 1)
      key = name.replace('-', '/')
      assert re.match(r'[a-z0-9_]+(/[a-z0-9_]+)?', key), key
      self.columns[key] = self.coltypes[ext](logdir, key)

  def keys(self):
    return tuple(self.columns.keys())

  def length(self, key):
    return self.columns[key].length()

  def __getitem__(self, index):
    if isinstance(index, str):
      key, start, stop = index, -np.inf, +np.inf
    else:
      key, pos = index
      if isinstance(pos, int):
        start, stop = pos, pos + 1
      else:
        assert pos.step is None
        start = -np.inf if pos.start is None else pos.start
        stop = +np.inf if pos.stop is None else pos.stop
    return self.columns[key].read(start, stop)

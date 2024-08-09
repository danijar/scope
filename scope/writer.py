import concurrent.futures
import pathlib
import re
from functools import partial as bind

import numpy as np

from . import columns


class Writer:

  def __init__(self, logdir, fps=20, workers=32):
    if isinstance(logdir, str):
      logdir = pathlib.Path(logdir)
    self.logdir = logdir
    self.logdir.mkdir(parents=True, exist_ok=True)
    self.fps = fps
    self.workers = workers
    self.coltypes = [
        (lambda x: isinstance(x, str), columns.TextColumn),
        (lambda x: x.ndim == 0, columns.FloatColumn),
        (lambda x: x.ndim == 3, bind(columns.ImageColumn, fmt='png')),
        (lambda x: x.ndim == 4, bind(columns.VideoColumn, fmt='mp4', fps=fps)),
    ]
    self.columns = {}
    self.values = {}
    if workers:
      self.pool = concurrent.futures.ThreadPoolExecutor(workers, 'writer')
      self.futures = []

  def add(self, step, *args, **kwargs):
    step = int(step)
    mapping = dict(*args, **kwargs)
    for key, value in mapping.items():
      value = value if isinstance(value, str) else np.asarray(value)
      if key not in self.columns:
        assert re.match(r'[a-z0-9_]+(/[a-z0-9_]+)?', key), key
        for applies, coltype in self.coltypes:
          if applies(value):
            break
        else:
          raise NotImplementedError((
              key, value,
              getattr(value, 'shape', None),
              getattr(value, 'dtype', None)))
        self.columns[key] = coltype(self.logdir, key)
        self.values[key] = []
      column = self.columns[key]
      try:
        value = column.validate(value)
      except Exception:
        print(f"Error validating key '{key}' with value '{value}'.")
        raise
      self.values[key].append((step, value))

  def flush(self):
    keys = [key for key, values in self.values.items() if values]
    if self.workers:
      list(self.futures)
      columns = [self.columns[x] for x in keys]
      values = [self.values[x] for x in keys]
      self.futures = self.pool.map(lambda x, y: x.write(y), columns, values)
    else:
      for key in keys:
        try:
          self.columns[key].write(self.values[key])
        except Exception:
          print(f"Exception writing '{key}' column.")
          raise
    self.values = {key: [] for key in self.values.keys()}

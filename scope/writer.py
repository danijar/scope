import concurrent.futures
import dataclasses
import pathlib
import re

import numpy as np

from . import formats

FPS = 10

FORMATS = [
    formats.Text(),
    formats.Float(),
    formats.Image(),
    formats.Video(fps=FPS),
]


@dataclasses.dataclass
class Column:

  fmt: str
  name: str
  created: bool
  steps: list
  values: list


class Writer:

  def __init__(self, logdir, workers=8, formats=None):
    formats = formats or FORMATS
    if isinstance(logdir, str):
      logdir = pathlib.Path(logdir)
    self.logdir = logdir / 'scope'
    self.logdir.mkdir(parents=True, exist_ok=True)
    self.workers = workers
    self.rng = np.random.default_rng(seed=None)
    self.fmts = FORMATS
    self.cols = {}
    if workers:
      self.pool = concurrent.futures.ThreadPoolExecutor(workers, 'scope')
      self.futures = []

  def add(self, step, *args, **kwargs):
    assert isinstance(step, (int, np.integer)), type(step)
    step = int(step)
    mapping = dict(*args, **kwargs)
    for key, value in mapping.items():
      if not isinstance(value, str):
        value = np.asarray(value)
      if key not in self.cols:
        assert re.match(r'[a-z0-9_]+(/[a-z0-9_]+)?', key), key
        for fmt in self.fmts:
          if fmt.valid(value):
            break
        else:
          raise NotImplementedError(
              f"No format supports key '{key}' with {self._info(value)}")
        name = key.replace('/', '-') + '.' + fmt.extension
        self.cols[key] = Column(fmt, name, False, [], [])
      col = self.cols[key]
      if not col.fmt.valid(value):
        raise ValueError(
            f"Key '{key}' contains invalid value {self._info(value)}")
      col.steps.append(step)
      col.values.append(value)

  def flush(self):
    if self.workers:
      list(self.futures)
      jobs = [(c, c.steps, c.values) for c in self.cols.values() if c.steps]
      self.futures = self.pool.map(self._write, *zip(*jobs))
    else:
      for col in self.cols.values():
        if col.steps:
          self._write(col, col.steps, col.values)
    for col in self.cols.values():
      col.steps = []
      col.values = []

  def _write(self, col, steps, values):
    try:
      path = self.logdir / col.name
      if not col.created:
        col.fmt.create(path)
        col.created = True
      col.fmt.write(path, steps, values)
    except Exception:
      print(f"Exception writing '{col.name}' column")
      raise

  def _info(self, value):
    if hasattr(value, 'dtype') and hasattr(value, 'shape'):
      return f"dtype '{value.dtype}' and shape '{value.shape}'"
    return f"type '{type(value)}'"

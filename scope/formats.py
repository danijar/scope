import io
import struct
import time

import numpy as np
import PIL.Image


class Float:

  @property
  def extension(self):
    return 'float'

  def valid(self, x):
    return x.ndim == 0 and np.isreal(x)

  def create(self, path):
    pass

  def write(self, path, steps, values):
    table_append(path, '>qd', steps, values)

  def read(self, path):
    steps, values = table_read(path, '>qd')
    steps = np.int64(steps)
    values = np.float64(values)
    return steps, values

  def length(self, path):
    return table_length(path, '>qd')


class Text:

  @property
  def extension(self):
    return 'txt'

  def valid(self, x):
    return isinstance(x, str)

  def create(self, path):
    path.mkdir(exist_ok=True)

  def write(self, path, steps, values):
    files_write(path, steps, values, self.encode)

  def read(self, path):
    return files_read(path)

  def encode(self, value):
    return value.encode('utf-8')

  def decode(self, buffer):
    return buffer.deceode('utf-8')

  def length(self, path):
    return files_length(path)


class Image:

  def __init__(self, ext='png', quality=90):
    self.ext = ext
    self.quality = quality

  @property
  def extension(self):
    return self.ext

  def valid(self, x):
    return (
        x.dtype == np.uint8 and
        x.ndim == 3 and
        x.shape[-1] in (1, 3))

  def create(self, path):
    path.mkdir(exist_ok=True)

  def write(self, path, steps, values):
    files_write(path, steps, values, self.encode)

  def read(self, path):
    return files_read(path)

  def encode(self, value):
    if value.shape[-1] == 1:
      value = value.repeat(3, -1)
    fmt = ('jpeg' if self.ext == 'jpg' else self.ext).upper()
    fp = io.BytesIO()
    PIL.Image.fromarray(value).save(fp, fmt, quality=self.quality)
    return fp.getvalue()

  def decode(self, buffer):
    return np.asarray(PIL.Image.open(io.BytesIO(buffer)).convert('RGB'))

  def length(self, path):
    return files_length(path)


class Video:

  def __init__(self, ext='mp4', codec='h264', fps=10):
    self.ext = ext
    self.codec = codec
    self.fps = fps

  @property
  def extension(self):
    return self.ext

  def valid(self, x):
    return (
        x.dtype == np.uint8 and
        x.ndim == 4 and
        x.shape[-1] in (1, 3))

  def create(self, path):
    path.mkdir(exist_ok=True)

  def write(self, path, steps, values):
    files_write(path, steps, values, self.encode)

  def read(self, path):
    return files_read(path)

  def encode(self, value):
    import av
    if value.shape[-1] == 1:
      value = value.repeat(3, -1)
    T, H, W, _ = value.shape
    fp = io.BytesIO()
    output = av.open(fp, mode='w', format=self.ext)
    stream = output.add_stream(self.codec, rate=self.fps)
    stream.width = W
    stream.height = H
    stream.pix_fmt = 'yuv420p'
    for t in range(T):
      frame = av.VideoFrame.from_ndarray(value[t], format='rgb24')
      frame.pts = t
      output.mux(stream.encode(frame))
    output.mux(stream.encode(None))
    output.close()
    return fp.getvalue()

  def decode(self, buffer):
    import av
    container = av.open(io.BytesIO(buffer))
    value = []
    for frame in container.decode(video=0):
      value.append(frame.to_ndarray(format='rgb24'))
    value = np.stack(value)
    container.close()
    return value

  def length(self, path):
    return files_length(path)


def table_append(filename, fmt, *cols):
  rows = tuple(zip(*cols))
  size = struct.calcsize(fmt)
  buffer = bytearray(len(rows) * size)
  for index, row in enumerate(rows):
    struct.pack_into(fmt, buffer, index * size, *row)
  with filename.open('ab') as f:
    f.write(buffer)


def table_read(filename, fmt, start=0, stop=None):
  assert stop is None or start < stop, (start, stop)
  if start == 0 and stop is None:
    buffer = filename.read_bytes()
  else:
    size = struct.calcsize(fmt)
    with filename.open('rb') as f:
      start and f.seek(start * size)
      buffer = f.read((stop - start) * size if stop else None)
  rows = struct.iter_unpack(fmt, buffer)
  cols = tuple(zip(*rows))
  return cols


def table_length(filename, fmt):
  return filename.stat().st_size // struct.calcsize(fmt)


def files_write(path, steps, values, encode):
  rng = np.random.default_rng(seed=None)
  prefix = int(time.time()).to_bytes(4, 'big')
  idents = [prefix + rng.bytes(4) for _ in range(len(steps))]
  for ident, step, value in zip(idents, steps, values):
    filename = f'{step:020}-{ident.hex()}{path.suffix}'
    buffer = encode(value)
    with (path / filename).open('wb') as f:
      f.write(buffer)
  table_append(path / 'index', 'q8s', steps, idents)


def files_read(path):
  steps, idents = table_read(path / 'index', 'q8s')
  filenames = [
      path / f'{step:020}-{ident.hex()}{path.suffix}'
      for step, ident in zip(steps, idents)]
  steps = np.int64(steps)
  return steps, filenames


def files_length(path):
  return table_length(path / 'index', 'q8s')

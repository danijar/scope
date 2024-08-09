import io
import struct
import time

import av
import numpy as np
from PIL import Image


def table_length(filename, fmt):
  return filename.stat().st_size // struct.calcsize(fmt)


def table_write(filename, fmt, *cols):
  rows = tuple(zip(*cols))
  size = struct.calcsize(fmt)
  buffer = bytearray(len(rows) * size)
  for index, row in enumerate(rows):
    struct.pack_into(fmt, buffer, index * size, *row)
  with filename.open('ab') as f:
    f.write(buffer)


def table_read(filename, fmt, start=0, stop=None):
  assert stop is None or start < stop, (start, stop)
  size = struct.calcsize(fmt)
  with filename.open('rb') as f:
    start and f.seek(start * size)
    buffer = f.read((stop - start) * size if stop else None)
  rows = struct.iter_unpack(fmt, buffer)
  cols = tuple(zip(*rows))
  return cols


class FloatColumn:

  def __init__(self, logdir, key):
    name = key.replace('/', '-') + '.float'
    self.filename = logdir / name

  def validate(self, value):
    assert value.dtype in (float, int) and value.ndim == 0, (
        value.dtype, value.shape)
    return value

  def write(self, values):
    steps, values = zip(*values)
    table_write(self.filename, '>qd', steps, values)

  def length(self):
    return table_length(self.filename, '>qd')

  def read(self, start, stop):
    steps, values = table_read(self.filename, '>qd')
    filtered = [(s, v) for s, v in zip(steps, values) if start <= s < stop]
    steps, values = zip(*filtered) if filtered else ([], [])
    steps = np.array(steps, np.int64)
    values = np.array(values, np.float64)
    return steps, values


class FileColumn:

  def __init__(self, logdir, key, ext, encfn, decfn):
    name = key.replace('/', '-') + '.' + ext
    self.folder = logdir / name
    self.folder.mkdir(exist_ok=True)
    self.index = self.folder / 'index'
    self.rng = np.random.default_rng(seed=None)
    self.ext = ext
    self.encfn = encfn
    self.decfn = decfn

  def validate(self, value):
    raise NotImplementedError

  def write(self, values):
    prefix = int(time.time()).to_bytes(4, 'big')
    steps, values = zip(*values)
    idents = [prefix + self.rng.bytes(4) for _ in range(len(steps))]
    for ident, step, value in zip(idents, steps, values):
      buffer = self.encfn(value)
      with self._filename(step, ident).open('wb') as f:
        f.write(buffer)
    table_write(self.index, 'q8s', steps, idents)

  def length(self):
    return table_length(self.index, 'q8s')

  def read(self, start, stop):
    steps, idents = table_read(self.index, 'q8s')
    filtered = [(s, v) for s, v in zip(steps, idents) if start <= s < stop]
    steps, idents = zip(*filtered) if filtered else ([], [])
    values = []
    for step, ident in zip(steps, idents):
      with self._filename(step, ident).open('rb') as f:
        buffer = f.read()
      values.append(self.decfn(buffer))
    steps = np.array(steps, np.int64)
    values = tuple(values)
    return steps, values

  def _filename(self, step, ident):
    return self.folder / f'{step:020}-{ident.hex()}.{self.ext}'


class TextColumn(FileColumn):

  def __init__(self, logdir, key, fmt='txt'):
    super().__init__(logdir, key, fmt, self.encode, self.decode)
    self.fmt = fmt

  def validate(self, value):
    assert isinstance(value, str), type(value)
    return value

  def encode(self, value):
    return value.encode('utf-8')

  def decode(self, buffer):
    return buffer.decode('utf-8')


class ImageColumn(FileColumn):

  def __init__(self, logdir, key, fmt='png', quality=None):
    super().__init__(logdir, key, fmt, self.encode, self.decode)
    self.fmt = fmt
    self.quality = quality

  def validate(self, value):
    assert (
        value.dtype == np.uint8 and value.ndim == 3 and
        value.shape[-1] == 3), (value.dtype, value.shape)
    return value

  def encode(self, value):
    fmt = ('jpeg' if self.fmt == 'jpg' else self.fmt).upper()
    fp = io.BytesIO()
    Image.fromarray(value).save(fp, format=fmt, quality=self.quality)
    return fp.getvalue()

  def decode(self, buffer):
    return np.asarray(Image.open(io.BytesIO(buffer)).convert('RGB'))


class VideoColumn(FileColumn):

  def __init__(self, logdir, key, fmt='mp4', fps=20, codec='h264'):
    super().__init__(logdir, key, fmt, self.encode, self.decode)
    self.fmt = fmt
    self.fps = fps
    self.codec = codec

  def validate(self, value):
    assert (
        value.dtype == np.uint8 and value.ndim == 4 and
        value.shape[-1] == 3), (value.dtype, value.shape)
    return value

  def encode(self, array):
    T, H, W, C = array.shape
    fp = io.BytesIO()
    output = av.open(fp, mode='w', format=self.fmt)
    stream = output.add_stream(self.codec, rate=float(self.fps))
    stream.width = W
    stream.height = H
    stream.pix_fmt = 'yuv420p'
    for t in range(T):
      frame = av.VideoFrame.from_ndarray(array[t], format='rgb24')
      frame.pts = t
      output.mux(stream.encode(frame))
    output.mux(stream.encode(None))
    output.close()
    return fp.getvalue()

  def decode(self, buffer):
    container = av.open(io.BytesIO(buffer))
    array = []
    for frame in container.decode(video=0):
      array.append(frame.to_ndarray(format='rgb24'))
    array = np.stack(array)
    container.close()
    return array

import elements
import io
import os
import subprocess


class Local:

  def list(self, path):
    return os.listdir(path)

  def size(self, path):
    return os.path.getsize(path)

  def read(self, path):
    with open(path, 'rb') as f:
      return f.read()

  def open(self, path, seek=0, limit=None):
    f = open(path, 'rb')
    f.seek(seek)
    return f


class Elements:

  def list(self, path):
    paths = elements.Path(path).glob('*')
    return [str(x) for x in paths]

  def size(self, path):
    return elements.Path(path).size

  def read(self, path):
    return elements.Path(path).read_bytes()

  def open(self, path, seek=0, limit=None):
    f = elements.Path(path).open('rb')
    f.seek(seek)
    return f


class Fileutil:

  def __init__(
      self,
      ls='fileutil ls {}',
      cat='fileutil cat {}',
      size="fileutil ls -l {} | tr -s ' ' | cut -d' ' -f5",
      catrange='fileutil cat -input_startpos={} -input_endpos={} {}',
  ):
    self._ls = ls
    self._cat = cat
    self._size = size
    self._catrange = catrange

  def list(self, path):
    try:
      output = self._sh(self._ls.format(path))
      return [x.rstrip('/') for x in output.decode('utf-8').splitlines()]
    except RuntimeError as e:
      print(e)
      return []

  def size(self, path):
    output = self._sh(self._size.format(path))
    return int(output.decode('utf-8').strip('\n'))

  def read(self, path):
    return self._sh(self._cat.format(path))

  def open(self, path, seek=0, limit=None):
    limit = limit or self._size(path)
    buffer = self._sh(self._catrange.format(seek, limit, path))
    return io.BytesIO(buffer)

  def _sh(self, cmd):
    if '|' in cmd:
      process = subprocess.Popen(
          cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      out, err = process.communicate()
      if process.returncode:
        raise RuntimeError((process.returncode, out, err))
      return out
    else:
      try:
        return subprocess.check_output(cmd.split(), shell=False)
      except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Error in subprocess: {e}')

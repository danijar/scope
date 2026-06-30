import io
import os
import pathlib
import subprocess

import elements
import filelock


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
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            out, err = process.communicate()
            if process.returncode:
                raise RuntimeError((process.returncode, out, err))
            return out
        else:
            try:
                return subprocess.check_output(cmd.split(), shell=False)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f'Error in subprocess: {e}')


class WithFileCache:
    def __init__(self, fs, cachedir, maxsize):
        # Cache size can be exceeded if multiple workers download in parallel.
        assert not isinstance(fs, Local)
        if isinstance(cachedir, str):
            cachedir = pathlib.Path(cachedir)
        cachedir.mkdir(exist_ok=True, parents=True)
        self.fs = fs
        self.localfs = Local()
        self.cachedir = cachedir
        self.maxsize = maxsize
        self.lock = filelock.FileLock(cachedir / '.lock')

    def list(self, path):
        return self.fs.list(path)

    def size(self, path):
        localpath = self._getfile(path)
        return self.localfs.size(localpath)

    def read(self, path):
        localpath = self._getfile(path)
        return self.localfs.read(localpath)

    def open(self, path, seek=0, limit=None):
        localpath = self._getfile(path)
        return self.localfs.open(localpath, seek, limit)

    def _getfile(self, path):
        name = str(path).replace(':', '').replace('//', '/').replace('/', ':')
        localpath = self.cachedir / name
        if not localpath.exists():
            buffer = self.fs.read(path)
            self._freeup(len(buffer))
            localpath.write_bytes(buffer)
        return localpath

    def _freeup(self, needed):
        with self.lock:
            pairs = []
            for path in self.cachedir.glob('*'):
                if path.name == '.lock':
                    continue
                try:
                    stat = path.stat()
                    pairs.append((path, stat))
                except FileNotFoundError:
                    pass
            pairs = sorted(pairs, key=lambda x: x[1].st_ctime)
            total = sum(s.st_size for _, s in pairs)
            while total + needed > self.maxsize and pairs:
                path, stat = pairs.pop(0)
                path.unlink()
                total -= stat.st_size

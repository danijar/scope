import io
import os
import struct
import subprocess

import elements
import fastapi
import fastapi.responses
import uvicorn

args = elements.Flags(
    root=os.environ.get('SCOPE_ROOT', ''),
    ls=os.environ.get('SCOPE_LS', ''),
    cat=os.environ.get('SCOPE_CAT', ''),
    port=6008,
).parse()
print(args)
root = args.root.rstrip('/')
assert root, root

app = fastapi.FastAPI(debug=True)


class FileSystem:

  def list(self, path):
    path = path.rstrip('/')
    if args.ls:
      try:
        output = subprocess.check_output([*args.ls.split(), path])
        names = [x.decode('utf-8').rstrip('/') for x in output.splitlines()]
      except subprocess.CalledProcessError:
        names = []
    else:
      names = [str(x).rstrip('/') for x in elements.Path(path).glob('*')]
    names = [x for x in names if x != path]
    return names

  def read(self, path):
    if args.cat:
      return subprocess.check_output([*args.cat.split(), str(path)])
    else:
      return elements.Path(path).read_bytes()

  def open(self, path):
    if args.cat:
      return io.BytesIO(self.read(path))
    else:
      return elements.Path(path).open('rb')

fs = FileSystem()


# @app.get('/', response_class=fastapi.responses.HTMLResponse)
# def index():
#   return '<h1>hello world</h1>'


@app.get('/exps')
def get_exps():
  print('GET /exps', flush=True)
  folders = fs.list(root)
  expids = [x.rsplit('/', 1)[-1] for x in folders]
  return {'exps': expids}


@app.get('/exp/{expid}')
def get_exp(expid: str):
  print(f'GET /exp/{expid}', flush=True)
  folders = find_runs(root + '/' + expid)
  folders = [x.removeprefix(str(root))[1:] for x in folders]
  runids = [x.replace('/', ':') for x in folders]
  return {'runs': runids}


@app.get('/run/{runid}')
def get_run(runid: str):
  print(f'GET /run/{runid}', flush=True)
  folder = root + '/' + runid.replace(':', '/') + '/scope'
  children = fs.list(folder)
  children = [x.removeprefix(str(root))[1:] for x in children]
  colids = [x.replace('/', ':') for x in children]
  return {'cols': colids}


@app.get('/col/{colid}')
def get_col(colid: str):
  print(f'GET /col/{colid}', flush=True)
  ext = colid.rsplit('.', 1)[-1]
  path = root + '/' + colid.replace(':', '/')
  if ext == 'float':
    buffer = fs.read(path)
    steps, values = tuple(zip(*struct.iter_unpack('>qd', buffer)))
    return {'steps': steps, 'values': values}
  elif ext in ('mp4', 'txt'):
    buffer = fs.read(path + '/index')
    steps, idents = tuple(zip(*struct.iter_unpack('q8s', buffer)))
    filenames = [f'{s:020}-{x.hex()}.{ext}' for s, x in zip(steps, idents)]
    values = [f'{colid}:{x}' for x in filenames]
    return {'steps': steps, 'values': values}
  else:
    raise NotImplementedError((colid, ext))


@app.get('/file/{fileid}')
def get_file(fileid: str):
  print(f'GET /file/{fileid}', flush=True)
  ext = fileid.rsplit('.', 1)[-1]
  assert ext in ('mp4', 'txt'), fileid
  path = root + '/' + fileid.replace(':', '/')

  if ext == 'mp4':
    fp = fs.open(path)
    fp.seek(0)
    total = fp.blob.size
    def iterfile():
      remaining = total
      while remaining > 0:
        chunk = fp.read(min(128 * 1024, remaining))
        remaining -= len(chunk)
        yield chunk
      fp.close()
    headers = {
        'Content-Disposition': f'attachment; filename={fileid}.mp4',
    }
    return fastapi.responses.StreamingResponse(
        iterfile(), media_type='video/mp4', headers=headers)

  if ext == 'txt':
    text = fs.read(path).decode('utf-8')
    return {'text': text}


def find_runs(folder):
  leafs = []
  queue = [folder]
  while queue:
    node = queue.pop(0)
    children = fs.list(node)
    if not children:
      pass
    elif any(x.endswith('/scope') for x in children):
      leafs.append(node)
    else:
      queue += children
  return leafs


if __name__ == '__main__':
  uvicorn.run('__main__:app', host='0.0.0.0', port=args.port, reload=True)

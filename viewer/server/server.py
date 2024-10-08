import concurrent.futures
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
    catrange=os.environ.get('SCOPE_CATRANGE', ''),
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
      buffer = self.read(path)
      return io.BytesIO(buffer), len(buffer)
    else:
      path = elements.Path(path)
      size = path.blob.size if hasattr(path, 'blob') else None
      return path.open('rb'), size

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
  return {'id': expid, 'runs': runids}


@app.get('/run/{runid}')
def get_run(runid: str):
  print(f'GET /run/{runid}', flush=True)
  folder = root + '/' + runid.replace(':', '/') + '/scope'
  children = fs.list(folder)
  children = [x.removeprefix(str(root))[1:] for x in children]
  colids = [x.replace('/', ':') for x in children]
  return {'id': runid, 'cols': colids}


@app.get('/col/{colid}')
def get_col(colid: str):
  print(f'GET /col/{colid}', flush=True)
  ext = colid.rsplit('.', 1)[-1]
  path = root + '/' + colid.replace(':', '/')
  runid = colid.rsplit(':', 2)[0]  # Remove metric name and scope folder.
  if ext == 'float':
    buffer = fs.read(path)
    steps, values = tuple(zip(*struct.iter_unpack('>qd', buffer)))
    return {'id': colid, 'run': runid, 'steps': steps, 'values': values}
  elif ext in ('txt', 'mp4', 'webm'):
    buffer = fs.read(path + '/index')
    steps, idents = tuple(zip(*struct.iter_unpack('q8s', buffer)))
    filenames = [f'{s:020}-{x.hex()}.{ext}' for s, x in zip(steps, idents)]
    values = [f'{colid}:{x}' for x in filenames]
    return {'id': colid, 'run': runid, 'steps': steps, 'values': values}
  else:
    raise NotImplementedError((colid, ext))


@app.get('/file/{fileid}')
def get_file(fileid: str):
  print(f'GET /file/{fileid}', flush=True)
  ext = fileid.rsplit('.', 1)[-1]
  path = root + '/' + fileid.replace(':', '/')

  if ext == 'txt':
    text = fs.read(path).decode('utf-8')
    return {'id': fileid, 'text': text}

  elif ext in ('mp4', 'webm'):
    fp, size = fs.open(path)
    fp.seek(0)
    def iterfile():
      if size:
        remaining = size
        while remaining > 0:
          chunk = fp.read(min(128 * 1024, remaining))
          remaining -= len(chunk)
          yield chunk
      else:
        while True:
          chunk = fp.read(128 * 1024)
          if not chunk:
            break
          yield chunk
      fp.close()
    headers = {
        'Content-Disposition': f'attachment; filename={fileid}.{ext}',
    }
    return fastapi.responses.StreamingResponse(
        iterfile(), media_type=f'video/{ext}', headers=headers)

  else:
    raise NotImplementedError((fileid, ext))



def find_runs(folder, workers=32):
  if not workers:
    leafs = []
    queue = [folder]
    while queue:
      node = queue.pop(0)
      children = fs.list(node)
      if any(x.endswith('/scope') for x in children):
        leafs.append(node)
      else:
        queue += children
    return leafs
  leafs = []
  with concurrent.futures.ThreadPoolExecutor(workers) as pool:
    future = pool.submit(fs.list, folder)
    future.parent = folder
    queue = [future]
    while queue:
      future = queue.pop(0)
      children = future.result()
      if any(x.endswith('/scope') for x in children):
        leafs.append(future.parent)
      else:
        for child in children:
          future = pool.submit(fs.list, child)
          future.parent = child
          queue.append(future)
  return leafs


if __name__ == '__main__':
  # uvicorn.run('__main__:app', host='0.0.0.0', port=args.port, reload=True)
  uvicorn.run('__main__:app', host='0.0.0.0', port=args.port, reload=False, workers=64)

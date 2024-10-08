import concurrent.futures
import functools
import os
import struct

import elements
import fastapi
import fastapi.responses
import uvicorn

import filesystems

args = elements.Flags(
    root=os.environ.get('SCOPE_ROOT', ''),
    fs=os.environ.get('SCOPE_FS', 'elements'),
    port=6008,
    maxdepth=2,
).parse()
print(args)
root = args.root.rstrip('/')
assert root, root

app = fastapi.FastAPI(debug=True)

fs = dict(
  elements=filesystems.Elements,
  fileutil=filesystems.Fileutil,
  local=filesystems.Local,
)[args.fs]()


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
def get_file(request: fastapi.Request, fileid: str):
  print(f'GET /file/{fileid}', flush=True)
  ext = fileid.rsplit('.', 1)[-1]
  path = root + '/' + fileid.replace(':', '/')
  if ext == 'txt':
    text = fs.read(path).decode('utf-8')
    return {'id': fileid, 'text': text}
  elif ext in ('mp4', 'webm'):
    filesize = fs.size(path)
    openfn = functools.partial(fs.open, path)
    content_type = f'video/{ext}'
    return RangeResponse(request, openfn, filesize, content_type)
  else:
    raise NotImplementedError((fileid, ext))


def find_runs(folder, maxdepth=args.maxdepth, workers=64):
  if not workers:
    runs = []
    queue = [(folder, 0)]
    while queue:
      node, depth = queue.pop(0)
      children = fs.list(node)
      if any(x.endswith('/scope') for x in children):
        runs.append(node)
      elif depth < maxdepth:
        queue += [(x, depth + 1) for x in children]
    return runs
  runs = []
  with concurrent.futures.ThreadPoolExecutor(workers) as pool:
    future = pool.submit(fs.list, folder)
    future.parent = folder
    future.depth = 0
    queue = [future]
    while queue:
      current = queue.pop(0)
      children = current.result()
      if any(x.endswith('/scope') for x in children):
        runs.append(current.parent)
      elif current.depth < maxdepth:
        for child in children:
          future = pool.submit(fs.list, child)
          future.parent = child
          future.depth = current.depth + 1
          queue.append(future)
  return runs


def RangeResponse(request, openfn, filesize, content_type):
  headers = {
      'content-type': content_type,
      'accept-ranges': 'bytes',
      'content-length': str(filesize),
      'access-control-expose-headers': (
          'content-type, accept-ranges, content-length, '
          'content-range, content-encoding'
      ),
  }
  range_header = request.headers.get('range')
  if range_header:
    try:
      h = range_header.replace('bytes=', '').split('-')
      start = int(h[0]) if h[0] != '' else 0
      end = int(h[1]) if h[1] != '' else filesize - 1
    except ValueError:
      raise fastapi.HTTPException(
        fastapi.status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
        detail=f'Invalid request range (Range:{range_header!r})')
    if start > end or start < 0 or end > filesize - 1:
      raise fastapi.HTTPException(
        fastapi.status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
        detail=f'Invalid request range (Range:{range_header!r})')
    size = end - start + 1
    headers['content-length'] = str(size)
    headers['content-range'] = f'bytes {start}-{end}/{filesize}'
    status_code = fastapi.status.HTTP_206_PARTIAL_CONTENT
  else:
    start = 0
    end = filesize - 1
    status_code = fastapi.status.HTTP_200_OK
  stop = end + 1
  def iterfile(chunksize=int(2e5)):
    with openfn(start, stop) as f:
      total = stop - start
      nbytes = 0
      while nbytes < total:
        chunk = f.read(min(chunksize, total - nbytes))
        nbytes += len(chunk)
        yield chunk
  return fastapi.responses.StreamingResponse(
    iterfile(), headers=headers, status_code=status_code)


if __name__ == '__main__':
  # uvicorn.run('__main__:app', host='0.0.0.0', port=args.port, reload=True)
  uvicorn.run(
      '__main__:app', host='0.0.0.0', port=args.port,
      reload=False, workers=64)

import pathlib
import subprocess
import sys

import elements
import fastapi
import fastapi.responses
import uvicorn

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
import scope


args = elements.Flags(
    root='gs://dm-gdm-worldmodel-team-us-ut-da6189d76684/logdir',
).parse()

assert args.root, args.root
root = elements.Path(args.root)

app = fastapi.FastAPI(debug=True)


# @app.get('/', response_class=fastapi.responses.HTMLResponse)
# def index():
#   return '<h1>hello world</h1>'


@app.get('/exps')
def get_exps():
  folders = ls(root, folders=True, files=False)
  expids = [x[:-1].rsplit('/', 1)[-1] for x in folders]
  return {'exps': expids}


@app.get('/exp/{expid}')
def get_exp(expid: str):
  folders = find_runs(root / expid)
  folders = [x.removeprefix(str(root)).strip('/') for x in folders]
  runids = [x.replace('/', ':') for x in folders]
  return {'runs': runids}


@app.get('/run/{runid}')
def get_run(runid: str):
  folder = str(root / runid.replace(':', '/') / 'scope')
  children = ls(folder)
  children = [x for x in children if x.strip('/') != folder]
  children = [x.removeprefix(str(root)).strip('/') for x in children]
  colids = [x.replace('/', ':') for x in children]
  return {'cols': colids}


@app.get('/col/{colid}')
def get_col(colid: str):
  ext = colid.rsplit('.', 1)[-1]
  path = root / colid.replace(':', '/')
  if ext == 'float':
    steps, values = scope.table_read(path, '>qd')
    return {'steps': steps, 'values': values}
  elif ext == 'mp4':
    steps, idents = scope.table_read(path / 'index', 'q8s')
    filenames = [f'{s:020}-{x.hex()}.{ext}' for s, x in zip(steps, idents)]
    values = [f'{colid}:{x}' for x in filenames]
    return {'steps': steps, 'values': values}
  else:
    raise NotImplementedError((colid, ext))


@app.get('/file/{fileid}')
def get_file(fileid: str):
  assert fileid.endswith('.mp4'), fileid
  path = root / fileid.replace(':', '/')
  fp = path.open('rb')
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


def find_runs(folder):
  leafs = []
  queue = [folder]
  while queue:
    node = queue.pop(0)
    children = ls(node, folders=True, files=False)
    if not children:
      pass
    elif any(x.endswith('/scope/') for x in children):
      leafs.append(node.strip('/'))
    else:
      queue += children
  return leafs


def ls(folder, folders=True, files=True):
  try:
    output = subprocess.check_output(['gsutil', 'ls', str(folder)])
  except subprocess.CalledProcessError:
    output = ''
  lines = [x.decode('utf-8') for x in output.splitlines()]
  results = []
  if folders:
    results += [line for line in lines if line.endswith('/')]
  if files:
    results += [line for line in lines if not line.endswith('/')]
  return results


if __name__ == '__main__':

  # import rich.traceback
  # rich.traceback.install()
  # x = 'e4ffb7_20240918T233314_us_vpt_shmap:23f6d8-dummy-arflow_shmap-1:scope:eval-openloop-video.mp4'
  # # x = 'e4ffb7_20240918T233314_us_vpt_shmap:23f6d8-dummy-arflow_shmap-1:scope:report-loss-dyn.float'
  # x = get_col(x)
  # print(x)

  uvicorn.run('__main__:app', host='0.0.0.0', port=6008, reload=True)

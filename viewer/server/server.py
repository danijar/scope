import urllib
import subprocess

import uvicorn
import elements
import fastapi


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
  exps = [x[:-1].rsplit('/', 1)[-1] for x in folders]
  return {'exps': exps}


@app.get('/leafs/{exp}')
def get_leafs(exp: str):
  leafs = find_leafs(root / exp)
  prefix = str(root)
  leafs = [x.removeprefix(prefix).strip('/') for x in leafs]
  return {'leafs': leafs}


@app.get('/keys/{leaf}')
def get_keys(leaf: str):
  leaf = leaf.replace(':', '/') + '/scope'
  keys = ls(root / leaf)
  prefix = str(root / leaf) + '/'
  keys = [x.removeprefix(prefix).strip('/') for x in keys]
  return {'keys': keys}


def find_leafs(folder):
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
  uvicorn.run('__main__:app', host='0.0.0.0', port=6008, reload=True)

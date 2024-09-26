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


@app.get('/exp/{exp}')
def get_exp(exp: str):
  folders = ls(root / exp, folders=True, files=False)
  runs = [x[:-1].rsplit('/', 1)[-1] for x in folders]
  return {'exp': exp, 'runs': runs}


def ls(folder, folders=True, files=True):
  output = subprocess.check_output(['gsutil', 'ls', str(folder)])
  lines = [x.decode('utf-8') for x in output.splitlines()]
  results = []
  if folders:
    results += [line for line in lines if line.endswith('/')]
  if files:
    results += [line for line in lines if not line.endswith('/')]
  return results


if __name__ == '__main__':
  uvicorn.run('__main__:app', host='0.0.0.0', port=6008, reload=True)

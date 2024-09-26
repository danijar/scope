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
  output = subprocess.check_output(['gsutil', 'ls', args.root])
  lines = [x.decode('utf-8') for x in output.splitlines()]
  folders = [x[:-1] for x in lines if x.endswith('/')]
  expnames = [x.rsplit('/', 1)[-1] for x in folders]
  return {'exps': expnames}


if __name__ == '__main__':
  uvicorn.run('__main__:app', host='0.0.0.0', port=6008, reload=True)

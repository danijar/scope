import os
import pathlib
import sys

import elements
import uvicorn


args, sys.argv[1:] = elements.Flags(
    port=int(os.environ.get('SCOPE_SERVER_PORT', 8000)),
    workers=32,
    debug=False,
).parse_known()

sys.argv.append(f'--debug={args.debug}')
sys.path.insert(0, str(pathlib.Path(__file__).parent))

uvicorn.run(
    'server:app',
    host='0.0.0.0',
    port=args.port,
    reload=args.debug,
    workers=None if args.debug else args.workers,
)

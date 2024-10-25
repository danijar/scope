import pathlib
import sys

import uvicorn
from . import config


config = config.config

print(config)

sys.path.insert(0, str(pathlib.Path(__file__).parent))

uvicorn.run(
    'server:app',
    host='0.0.0.0',
    port=config.port,
    reload=config.debug,
    workers=None if config.debug else config.workers,
)

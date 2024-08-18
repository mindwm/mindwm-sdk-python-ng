import asyncio
import os

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def get_root():
    return {"omg": "bebebe"}


@app.get("/health/liveness")
def liveness():
    return "OK"


@app.get("/health/readiness")
def readiness():
    return "OK"


async def main():
    log_level = os.environ('LOG_LEVEL', 'INFO')
    config = uvicorn.Config("mindwm.knfunc.server:app",
                            host="0.0.0.0",
                            port=8080,
                            log_level=log_level)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())

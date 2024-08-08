from fastapi import FastAPI
import asyncio
import uvicorn

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
    config = uvicorn.Config("mindwm.knfunc.server:app", port=8080, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())

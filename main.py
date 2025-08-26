from app.app import app
from app.config.config import config

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.host, port=config.port)

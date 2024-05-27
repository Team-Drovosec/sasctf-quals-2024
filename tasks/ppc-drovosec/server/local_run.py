# import uvicorn
from src.app import app
from starlette.staticfiles import StaticFiles

app.mount("/game", StaticFiles(directory="../static"), name="static")



# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=5000)

import threading
import webbrowser

import uvicorn

from webapp.server import app

HOST = "127.0.0.1"
PORT = 8765


def main():
    url = f"http://{HOST}:{PORT}"
    threading.Timer(1.2, lambda: webbrowser.open(url)).start()
    print(f"Dang chay web app tai {url}")
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")


if __name__ == "__main__":
    main()

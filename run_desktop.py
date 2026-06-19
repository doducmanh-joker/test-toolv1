import threading

import uvicorn
import webview

from webapp.server import app

HOST = "127.0.0.1"
PORT = 8766


def start_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")


def main():
    threading.Thread(target=start_server, daemon=True).start()
    webview.create_window(
        "Douyin Auto-Sub Tool",
        f"http://{HOST}:{PORT}",
        width=900,
        height=900,
        min_size=(600, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()

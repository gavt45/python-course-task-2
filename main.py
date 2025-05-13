import logging
import uvicorn

from config import UVICORN_HOST, UVICORN_PORT, UVICORN_UDS, DEBUG, FORWARDED_ALLOW_IPS

if __name__ == "__main__":
    try:
        uvicorn.run(
            "todo_app:app",
            host=('0.0.0.0' if DEBUG else UVICORN_HOST),
            port=UVICORN_PORT,
            uds=(None if DEBUG else UVICORN_UDS),
            workers=1,
            reload=DEBUG,
            log_level=logging.DEBUG if DEBUG else logging.INFO,
            proxy_headers=True,
            forwarded_allow_ips=FORWARDED_ALLOW_IPS,
        )
    except FileNotFoundError:  # to prevent error on removing unix sock
        pass

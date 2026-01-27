import logging

def log_error(msg, exc=None):
    if exc:
        logging.error(f"{msg}: {exc}")
    else:
        logging.error(msg)

def error_response(msg):
    log_error(msg)
    return {"status": "error", "message": msg}

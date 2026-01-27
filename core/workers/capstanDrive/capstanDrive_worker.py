
import os
import json
import threading
import queue
from datetime import datetime
from .capstanDrive_handler import CapstanDriveHandler

class CapstanDriveWorker(threading.Thread):
    def __init__(self, server_config, mailbox=None):
        super().__init__()
        self.server_config = server_config
        self.mailbox = mailbox or queue.Queue()
        self.running = threading.Event()
        self.running.set()
        self.handler = CapstanDriveHandler(self)
        self.command_dict = self.load_command_dictionary()

    def load_command_dictionary(self):
        dict_path = os.path.join(os.path.dirname(__file__), 'capstanDrive_commandDictionary.json')
        try:
            with open(dict_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log_error(f"Failed to load command dictionary: {e}")
            return {}

    def run(self):
        while self.running.is_set():
            try:
                msg = self.mailbox.get(timeout=0.2)
                self.dispatch_command(msg)
            except queue.Empty:
                continue
            except Exception as e:
                self.log_error(f"Worker run error: {e}")

    def dispatch_command(self, msg):
        try:
            cmd = msg.get('command')
            params = msg.get('params', {})
            if cmd in self.command_dict:
                self.handler.handle(cmd, params)
            else:
                self.log_error(f"Unknown command: {cmd}")
        except Exception as e:
            self.log_error(f"Dispatch error: {e}")

    def stop(self):
        self.running.clear()

    def log_error(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [CapstanDriveWorker ERROR] {message}")

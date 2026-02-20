
import json
import logging
import queue
from core.workers import handlers

class CapstanDriveWorker:
    def __init__(self, client_name="capstanDrive", mailbox=None):
        self.client_name = client_name
        self.command_dict = self.load_command_dict()
        self.config = self.load_config()
        self.handler = CapstanDriveHandler(self)
        self.last_error = None
        self.mailbox = mailbox or queue.Queue()

    def load_command_dict(self):
        try:
            import os
            dict_path = os.path.join(os.path.dirname(__file__), f"../../../../shared_dictionaries/command_dictionaries/{self.client_name}_commandDictionary.json")
            with open(dict_path, "r") as f:
                return json.load(f)["commands"]
        except Exception as e:
            self.last_error = f"Error loading command dictionary: {e}"
            logging.error(self.last_error)
            return {}
    
    def load_config(self):
        try:
            import importlib.util
            import os
            config_path = os.path.join(os.path.dirname(__file__), f"{self.client_name}/{self.client_name}_config.py")
            spec = importlib.util.spec_from_file_location(f'{self.client_name}_config', config_path)
            config_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_mod)
            return config_mod
        except Exception as e:
            logging.warning(f"Could not load config: {e}")
            return None

    def register_handlers(self):
        pass  # Handlers are now managed by CapstanDriveHandler

    def parse_and_dispatch(self, csv_command):
        try:
            parts = [p.strip() for p in csv_command.split(",") if p.strip()]
            if not parts:
                return self.error_response("Empty command")
            cmd = parts[0]
            if cmd not in self.command_dict:
                return self.error_response(f"Unknown command: {cmd}")
            cmd_info = self.command_dict[cmd]
            params = self.extract_params(parts[1:], cmd_info)
            if isinstance(params, dict) and "error" in params:
                return self.error_response(params["error"])
            self.handler.handle(cmd, params)
            # Optionally, send result to Supervisor via mailbox
            if self.should_notify_supervisor(cmd, result):
                self.mailbox.put((cmd, result))
            return result
        except Exception as e:
            logging.exception("Exception in parse_and_dispatch")
            return self.error_response(f"Exception: {e}")

    def extract_params(self, param_list, cmd_info):
        params = {}
        param_defs = cmd_info.get("parameters", [])
        context = {}
        i = 0
        for pdef in param_defs:
            conds = pdef.get("condition", [])
            if conds:
                try:
                    for cond in conds:
                        key, op, val = cond.split()
                        if op == "==":
                            if context.get(key) != val:
                                continue
                except Exception as e:
                    return {"error": f"Condition parse error: {e}"}
            idx = pdef.get("param_number", i+1) - 1
            if idx >= len(param_list):
                continue
            raw_val = param_list[idx]
            try:
                if pdef["type"] == "integer":
                    val = int(raw_val)
                elif pdef["type"] == "float":
                    val = float(raw_val)
                elif pdef["type"] == "boolean":
                    # Use BOOLEAN_CONFIG from config file if available
                    if self.config and hasattr(self.config, 'BOOLEAN_CONFIG'):
                        bool_config = self.config.BOOLEAN_CONFIG
                        true_strings = [s.lower() for s in bool_config.get('true_strings', ['true', '1'])]
                        false_strings = [s.lower() for s in bool_config.get('false_strings', ['false', '0'])]
                        raw_lower = raw_val.lower()
                        if raw_lower in true_strings:
                            val = True
                        elif raw_lower in false_strings:
                            val = False
                        else:
                            return {"error": f"Invalid boolean value: {raw_val}"}
                    else:
                        # Fallback to default behavior
                        val = bool(int(raw_val)) if raw_val in ("0", "1") else raw_val.lower() in ("true", "on")
                elif pdef["type"] == "enum":
                    if raw_val not in pdef.get("options", []):
                        return {"error": f"Invalid enum value: {raw_val}"}
                    val = raw_val
                else:
                    val = raw_val
                if "range" in pdef:
                    r = pdef["range"]
                    if "min" in r and val < r["min"]:
                        return {"error": f"Value {val} below min {r['min']}"}
                    if "max" in r and val > r["max"]:
                        return {"error": f"Value {val} above max {r['max']}"}
                params[pdef["name"]] = val
                context[pdef["name"]] = val
            except Exception as e:
                return {"error": f"Param {pdef['name']} error: {e}"}
            i += 1
        return params

    def should_notify_supervisor(self, cmd, result):
        # Example: notify for all errors or for GET_ commands
        if result.get("status") == "error":
            return True
        if cmd.startswith("GET_"):
            return True
        return False

    def poll_mailbox(self):
        # Non-blocking poll for messages from Supervisor
        try:
            while not self.mailbox.empty():
                msg = self.mailbox.get_nowait()
                self.handle_mailbox_message(msg)
        except Exception as e:
            logging.error(f"Mailbox poll error: {e}")

    def handle_mailbox_message(self, msg):
        # Implement logic to handle messages from Supervisor
        logging.info(f"Received mailbox message: {msg}")

    def error_response(self, msg):
        self.last_error = msg
        logging.error(msg)
        return {"status": "error", "message": msg}

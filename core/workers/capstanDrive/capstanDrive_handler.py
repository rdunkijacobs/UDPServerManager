class CapstanDriveHandler:
    def __init__(self, worker):
        self.worker = worker

    def handle(self, command, params):
        try:
            handler_method = getattr(self, f"handle_{command}", None)
            if handler_method:
                handler_method(params)
            else:
                self.worker.log_error(f"No handler for command: {command}")
        except Exception as e:
            self.worker.log_error(f"Handler error for {command}: {e}")

    def handle_led(self, params):
        # Example handler for 'led' command
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Handling LED command with params: {params}")
        # Implement actual logic here

    # Add more handlers as needed

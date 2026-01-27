
import socket
from PySide6.QtCore import QThread, Signal
from core.workers.capstanDrive.capstanDrive_worker import CapstanDriveWorker

class UDPClientThread(QThread):
    message_received = Signal(str)

    def __init__(self, host, port, client_name=None):
        super().__init__()
        self.host = host
        self.port = int(port)
        self.client_name = client_name
        self.running = True
        self.worker = CapstanDriveWorker(client_name) if client_name == "capstanDrive" else None
        self.sock = None  # Will be created in run()

    def send_message(self, msg):
        """Send a message over UDP using the same socket as the receive thread."""
        try:
            if self.sock is not None:
                self.sock.sendto(msg.encode(), (self.host, self.port))
                local_port = self.sock.getsockname()[1]
                self.message_received.emit(f"Sent: {msg} (from local port {local_port})")
                self.message_received.emit(f"[UDP] Still listening for responses on local port {local_port} after send.")
            else:
                self.message_received.emit("UDP Send Error: Socket not initialized.")
        except Exception as e:
            self.message_received.emit(f"UDP Send Error: {e}")
    def run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(1.0)
            self.sock.bind(("0.0.0.0", 0))
            local_port = self.sock.getsockname()[1]
            self.listening_port = local_port
            self.message_received.emit(f"[UDP] Listening for responses on local port {local_port}.")
            # No test command sent on startup; only user-initiated messages will be sent
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(4096)
                    msg = data.decode()
                    self.message_received.emit(f"Received from {addr}: {msg}")
                    # Parse and handle command if worker is available
                    if self.worker:
                        response = self.worker.parse_and_dispatch(msg)
                        self.message_received.emit(f"Handler response: {response}")
                except socket.timeout:
                    continue
                except Exception as e:
                    self.message_received.emit(f"UDP Receive Error: {e}")
        except Exception as e:
            self.message_received.emit(f"UDP Error: {e}")
        finally:
            if self.sock is not None:
                self.sock.close()
                self.sock = None
    def stop(self):
        self.running = False
        self.wait()

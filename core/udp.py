
import socket
from PySide6.QtCore import QThread, Signal

class UDPClientThread(QThread):
    message_received = Signal(str)
    pong_received = Signal(str, float, dict)  # worker_name, ping_time, additional_info

    def __init__(self, host, port, client_name=None):
        super().__init__()
        self.host = host
        self.port = int(port)
        self.client_name = client_name
        self.running = True
        self.sock = None  # Will be created in run()
        self.pending_pings = {}  # Track pending pings keyed by tracking key

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
                    
                    # NEW: Check for ping/pong messages (bypass normal command flow)
                    if msg == 'PING' or msg.startswith('PING:') or msg == 'PONG' or msg.startswith('PONG:'):
                        if msg == 'PONG' or msg.startswith('PONG:'):
                            self.message_received.emit(f"[UDP] Received PONG: {msg}")
                            self._handle_pong_message(msg)
                        continue  # Don't process through normal command flow
                    
                    self.message_received.emit(f"Received from {addr}: {msg}")
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
    
    # NEW METHODS FOR HEALTH MONITORING
    def send_ping(self, ping_time, send_timestamp=False):
        """
        Send ping to device (non-blocking, for health monitoring).
        
        Args:
            ping_time: Timestamp of ping request (used internally for tracking)
            send_timestamp: If True, include timestamp (for first contact/recovery)
        """
        try:
            if send_timestamp:
                from datetime import datetime, timezone
                # Create human-readable timestamp: yyyymmdd.HHMMSS.xxx
                dt = datetime.fromtimestamp(ping_time, tz=timezone.utc)
                human_time = dt.strftime('%Y%m%d.%H%M%S.') + f"{dt.microsecond // 1000:03d}"
                message = f"PING:{human_time}"
                tracking_key = human_time
            else:
                # Minimal ping - just 4 bytes!
                message = "PING"
                tracking_key = "PING"
            
            # Track pending ping
            self.pending_pings[tracking_key] = ping_time  # Store send time for round-trip calc
            print(f"[UDP DEBUG] Sending {message}")
            
            # Send via UDP (non-blocking)
            if self.sock is not None:
                self.sock.sendto(message.encode(), (self.host, self.port))
                print(f"[UDP DEBUG] PING sent to {self.host}:{self.port}")
            else:
                print(f"[UDP DEBUG] ERROR: Socket is None, cannot send PING")
                
        except Exception as e:
            print(f"Failed to send ping: {e}")
    
    def _handle_pong_message(self, message):
        """
        Handle incoming PONG message (bypass normal command flow).
        
        Format: PONG or PONG:timestamp
        """
        try:
            parts = message.split(':', 1)
            if len(parts) < 1:
                print(f"[UDP DEBUG] Invalid PONG format: {message}")
                return
            
            # Determine tracking key (PING or timestamp)
            if len(parts) == 2:
                tracking_key = parts[1]  # PONG with timestamp
            else:
                tracking_key = "PING"  # Simple PONG
            
            print(f"[UDP DEBUG] PONG received: {tracking_key}")
            
            # Check if this PONG matches a pending PING
            if tracking_key in self.pending_pings:
                # Get original send time and calculate round-trip
                ping_time = self.pending_pings[tracking_key]
                del self.pending_pings[tracking_key]
                
                # Emit pong_received signal with worker name (use ping_time for round-trip calc)
                print(f"[UDP DEBUG] Emitting pong_received signal for {self.client_name}")
                self.pong_received.emit(self.client_name, ping_time, {})
                
        except Exception as e:
            print(f"[UDP DEBUG] Failed to parse PONG: {e}")
            print(f"Error handling PONG message: {e}")
    
    def send_zulu_sync(self, broadcast=False):
        """
        Send ZULU time synchronization to edge device(s).
        
        Format: ZULU:yyyymmdd:hhmmss.xxx
        
        Args:
            broadcast: If True, send to broadcast address (all devices on network)
        """
        try:
            from datetime import datetime, timezone
            
            # Get current ZULU (UTC) time
            now_utc = datetime.now(timezone.utc)
            
            # Format: ZULU:yyyymmdd:hhmmss.xxx
            date_str = now_utc.strftime('%Y%m%d')
            time_str = now_utc.strftime('%H%M%S.%f')[:-3]  # Include milliseconds
            message = f"ZULU:{date_str}:{time_str}"
            
            if self.sock is None:
                print(f"[ZULU SYNC] ERROR: Socket is None, cannot send")
                return
            
            if broadcast:
                # Enable broadcast on socket
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                # Send to broadcast address
                broadcast_addr = ('<broadcast>', self.port)
                self.sock.sendto(message.encode(), broadcast_addr)
                print(f"[ZULU SYNC] Broadcast sent: {message}")
                self.message_received.emit(f"[ZULU SYNC] Broadcast: {message}")
            else:
                # Send to specific device
                self.sock.sendto(message.encode(), (self.host, self.port))
                print(f"[ZULU SYNC] Sent to {self.host}:{self.port}: {message}")
                self.message_received.emit(f"[ZULU SYNC] Sent: {message}")
                
        except Exception as e:
            print(f"[ZULU SYNC] Failed to send: {e}")
            self.message_received.emit(f"[ZULU SYNC] Error: {e}")
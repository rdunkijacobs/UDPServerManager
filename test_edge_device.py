"""
Test Edge Device Server - Simulates an edge device for testing health monitoring.

This standalone server:
1. Listens on a UDP port
2. Responds to PING messages with PONG (for health monitoring)
3. Responds to regular commands (for normal operation testing)
4. Collects and reports metrics (uptime, temperature, cpu, etc.)

Usage:
    python test_edge_device.py [--port PORT] [--host HOST]

Example:
    python test_edge_device.py --port 5000 --host 0.0.0.0
"""

import socket
import time
import argparse
import random
import platform
import psutil  # pip install psutil if not available


class TestEdgeDevice:
    """Simulated edge device with health monitoring support."""
    
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.start_time = time.time()
        
        # ZULU time synchronization (milliseconds)
        self.zulu_offset_ms = 0  # Offset in ms: ZULU_ms - uptime_ms
        self.time_synced = False
        
        # Simulated device state
        self.led_status = "OFF"
        self.motor_position = 0
        self.device_name = "TestDevice"
        
        print(f"[TestEdgeDevice] Initializing on {host}:{port}")
    
    def start(self):
        """Start the UDP server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(0.5)  # Short timeout for responsive shutdown
            self.sock.bind((self.host, self.port))
            self.running = True
            
            print(f"[TestEdgeDevice] Listening on {self.host}:{self.port}")
            print("[TestEdgeDevice] Ready to receive commands and health checks")
            print("[TestEdgeDevice] Press Ctrl+C to stop")
            print("-" * 60)
            
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(4096)
                    message = data.decode('utf-8', errors='ignore')
                    
                    print(f"[RECV] {message} from {addr}")
                    
                    # Handle message and generate response
                    response = self.handle_message(message)
                    
                    if response:
                        # Send response back to sender
                        try:
                            self.sock.sendto(response.encode('utf-8'), addr)
                            print(f"[SEND] {response} to {addr}")
                        except OSError as e:
                            # Handle "connection reset" errors (common when remote closes)
                            if e.winerror == 10054:
                                print(f"[WARN] Remote host closed connection (normal during restart)")
                            else:
                                print(f"[ERROR] Send failed: {e}")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"[ERROR] {e}")
                    
        except Exception as e:
            print(f"[FATAL] Failed to start server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server."""
        self.running = False
        if self.sock:
            self.sock.close()
            self.sock = None
        print("\n[TestEdgeDevice] Stopped")
    
    def handle_message(self, message):
        """
        Handle incoming message and return response.
        
        Args:
            message: Received message string
            
        Returns:
            Response string or None
        """
        # PRIORITY 1: ZULU time sync (intercept at UDP level, no response)
        if message.startswith('ZULU:'):
            self.handle_zulu_sync(message)
            return None  # No response needed
        
        # PRIORITY 2: Health Check PING (high priority)
        if message == 'PING' or message.startswith('PING:'):
            return self.handle_ping(message)
        
        # PRIORITY 3: Regular commands
        # Parse command format: COMMAND:param1:param2:...
        parts = message.split(':')
        command = parts[0].upper()
        
        if command == 'LED':
            return self.handle_led_command(parts)
        elif command == 'MOTOR':
            return self.handle_motor_command(parts)
        elif command == 'STATUS':
            return self.handle_status_command(parts)
        elif command == 'ECHO':
            return self.handle_echo_command(parts)
        else:
            return f"ERROR:Unknown command: {command}"
    
    def handle_zulu_sync(self, message):
        """
        Handle ZULU time synchronization (one-time setup).
        
        Format: ZULU:yyyymmdd:hhmmss.xxx
        
        This intercepts at UDP level and syncs edge device time to ZULU.
        No response is sent back.
        
        Calculates: zulu_offset_ms = ZULU_timestamp_ms - uptime_ms
        """
        try:
            parts = message.split(':')
            
            if len(parts) != 3:
                print(f"[ZULU SYNC] Invalid format: {message}")
                return
            
            date_str = parts[1]  # yyyymmdd
            time_str = parts[2]  # hhmmss.xxx
            
            # Parse ZULU time
            from datetime import datetime, timezone
            
            # Parse: yyyymmdd + hhmmss.xxx
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            
            hour = int(time_str[0:2])
            minute = int(time_str[2:4])
            second = int(time_str[4:6])
            millisecond = int(time_str[7:10]) if len(time_str) >= 10 else 0
            
            # Create ZULU datetime
            zulu_dt = datetime(year, month, day, hour, minute, second, 
                              millisecond * 1000, tzinfo=timezone.utc)
            zulu_timestamp_s = zulu_dt.timestamp()
            zulu_timestamp_ms = int(zulu_timestamp_s * 1000)
            
            # Calculate offset in milliseconds: zulu_offset = ZULU_ms - uptime_ms
            uptime_ms = int(self.get_uptime() * 1000)
            self.zulu_offset_ms = zulu_timestamp_ms - uptime_ms
            self.time_synced = True
            
            print(f"[ZULU SYNC] Time synchronized to {zulu_dt.isoformat()}")
            print(f"[ZULU SYNC] ZULU timestamp (ms): {zulu_timestamp_ms}")
            print(f"[ZULU SYNC] Uptime (ms): {uptime_ms}")
            print(f"[ZULU SYNC] Offset (ms): {self.zulu_offset_ms}")
            
        except Exception as e:
            print(f"[ZULU SYNC] Error: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_ping(self, message):
        """
        Handle PING message for health monitoring.
        
        Format: PING or PING:timestamp
        Response: PONG or PONG:timestamp
        
        Minimal response - just acknowledge. Metrics sent via separate command.
        """
        try:
            parts = message.split(':', 1)
            
            # Check if timestamp included
            has_timestamp = len(parts) == 2
            
            if has_timestamp:
                time_str = parts[1]
                return f"PONG:{time_str}"
            else:
                return "PONG"
            
        except Exception as e:
            print(f"[ERROR] Failed to handle PING: {e}")
            import traceback
            traceback.print_exc()
            return "ERROR:Exception in handle_ping"
    
    def handle_led_command(self, parts):
        """Handle LED command: LED:ON or LED:OFF"""
        if len(parts) < 2:
            return "ERROR:LED command requires parameter (ON/OFF)"
        
        state = parts[1].upper()
        if state in ['ON', 'OFF']:
            self.led_status = state
            return f"OK:LED:{state}"
        else:
            return f"ERROR:Invalid LED state: {state}"
    
    def handle_motor_command(self, parts):
        """Handle MOTOR command: MOTOR:position"""
        if len(parts) < 2:
            return "ERROR:MOTOR command requires position parameter"
        
        try:
            position = int(parts[1])
            self.motor_position = position
            return f"OK:MOTOR:{position}"
        except ValueError:
            return f"ERROR:Invalid motor position: {parts[1]}"
    
    def handle_status_command(self, parts):
        """Handle STATUS command: return device status"""
        status = {
            'device': self.device_name,
            'uptime': f"{self.get_uptime():.1f}s",
            'led': self.led_status,
            'motor': self.motor_position,
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage()
        }
        
        # Format as: STATUS:key1=val1:key2=val2:...
        status_str = ':'.join([f"{k}={v}" for k, v in status.items()])
        return f"STATUS:{status_str}"
    
    def handle_echo_command(self, parts):
        """Handle ECHO command: echo back the message"""
        if len(parts) < 2:
            return "ERROR:ECHO command requires message"
        
        message = ':'.join(parts[1:])
        return f"ECHO:{message}"
    
    # ========================================================================
    # METRIC COLLECTION METHODS
    # ========================================================================
    
    def get_zulu_time(self):
        """Return current time in ZULU (UTC) based on synchronized offset."""
        if self.time_synced:
            # Calculate: zulu_offset_ms + current_uptime_ms
            current_uptime_ms = int(self.get_uptime() * 1000)
            current_zulu_ms = self.zulu_offset_ms + current_uptime_ms
            return current_zulu_ms / 1000.0
        else:
            # If not synced yet, return local time
            return time.time()
    
    def get_uptime(self):
        """Return uptime in seconds."""
        return time.time() - self.start_time
    
    def get_temperature(self):
        """
        Return CPU temperature.
        
        Note: Real implementation depends on hardware.
        This is a simulated value for testing.
        """
        # Simulate temperature with some variation
        base_temp = 45.0  # Base temperature
        variation = random.uniform(-5.0, 10.0)  # Random variation
        temp = base_temp + variation
        
        # Try to get real temperature on supported platforms
        try:
            if platform.system() == 'Linux':
                # Raspberry Pi / Linux systems
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read()) / 1000.0
        except:
            pass
        
        return f"{temp:.1f}C"
    
    def get_cpu_usage(self):
        """Return CPU usage percentage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return f"{cpu_percent:.1f}%"
        except:
            # Fallback if psutil not available
            return f"{random.uniform(10, 80):.1f}%"
    
    def get_memory_usage(self):
        """Return memory usage percentage."""
        try:
            mem = psutil.virtual_memory()
            return f"{mem.percent:.1f}%"
        except:
            # Fallback if psutil not available
            return f"{random.uniform(30, 70):.1f}%"


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description='Test Edge Device Server - Simulates edge device for health monitoring testing'
    )
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host address to bind to (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='UDP port to listen on (default: 5000)'
    )
    
    args = parser.parse_args()
    
    # Create and start test device
    device = TestEdgeDevice(host=args.host, port=args.port)
    
    try:
        device.start()
    except KeyboardInterrupt:
        print("\n[TestEdgeDevice] Received Ctrl+C, shutting down...")
        device.stop()


if __name__ == '__main__':
    main()

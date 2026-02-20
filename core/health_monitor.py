"""
Health Monitor System v2.01

Implements round-robin health checking with sliding window failure analysis.
Monitors all registered workers using ping/pong UDP messaging.

Architecture:
- HealthStatus: Tracks individual worker health with sliding windows
- HealthMonitor: Manages round-robin scheduling and worker coordination
"""

import time
from collections import deque
from PySide6.QtCore import QObject, Signal, QTimer
import config


class HealthStatus:
    """
    Health status tracker for a single worker with sliding window analysis.
    
    Tracks:
    - Last M checks (success/failure)
    - Last N response times (for slow detection)
    - Error level determination (WARNING, CRITICAL, FATAL)
    """
    
    def __init__(self, worker_name):
        self.worker_name = worker_name
        
        # Sliding windows
        self.check_history = deque(maxlen=config.HEALTH_CHECK_WINDOW_SIZE)
        self.response_times = deque(maxlen=config.HEALTH_CHECK_SLOW_WINDOW)
        self.transit_times = deque(maxlen=config.HEALTH_CHECK_TRANSIT_WINDOW)  # 3-minute window
        
        # State tracking
        self.last_ping_time = 0.0
        self.last_pong_time = 0.0
        self.last_response_time_ms = None
        self.consecutive_failures = 0
        self.status = 'unknown'
        self.error_level = 'UNKNOWN'
        self.previous_error_level = 'UNKNOWN'  # For recovery detection
        self.negotiated_metrics = []
        self.additional_info = {}
        self.last_error = None
        self.transit_anomaly_detected = False
        
    def record_success(self, response_time_ms, additional_info=None):
        """Record successful health check."""
        self.check_history.append(True)
        self.response_times.append(response_time_ms)
        self.transit_times.append(response_time_ms)  # Also track for statistical analysis
        self.last_pong_time = time.time()
        self.last_response_time_ms = response_time_ms
        self.consecutive_failures = 0
        
        if additional_info:
            self.additional_info = additional_info
        
        self._update_status()
    
    def record_failure(self, error_msg):
        """Record failed health check (timeout or error)."""
        self.check_history.append(False)
        self.consecutive_failures += 1
        self.last_error = error_msg
        self._update_status()
    
    def _check_transit_anomaly(self):
        """Check if latest transit time is anomalous (>2 std dev from mean)."""
        # Need full window before checking
        if len(self.transit_times) < config.HEALTH_CHECK_TRANSIT_WINDOW:
            return False
        
        # Calculate mean and standard deviation
        import statistics
        try:
            mean_time = statistics.mean(self.transit_times)
            stddev_time = statistics.stdev(self.transit_times)
            
            # Check if latest time is outside threshold
            latest_time = self.transit_times[-1]
            threshold = mean_time + (config.HEALTH_CHECK_TRANSIT_STDDEV_THRESHOLD * stddev_time)
            
            if latest_time > threshold:
                print(f"[Transit Anomaly] {self.worker_name}: {latest_time:.1f}ms > {threshold:.1f}ms "
                      f"(mean={mean_time:.1f}ms, stddev={stddev_time:.1f}ms)")
                return True
        except statistics.StatisticsError:
            # Not enough variation to calculate stddev
            pass
        
        return False
    
    def _update_status(self):
        """
        Analyze sliding windows and determine error level.
        
        Priority order:
        1. FATAL: N failures in last M checks
        2. CRITICAL: Last check failed
        3. WARNING: Slow responses OR transit time anomaly
        4. HEALTHY: All good
        """
        # Store previous state for recovery detection
        self.previous_error_level = self.error_level
        
        # Need data to evaluate
        if len(self.check_history) == 0:
            self.status = 'unknown'
            self.error_level = 'UNKNOWN'
            return
        
        # Check for FATAL: N failures in sliding window
        failures_in_window = sum(1 for success in self.check_history if not success)
        if failures_in_window >= config.HEALTH_CHECK_FATAL_THRESHOLD:
            self.status = 'fatal'
            self.error_level = 'FATAL'
            # Clear transit window on FATAL
            self.transit_times.clear()
            self.transit_anomaly_detected = False
            return
        
        # Check for CRITICAL: Last check failed
        if not self.check_history[-1]:
            self.status = 'critical'
            self.error_level = 'CRITICAL'
            # Clear transit window on CRITICAL
            self.transit_times.clear()
            self.transit_anomaly_detected = False
            return
        
        # Check for WARNING: Transit time anomaly (must check before slow responses)
        self.transit_anomaly_detected = self._check_transit_anomaly()
        if self.transit_anomaly_detected:
            self.status = 'warning'
            self.error_level = 'WARNING'
            self.last_error = f"Transit time anomaly detected"
            return
        
        # Check for WARNING: Slow responses
        if len(self.response_times) >= config.HEALTH_CHECK_SLOW_THRESHOLD:
            slow_count = sum(1 for rt in self.response_times 
                           if rt > config.HEALTH_CHECK_SLOW_RESPONSE_MS)
            if slow_count >= config.HEALTH_CHECK_SLOW_THRESHOLD:
                self.status = 'warning'
                self.error_level = 'WARNING'
                return
        
        # All checks passed
        self.status = 'healthy'
        self.error_level = 'HEALTHY'
        self.last_error = None
    
    def get_status_dict(self):
        """Return current status as dictionary for display."""
        return {
            'worker': self.worker_name,
            'status': self.status,
            'error_level': self.error_level,
            'response_time_ms': self.last_response_time_ms,
            'consecutive_failures': self.consecutive_failures,
            'failures_in_window': sum(1 for s in self.check_history if not s),
            'slow_responses': sum(1 for rt in self.response_times if rt > config.HEALTH_CHECK_SLOW_RESPONSE_MS),
            'transit_window_size': len(self.transit_times),
            'transit_anomaly': self.transit_anomaly_detected,
            'last_check': self.last_ping_time,
            'last_response': self.last_pong_time,
            'error': self.last_error,
            'metrics': self.additional_info
        }
    
    def get_tooltip_text(self):
        """Generate tooltip text for UI display."""
        if self.status == 'healthy':
            return f"Status: HEALTHY\nResponse: {self.last_response_time_ms:.0f}ms\nLast: {time.strftime('%H:%M:%S', time.localtime(self.last_pong_time))}"
        elif self.status == 'warning':
            if self.transit_anomaly_detected:
                # Show transit anomaly details
                import statistics
                mean_time = statistics.mean(self.transit_times) if len(self.transit_times) > 0 else 0
                stddev_time = statistics.stdev(self.transit_times) if len(self.transit_times) > 1 else 0
                return f"Status: WARNING\nTransit anomaly: {self.last_response_time_ms:.0f}ms\nMean: {mean_time:.0f}ms (±{stddev_time:.0f}ms)"
            else:
                # Show slow response details
                slow = sum(1 for rt in self.response_times if rt > config.HEALTH_CHECK_SLOW_RESPONSE_MS)
                return f"Status: WARNING\n{slow}/{len(self.response_times)} slow responses\nAvg: {sum(self.response_times)/len(self.response_times):.0f}ms"
        elif self.status == 'critical':
            return f"Status: CRITICAL\nNo response\nLast: {time.strftime('%H:%M:%S', time.localtime(self.last_ping_time))}"
        elif self.status == 'fatal':
            failures = sum(1 for s in self.check_history if not s)
            return f"Status: FATAL\n{failures}/{len(self.check_history)} checks failed\n{self.last_error}"
        else:
            return "Status: UNKNOWN\nNo data"


class HealthMonitor(QObject):
    """
    Core health monitoring system with round-robin scheduling.
    
    Features:
    - Non-blocking, lowest priority operation
    - Round-robin scheduling across all workers
    - Timing analysis and warnings
    - Immediate controller escalation on CRITICAL/FATAL
    """
    
    # Signals
    health_status_updated = Signal(str, dict)  # worker_name, status_dict
    health_warning = Signal(str, str)  # worker_name, message
    health_critical = Signal(str, str)  # worker_name, message
    health_fatal = Signal(str, str)  # worker_name, message
    escalate_to_controller = Signal(str, dict)  # worker_name, status_dict
    round_robin_cycle_complete = Signal(float)  # cycle_time_seconds
    round_robin_timing_warning = Signal(float, float)  # actual, target
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.enabled = config.HEALTH_CHECK_ENABLED
        self.workers = {}  # {worker_name: worker_instance}
        self.health_status = {}  # {worker_name: HealthStatus}
        
        # Round-robin state
        self.cycle_start_time = 0.0
        self.next_cycle_time = 0.0
        self.waiting_for_next_cycle = False
        self.current_worker_index = 0
        self.workers_checked_this_cycle = set()
        
        # Timer for lowest-priority scheduling
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._perform_next_check)
        self.timer.setInterval(10)  # 10ms tick, logic controls actual checks
        
        if not self.enabled:
            print("HealthMonitor: Disabled (HEALTH_CHECK_ENABLED=False)")
    
    def register_worker(self, worker_name, worker_instance, negotiated_metrics=None):
        """Register a worker for health monitoring."""
        if not self.enabled:
            return
        
        self.workers[worker_name] = worker_instance
        status = HealthStatus(worker_name)
        
        if negotiated_metrics:
            status.negotiated_metrics = negotiated_metrics
        else:
            status.negotiated_metrics = config.STANDARD_HEALTH_METRICS
        
        self.health_status[worker_name] = status
        
        # Connect pong signal
        if hasattr(worker_instance, 'pong_received'):
            worker_instance.pong_received.connect(self._handle_pong)
        
        print(f"HealthMonitor: Registered '{worker_name}' with metrics: {status.negotiated_metrics}")
    
    def start(self):
        """Start health monitoring."""
        if not self.enabled:
            print("HealthMonitor: Not starting (disabled in config)")
            return
        
        if not self.workers:
            print("HealthMonitor: No workers registered")
            return
        
        self.cycle_start_time = time.time()
        self.next_cycle_time = 0.0
        self.waiting_for_next_cycle = False
        self.current_worker_index = 0
        self.workers_checked_this_cycle.clear()
        self.timer.start()
        
        print(f"HealthMonitor: Started monitoring {len(self.workers)} workers")
    
    def stop(self):
        """Stop health monitoring."""
        self.timer.stop()
        print("HealthMonitor: Stopped")
    
    def trigger_manual_check(self, worker_name=None):
        """
        Manually trigger health check.
        
        Args:
            worker_name: Specific worker to check, or None to check all workers
        """
        if not self.enabled:
            return
        
        if worker_name is None:
            # Check all workers
            for name in self.workers.keys():
                print(f"HealthMonitor: Manual check for '{name}'")
                self._send_ping(name)
        else:
            # Check specific worker
            if worker_name not in self.workers:
                print(f"HealthMonitor: Unknown worker '{worker_name}'")
                return
            
            print(f"HealthMonitor: Manual check for '{worker_name}'")
            self._send_ping(worker_name)
    
    def get_health_status(self, worker_name):
        """Get current health status for worker."""
        if worker_name in self.health_status:
            return self.health_status[worker_name].get_status_dict()
        return None
    
    def _perform_next_check(self):
        """
        Perform next check in round-robin cycle.
        Called by timer (10ms interval), but logic controls actual checking.
        """
        if not self.workers:
            return
        
        # Check if we're waiting for next cycle to start
        if self.waiting_for_next_cycle:
            if time.time() >= self.next_cycle_time:
                # Start new cycle
                self.waiting_for_next_cycle = False
                self.cycle_start_time = time.time()
                self.workers_checked_this_cycle.clear()
                self.current_worker_index = 0
            else:
                # Still waiting, do nothing
                return
        
        worker_names = list(self.workers.keys())
        
        # Check if cycle complete
        if len(self.workers_checked_this_cycle) >= len(worker_names):
            self._complete_cycle()
            return
        
        # Get next worker
        worker_name = worker_names[self.current_worker_index]
        self.current_worker_index = (self.current_worker_index + 1) % len(worker_names)
        
        # Skip if already checked this cycle
        if worker_name in self.workers_checked_this_cycle:
            return
        
        # Send ping
        self._send_ping(worker_name)
        self.workers_checked_this_cycle.add(worker_name)
    
    def _complete_cycle(self):
        """Complete round-robin cycle and check timing."""
        cycle_time = time.time() - self.cycle_start_time
        
        self.round_robin_cycle_complete.emit(cycle_time)
        
        # Check if cycle exceeded target
        if cycle_time > config.HEALTH_CHECK_ROUND_ROBIN_INTERVAL:
            msg = (f"Round-robin took {cycle_time:.2f}s, "
                   f"exceeds target {config.HEALTH_CHECK_ROUND_ROBIN_INTERVAL}s")
            print(f"HealthMonitor WARNING: {msg}")
            self.round_robin_timing_warning.emit(cycle_time, 
                                                 config.HEALTH_CHECK_ROUND_ROBIN_INTERVAL)
        
        # Wait for next cycle (respect the interval)
        self.waiting_for_next_cycle = True
        self.next_cycle_time = self.cycle_start_time + config.HEALTH_CHECK_ROUND_ROBIN_INTERVAL
    
    def _send_ping(self, worker_name):
        """Send ping to worker."""
        worker = self.workers.get(worker_name)
        if not worker:
            return
        
        status = self.health_status[worker_name]
        status.last_ping_time = time.time()
        
        try:
            # Determine if we should send timestamp
            # Send timestamp on: first contact OR recovery from FATAL/CRITICAL
            send_timestamp = False
            if status.error_level == 'UNKNOWN':
                # First contact (no checks yet)
                send_timestamp = True
                print(f"[HealthMonitor] First contact with {worker_name} - sending timestamp")
            elif hasattr(status, 'previous_error_level'):
                # Check for recovery from FATAL/CRITICAL
                if status.previous_error_level in ['FATAL', 'CRITICAL'] and status.error_level in ['HEALTHY', 'WARNING']:
                    send_timestamp = True
                    print(f"[HealthMonitor] {worker_name} recovered from {status.previous_error_level} - sending timestamp")
            
            # Send ping (with or without timestamp)
            worker.send_ping(status.last_ping_time, send_timestamp)
            
            # Start timeout timer
            QTimer.singleShot(
                int(config.HEALTH_CHECK_PONG_TIMEOUT * 1000),
                lambda: self._check_timeout(worker_name, status.last_ping_time)
            )
            
        except Exception as e:
            error_msg = f"Ping send error: {e}"
            print(f"HealthMonitor WARNING: {worker_name} - {error_msg}")
            status.record_failure(error_msg)
            self._emit_status_signals(worker_name, status)
    
    def _check_timeout(self, worker_name, ping_time):
        """Check if ping timed out."""
        status = self.health_status.get(worker_name)
        if not status:
            return
        
        # If pong received, last_pong_time will be >= ping_time
        if status.last_pong_time >= ping_time:
            return  # Pong received on time
        
        # Timeout occurred
        error_msg = f"No PONG within {config.HEALTH_CHECK_PONG_TIMEOUT}s"
        status.record_failure(error_msg)
        
        print(f"HealthMonitor WARNING: {worker_name} timeout "
              f"({status.consecutive_failures} consecutive)")
        
        self._emit_status_signals(worker_name, status)
    
    def _handle_pong(self, worker_name, ping_time, additional_info):
        """Handle pong response from worker."""
        status = self.health_status.get(worker_name)
        if not status:
            return
        
        # Calculate response time
        response_time_ms = (time.time() - ping_time) * 1000
        
        # Record success
        status.record_success(response_time_ms, additional_info)
        
        # Emit signals
        self._emit_status_signals(worker_name, status)
    
    def _emit_status_signals(self, worker_name, status):
        """Emit appropriate signals based on status."""
        status_dict = status.get_status_dict()
        
        # Always emit status update
        self.health_status_updated.emit(worker_name, status_dict)
        
        # Check if status changed (for escalation and popups)
        status_changed = status.previous_error_level != status.error_level
        
        # Emit level-specific signals (only on state transitions)
        if status.error_level == 'FATAL':
            print(f"HealthMonitor FATAL: {worker_name} - {status.last_error}")
            # Only emit signals and escalate on state transition
            if status_changed:
                self.health_fatal.emit(worker_name, status.last_error or "Fatal error")
                self.escalate_to_controller.emit(worker_name, status_dict)
            
        elif status.error_level == 'CRITICAL':
            print(f"HealthMonitor CRITICAL: {worker_name} - {status.last_error}")
            # Only emit signals and escalate on state transition
            if status_changed:
                self.health_critical.emit(worker_name, status.last_error or "Critical error")
                self.escalate_to_controller.emit(worker_name, status_dict)
            
        elif status.error_level == 'WARNING':
            # WARNING is logged every time but popup only on transition
            if status_changed:
                print(f"HealthMonitor WARNING: {worker_name} - Slow responses")
                self.health_warning.emit(worker_name, "Slow response times detected")
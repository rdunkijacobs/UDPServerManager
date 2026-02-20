# Health Monitor Testing Guide - v2.01

This guide explains how to test the Health Monitor system using the test edge device.

## Phase 2: Testing Setup

### Prerequisites

1. **Install psutil** (for CPU/memory metrics):
   ```powershell
   pip install psutil
   ```

2. **Update data/servers.json** to include test device:
   ```json
   {
     "servers": [
       {
         "name": "TestDevice",
         "description": "Test Edge Device",
         "host": "127.0.0.1",
         "ip": "127.0.0.1",
         "port": 5000,
         "worker_type": "capstan_drive",
         "status": "green",
         "location": "Local",
         "health_metrics": ["uptime", "temperature", "cpu", "memory"]
       }
     ]
   }
   ```

### Starting the Test Edge Device

**Terminal 1 - Start test edge device:**
```powershell
python test_edge_device.py --port 5000 --host 0.0.0.0
```

Expected output:
```
[TestEdgeDevice] Initializing on 0.0.0.0:5000
[TestEdgeDevice] Listening on 0.0.0.0:5000
[TestEdgeDevice] Ready to receive commands and health checks
[TestEdgeDevice] Press Ctrl+C to stop
------------------------------------------------------------
```

**Terminal 2 - Start UDPServerManager:**
```powershell
python main.py
```

---

## Test Scenarios

### Scenario 1: Health Monitoring Disabled (Default)

**Config:** `config.py` has `HEALTH_CHECK_ENABLED = False`

**Steps:**
1. Start test edge device (Terminal 1)
2. Start UDPServerManager (Terminal 2)
3. Select "TestDevice" from device panel

**Expected Results:**
- ✅ Application starts normally
- ✅ No "Check Health" button visible
- ✅ No health monitoring messages in log
- ✅ Device icon remains green (default status)
- ✅ Regular commands work normally

**Test Command:**
- Click "SELECT COMMAND" → choose any command → Send
- Edge device should respond normally

---

### Scenario 2: Health Monitoring Enabled - Normal Operation

**Config:** Change `config.py` to `HEALTH_CHECK_ENABLED = True`

**Steps:**
1. Edit `config.py`: Set `HEALTH_CHECK_ENABLED = True`
2. Start test edge device (Terminal 1)
3. Start UDPServerManager (Terminal 2)
4. Select "TestDevice" from device panel

**Expected Results:**
- ✅ Log shows: `[HealthMonitor] Health monitoring system initialized`
- ✅ "Check Health" button appears (enabled after device selection)
- ✅ Log shows: `[HealthMonitor] Registered worker: TestDevice`
- ✅ Health checks start automatically every 10 seconds
- ✅ Device icon remains green (healthy)

**Terminal 1 Output (Edge Device):**
```
[RECV] PING:1708502400.123:uptime,temperature,cpu,memory from ('127.0.0.1', 54321)
[SEND] PONG:1708502400.123:uptime=123.4s,temperature=45.2C,cpu=23.5%,memory=56.7% to ('127.0.0.1', 54321)
```

**Terminal 2 Output (UDPServerManager):**
```
[HealthMonitor] Health check cycle starting...
[HealthMonitor] TestDevice: OK (Last check: 2026-02-20 10:30:00)
```

---

### Scenario 3: Manual Health Check

**Steps:**
1. With health monitoring enabled and device selected
2. Click "Check Health" button

**Expected Results:**
- ✅ Log shows: `[HealthMonitor] Manual health check triggered`
- ✅ Immediate PING sent to device
- ✅ Device responds with PONG
- ✅ Health status updated immediately

---

### Scenario 4: Slow Response Warning

**Simulate slow response:**

**Option A - Modify test_edge_device.py:**
Add delay in `handle_ping` method:
```python
def handle_ping(self, message):
    import time
    time.sleep(0.6)  # 600ms delay (exceeds 500ms threshold)
    # ... rest of method
```

**Option B - Network delay:**
Use network throttling tools to add latency

**Expected Results:**
- ⚠️ Device icon turns yellow (WARNING)
- ⚠️ Log shows: `[HealthMonitor WARNING] TestDevice: Slow response time`
- ⚠️ Tooltip shows response time details

---

### Scenario 5: Critical - Last Check Failed

**Simulate timeout:**

**Steps:**
1. Stop the test edge device (Ctrl+C in Terminal 1)
2. Wait for next health check (max 10 seconds)

**Expected Results:**
- 🟠 Device icon turns orange/red (CRITICAL)
- 🟠 Message box appears: "Health Check Critical"
- 🟠 Log shows: `[HealthMonitor CRITICAL] TestDevice: Health check failed`
- 🟠 Tooltip shows "Last check: FAILED"

**Message Box Details:**
- Title: "Health Check Critical"
- Text: "Device TestDevice health check CRITICAL"
- Icon: Warning ⚠️

---

### Scenario 6: Fatal - Multiple Failures

**Config:** Default is 3 failures in 10 checks window

**Steps:**
1. Keep test edge device stopped
2. Wait for 3+ failed health checks (30+ seconds)

**Expected Results:**
- 🔴 Device icon turns red (FATAL)
- 🔴 Message box appears: "Health Check Fatal"
- 🔴 Log shows: `[HealthMonitor FATAL] TestDevice: Multiple health checks failed`
- 🔴 Log shows: `[HealthMonitor ESCALATE] TestDevice [FATAL]: ...`

**Message Box Details:**
- Title: "Health Check Fatal"
- Text: "Device TestDevice health check FATAL"
- Icon: Critical Error ❌

---

### Scenario 7: Recovery

**Steps:**
1. With device in CRITICAL or FATAL state
2. Restart test edge device (Terminal 1)
3. Wait for next health check (max 10 seconds)

**Expected Results:**
- ✅ Device icon returns to green (OK)
- ✅ Log shows successful health check
- ✅ Tooltip shows "Status: OK"
- ✅ Sliding window begins to clear failed checks

---

## Configuration Tuning

Edit `config.py` to adjust health monitoring behavior:

### Health Check Interval
```python
HEALTH_CHECK_ROUND_ROBIN_INTERVAL = 10.0  # Seconds between checks
```
- **Lower** = More frequent checks, faster error detection
- **Higher** = Less network traffic, slower detection

### Timeout Duration
```python
HEALTH_CHECK_TIMEOUT = 1.0  # Seconds waiting for PONG
```
- **Lower** = Stricter timeout, may cause false positives
- **Higher** = More tolerant, may miss real issues

### Sliding Window Size
```python
HEALTH_CHECK_WINDOW_SIZE = 10  # Number of recent checks tracked
```
- **Smaller** = Faster reaction to issues, more sensitive
- **Larger** = More stable, averages out transient issues

### Fatal Threshold
```python
HEALTH_CHECK_FATAL_THRESHOLD = 3  # Failures needed for FATAL
```
- **Lower** = More aggressive error escalation
- **Higher** = More tolerant of transient failures

### Slow Response Threshold
```python
HEALTH_CHECK_SLOW_THRESHOLD_MS = 500  # Milliseconds
```
- **Lower** = Stricter performance monitoring
- **Higher** = More tolerant of network delays

---

## Advanced Testing

### Test with Multiple Devices

Start multiple test devices on different ports:

**Terminal 1:**
```powershell
python test_edge_device.py --port 5000
```

**Terminal 2:**
```powershell
python test_edge_device.py --port 5001
```

**Terminal 3:**
```powershell
python test_edge_device.py --port 5002
```

Update `data/servers.json` with all three devices.

**Expected:** Round-robin health checks cycle through all devices.

---

### Test Custom Metrics

Modify test_edge_device.py to add custom metrics:

```python
def handle_ping(self, message):
    # ... existing code ...
    
    # Add custom metrics
    for metric in requested_metrics:
        if metric == 'custom_sensor':
            metrics['custom_sensor'] = self.read_custom_sensor()
        elif metric == 'battery_level':
            metrics['battery_level'] = self.get_battery_level()
```

Update server config to request custom metrics:
```json
{
  "health_metrics": ["uptime", "temperature", "custom_sensor", "battery_level"]
}
```

---

## Troubleshooting

### Issue: No PING messages received by edge device

**Symptoms:** Terminal 1 shows no PING messages

**Check:**
1. `config.py`: `HEALTH_CHECK_ENABLED = True`
2. Device is selected in UDPServerManager
3. Correct IP:Port in `data/servers.json`
4. Firewall not blocking UDP traffic
5. Log shows: `[HealthMonitor] Registered worker: TestDevice`

---

### Issue: Edge device responds but health check fails

**Symptoms:** Terminal 1 shows PONG sent, but UDPServerManager shows timeout

**Check:**
1. Response format: Must be `PONG:timestamp:metrics`
2. Timestamp matches PING timestamp exactly
3. No extra whitespace or line breaks
4. Network firewall allows return path
5. UDPServerManager socket listening on correct port

---

### Issue: "Check Health" button missing

**Check:**
1. `config.py`: `HEALTH_CHECK_ENABLED = True`
2. Application restarted after config change
3. Device selected from device panel
4. No import errors in console

---

### Issue: Icon not changing color

**Check:**
1. `update_health_status()` method exists in `device_panel.py`
2. Signal connection in `gui.py`: `health_status_updated.connect(...)`
3. Server name in config matches name in health status update
4. Status icons exist for all colors (green, yellow, red)

---

## Production Deployment

### Ready to Deploy? Checklist:

- [ ] All test scenarios pass
- [ ] Configuration tuned for your network
- [ ] Edge devices implement PING/PONG handling
- [ ] Firewall rules configured for UDP traffic
- [ ] Health check interval appropriate for your needs
- [ ] Fatal threshold tested and verified
- [ ] Documentation updated for your edge devices
- [ ] Monitoring/logging configured for escalations

### Edge Device Implementation

For real edge devices, add PING/PONG handling:

```python
def handle_udp_message(message):
    """Handle incoming UDP message."""
    
    # PRIORITY 1: Health Check PING
    if message.startswith('PING:'):
        handle_ping_message(message)
        return
    
    # PRIORITY 2: Regular commands
    # ... your existing command handling ...

def handle_ping_message(message):
    """Handle PING and respond with PONG."""
    try:
        parts = message.split(':', 2)
        ping_timestamp = parts[1]
        requested_metrics = parts[2].split(',') if len(parts) >= 3 else []
        
        # Collect metrics
        metrics = {}
        for metric in requested_metrics:
            metrics[metric] = get_metric_value(metric)
        
        # Format PONG
        metrics_str = ','.join([f"{k}={v}" for k, v in metrics.items()])
        pong_message = f"PONG:{ping_timestamp}:{metrics_str}"
        
        # Send response
        send_udp_response(pong_message)
        
    except Exception as e:
        print(f"Error handling PING: {e}")
```

---

## Next Steps

1. ✅ **Phase 1 Complete:** Health monitoring disabled, no regression
2. ✅ **Phase 2 Complete:** Test edge device implements PING/PONG
3. ⏭️ **Phase 3:** Enable health monitoring and run all test scenarios
4. ⏭️ **Phase 4:** Tune configuration based on test results
5. ⏭️ **Phase 5:** Implement PING/PONG in real edge devices
6. ⏭️ **Phase 6:** Production deployment

---

## Summary

v2.01 Health Monitor is now fully implemented and ready for testing!

**Testing Command Summary:**

```powershell
# Terminal 1 - Start test edge device
python test_edge_device.py --port 5000

# Terminal 2 - Start UDPServerManager
python main.py
```

**Test Sequence:**
1. Test with health monitoring disabled ✅
2. Test with health monitoring enabled ✅
3. Test manual health check ✅
4. Test slow response warning ⚠️
5. Test critical failure 🟠
6. Test fatal escalation 🔴
7. Test recovery ✅

All tests should pass before production deployment!

# Live Video Streaming Feature Roadmap

## Overview
This document outlines the planned implementation of live video streaming capabilities for the generic worker application when deployed on Raspberry Pi 4B devices.

## Current Implementation (Phase 1)

### Supported Features
- ✅ Local video file playback (MP4, AVI, MOV)
- ✅ Basic network stream support (HTTP, HTTPS, RTSP URLs)
- ✅ Video playback controls (Play, Pause, Stop)
- ✅ Seekable timeline with time display
- ✅ Static image display with aspect ratio preservation

### Current Limitations
- No stream health monitoring
- No automatic reconnection on connection loss
- No buffering indicators
- No network quality metrics
- Single video source only

## Future Implementation (Raspberry Pi 4B Phase)

### Hardware Support

#### Raspberry Pi 4B
- **Camera Modules:**
  - Pi Camera Module v2 (8MP)
  - Pi Camera Module v3 (12MP, HDR)
  - Pi HQ Camera (12.3MP)
  - USB webcams

- **Network:**
  - Gigabit Ethernet
  - Dual-band WiFi (2.4GHz/5GHz)
  - Multiple simultaneous streams

### Planned Features

#### 1. Live Streaming Sources
- **Pi Camera Direct Streaming**
  - Native V4L2 capture
  - Hardware H.264 encoding
  - Low-latency streaming (< 200ms)
  
- **Network Stream Support**
  - RTSP (Real Time Streaming Protocol)
  - HLS (HTTP Live Streaming)
  - WebRTC (ultra-low latency)
  - RTP/UDP custom streams
  - MJPEG streams

#### 2. Stream Management

**Connection Handling:**
```python
# Auto-detect stream type and protocol
stream_manager.connect(url='http://pi4b.local:8080/stream')

# Manual protocol specification
stream_manager.connect(
    url='192.168.1.50:8554/live',
    protocol='rtsp',
    codec='h264',
    resolution='1920x1080',
    framerate=30
)
```

**Health Monitoring:**
- Connection status (connected, buffering, error)
- Network latency (ms)
- Bandwidth usage (Mbps)
- Dropped frame counter
- Buffer health status

**Auto-Reconnection:**
- Automatic retry on connection loss
- Configurable retry interval and max attempts
- Fallback to alternative stream sources
- Connection state callbacks

#### 3. Quality Management

**Adaptive Streaming:**
- Automatic quality adjustment based on bandwidth
- Manual quality override (240p, 480p, 720p, 1080p)
- Dynamic resolution switching

**Network Optimization:**
- Buffer size configuration
- Jitter buffer management
- Packet loss recovery (FEC)
- QoS prioritization

#### 4. Multi-Camera Support

**Feature Set:**
- Picture-in-Picture (PiP) mode
- Side-by-side dual camera view
- Grid layout (2x2, 3x3)
- Switchable camera sources
- Synchronized multi-camera recording

**Example Usage:**
```python
# Configure multi-camera layout
status_panel.set_camera_layout('grid_2x2')

# Add multiple streams
status_panel.add_camera_stream(
    camera_id='cam1',
    url='http://pi4b-1.local/stream',
    position='top_left'
)
status_panel.add_camera_stream(
    camera_id='cam2',
    url='rtsp://pi4b-2.local:8554/live',
    position='top_right'
)
```

#### 5. Recording & Playback

**Capabilities:**
- Start/stop recording from live stream
- Timestamped video files
- Configurable format (MP4, MKV)
- Compression settings
- Storage location management
- Playback of recorded streams

#### 6. Overlay & Annotations

**Visual Enhancements:**
- Timestamp overlay
- Device status text
- Custom text/graphics overlay
- Bounding boxes for object tracking
- Grid overlays
- Crosshairs/reticles

#### 7. Advanced Controls

**Camera Control (Pi Camera):**
- Brightness, contrast, saturation
- Exposure control (auto/manual)
- White balance
- Focus (if supported by camera)
- Digital zoom
- Rotation and flip

**Stream Control:**
- Resolution selection
- Frame rate adjustment
- Bitrate control
- Codec selection (H.264, H.265, VP9)

### Implementation Architecture

```
┌─────────────────────────────────────────┐
│         Main Application (PC)           │
│  ┌─────────────────────────────────┐   │
│  │      Status Panel (UI)          │   │
│  │  ┌──────────┐  ┌─────────────┐ │   │
│  │  │  Video   │  │   Stream    │ │   │
│  │  │  Widget  │  │  Controls   │ │   │
│  │  └──────────┘  └─────────────┘ │   │
│  └─────────────────────────────────┘   │
│              ↕ Network Stream           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    Raspberry Pi 4B (Edge Device)        │
│  ┌─────────────────────────────────┐   │
│  │   Video Streaming Server        │   │
│  │  - Pi Camera Interface          │   │
│  │  - Hardware H.264 Encoder       │   │
│  │  - RTSP/HTTP/WebRTC Server      │   │
│  │  - Stream Manager               │   │
│  └─────────────────────────────────┘   │
│              ↑                          │
│      ┌───────────────┐                 │
│      │  Pi Camera    │                 │
│      │  Module v3    │                 │
│      └───────────────┘                 │
└─────────────────────────────────────────┘
```

### API Design (Placeholder)

```python
# Stream connection with full configuration
main_window.connect_live_stream(
    stream_url='http://192.168.1.50:8080/stream',
    protocol='http',
    options={
        'auto_reconnect': True,
        'reconnect_interval': 5,  # seconds
        'max_retries': 10,
        'buffer_size': 2048,      # KB
        'quality_auto': True,
        'preferred_resolution': '1280x720',
        'preferred_fps': 30
    }
)

# Monitor stream health
status = main_window.get_stream_quality()
# Returns:
# {
#     'connected': True,
#     'latency_ms': 45,
#     'bandwidth_mbps': 3.2,
#     'dropped_frames': 12,
#     'buffer_health': 'good',
#     'resolution': '1280x720',
#     'fps': 28.5,
#     'codec': 'h264'
# }

# Stream event callbacks
def on_stream_connected():
    print("Stream connected successfully")

def on_stream_error(error):
    print(f"Stream error: {error}")

def on_stream_quality_changed(quality):
    print(f"Stream quality changed to {quality}p")

status_panel.stream_connected.connect(on_stream_connected)
status_panel.stream_error.connect(on_stream_error)
status_panel.quality_changed.connect(on_stream_quality_changed)
```

## Development Timeline

### Phase 1: Current (Complete)
- ✅ Basic video playback infrastructure
- ✅ Local file support
- ✅ Basic URL streaming

### Phase 2: Raspberry Pi 4B Integration (Future)
- 🔲 Pi Camera module support
- 🔲 Hardware encoding setup
- 🔲 RTSP server implementation
- 🔲 WebRTC integration

### Phase 3: Stream Management (Future)
- 🔲 Health monitoring
- 🔲 Auto-reconnection logic
- 🔲 Quality adaptation
- 🔲 Multi-stream support

### Phase 4: Advanced Features (Future)
- 🔲 Recording capabilities
- 🔲 Overlay support
- 🔲 Multi-camera layouts
- 🔲 Advanced camera controls

## Testing Requirements

### Unit Tests
- Stream connection/disconnection
- Protocol detection
- Error handling
- Reconnection logic

### Integration Tests
- Pi Camera capture
- Hardware encoding
- Network streaming
- Multi-device communication

### Performance Tests
- Latency measurements
- Bandwidth optimization
- Frame drop analysis
- CPU/GPU usage monitoring

## Dependencies (Future)

### Raspberry Pi Side
- `picamera2` - Pi Camera interface
- `ffmpeg` - Video encoding/streaming
- `gstreamer` - Media pipeline
- `uvicorn` or `flask` - HTTP server

### PC Application Side
- `PySide6.QtMultimedia` - Already integrated
- Optional: `opencv-python` for advanced processing
- Optional: `aiortc` for WebRTC support

## Configuration Examples

### Stream Server Configuration (Pi 4B)
```yaml
# stream_config.yaml
camera:
  resolution: [1920, 1080]
  framerate: 30
  format: 'h264'
  bitrate: 2000000  # 2 Mbps

server:
  protocol: 'rtsp'
  port: 8554
  path: '/live'
  
network:
  buffer_size: 2048
  latency_mode: 'low'
  
monitoring:
  enable: true
  health_check_interval: 5
```

### Client Configuration (PC)
```yaml
# client_config.yaml
stream:
  auto_connect: false
  preferred_protocol: 'rtsp'
  auto_quality: true
  
reconnection:
  enabled: true
  max_attempts: 10
  retry_interval: 5
  
display:
  aspect_ratio: '16:9'
  deinterlace: false
  hardware_acceleration: true
```

## Notes

- Current implementation provides foundation for future streaming features
- Qt Multimedia framework already supports most required protocols
- Focus on reliability and low latency for industrial applications
- Consider network security (encryption, authentication) for production deployment
- Performance optimization critical for real-time operations

## Contact & Support

For questions regarding live streaming implementation:
- See: `docs/architecture.md` for system architecture
- See: `docs/contributing.md` for development guidelines
- Raspberry Pi 4B integration planned for Q2 2026

---
*Last Updated: February 19, 2026*

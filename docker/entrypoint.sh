#!/bin/bash
set -e

# Display
DISPLAY=:0
export DISPLAY

# Start Xorg dummy server to provide GLX-capable display
Xorg :0 -config /etc/X11/xorg.conf -noreset +extension GLX +extension RENDER &
XORG_PID=$!
sleep 2

# Start a lightweight window manager
fluxbox &

# Start a terminal so user can see something (optional)
# xterm &

# Start x11vnc to serve the X display
x11vnc -display $DISPLAY -forever -nopw -shared -rfbport 5900 &
X11VNC_PID=$!

# Start noVNC's websockify proxy (uses bundled websockify)
# novnc's novnc_proxy script expects websockify under utils, we'll use it directly
/opt/noVNC/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &
NOVNC_PID=$!

# Wait a moment for services to come up
sleep 1

# Print connection info
echo "noVNC running on http://0.0.0.0:6080/"
echo "Open in your browser: http://localhost:6080/vnc.html?host=localhost&port=6080"

# Optionally start a visible terminal on the virtual display
if command -v xterm >/dev/null 2>&1; then
	DISPLAY=$DISPLAY xterm -geometry 120x30+10+10 &
fi

conda init 
source /root/.bashrc
# Try to start L-Py GUI if available (don't fail the entrypoint if it isn't)
if [ -x "/opt/conda/bin/conda" ]; then
	/opt/conda/bin/conda run -n lpy --no-capture-output lpy >/tmp/lpy.log 2>&1 || true
fi

# Ensure we keep the container alive: trap signals and wait on background PIDs
cleanup() {
	echo "Shutting down..."
	kill "${XORG_PID}" "${X11VNC_PID}" "${NOVNC_PID}" 2>/dev/null || true
	wait 2>/dev/null || true
}
trap cleanup SIGINT SIGTERM EXIT

# Wait forever (until a signal) while background services run
while true; do
	sleep 1
done

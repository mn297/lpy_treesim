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

# Source conda to allow activation in xterm (useful for interactive shells)
if [ -f /opt/conda/etc/profile.d/conda.sh ]; then
	. /opt/conda/etc/profile.d/conda.sh
fi

# Install the package in editable mode from mounted /app (if pyproject.toml exists)
if [ -f /app/pyproject.toml ]; then
    /opt/conda/bin/conda run -n lpy --no-capture-output pip install -e /app || true
fi

# Ensure non-login shells still source the root .bashrc if needed
export BASH_ENV=/root/.bashrc

# Optionally start a visible terminal on the virtual display and activate
# the 'lpy' environment in it so the user gets an interactive shell already
# set up for LPy usage.
if command -v xterm >/dev/null 2>&1; then
	# Start a visible terminal that runs the helper script /usr/local/bin/enter-lpy
	# that activates the conda env and starts an interactive bash session.
	if [ -x /usr/local/bin/enter-lpy ]; then
		# Use -ls to ensure the shell runs as a login shell and sources /etc/profile
		DISPLAY=$DISPLAY xterm -ls -geometry 120x30+10+10 -e "/usr/local/bin/enter-lpy" &
	else
		DISPLAY=$DISPLAY xterm -ls -geometry 120x30+10+10 -e "bash -lc '. /opt/conda/etc/profile.d/conda.sh && conda activate lpy && exec bash -i'" &
	fi
fi

# Try to start L-Py GUI if available (don't fail the entrypoint if it isn't)
if command -v /opt/conda/bin/conda >/dev/null 2>&1; then
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

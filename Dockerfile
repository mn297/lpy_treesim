# Ubuntu 22.04 base
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages: build tools, X virtual framebuffer, VNC, window manager, OpenGL libs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget bzip2 ca-certificates git build-essential \
        x11vnc xserver-xorg xserver-xorg-core xserver-xorg-video-dummy fluxbox xterm supervisor procps \
        python3 python3-pip \
        libgl1-mesa-glx libglu1-mesa libgl1-mesa-dri mesa-utils \
        libx11-6 libx11-xcb1 libxcb1 libxext6 libxrender1 libxi6 libxrandr2 libxcursor1 libxfixes3 libxdamage1 libxcomposite1 libxss1 libsm6 libice6 \
        libpng16-16 libjpeg-turbo8 libfreetype6 libpango-1.0-0 \
        && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH=/opt/conda/bin:$PATH
SHELL ["/bin/bash", "-lc"]

# Ensure PATH contains the lpy conda env's bin directory by default
ENV PATH=/opt/conda/envs/lpy/bin:/opt/conda/bin:$PATH

# Force software GL renderer to avoid hardware/driver GL enum errors inside Xvfb
# ENV LIBGL_ALWAYS_SOFTWARE=1
# ENV MESA_LOADER_DRIVER_OVERRIDE=swrast
# ENV MESA_GL_VERSION_OVERRIDE=3.1

# Use only conda-forge and openalea channels to avoid Anaconda TOS prompts and incompatible defaults
RUN conda config --system --remove-key channels || true && \
    conda config --system --add channels fredboudon && \
    conda config --system --add channels conda-forge && \
    conda config --system --add channels defaults && \
    conda config --system --set channel_priority flexible
    
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Create environment; try python 3.8 if 3.9 is unavailable for OpenAlea packages
RUN conda create -n lpy openalea.lpy=3.14.1 python=3.10 -c fredboudon -c conda-forge && \
    # Ensure conda 'activate' works in bash shells started in the container
    /opt/conda/bin/conda init bash && \
    # Also ensure a reference to conda shell functions exists for non-login shells
    echo ". /opt/conda/etc/profile.d/conda.sh" >> /root/.bashrc && \
    # Append an idempotent auto-activation of the 'lpy' environment for interactive shells
    grep -qxF '# Auto-activate lpy for interactive shells' /root/.bashrc || printf '%s\n' '# Auto-activate lpy for interactive shells' 'if [ -n "$PS1" ]; then' '    if [ -f /opt/conda/etc/profile.d/conda.sh ]; then' '        . /opt/conda/etc/profile.d/conda.sh' '        conda activate lpy || true' '    fi' 'fi' >> /root/.bashrc && \

    # Also add a system-wide profile script to activate lpy for login shells
    printf '%s\n' '#!/bin/sh' '# Auto-activate lpy when login/interative shell starts' 'if [ -n "$PS1" ]; then' '  if [ -f /opt/conda/etc/profile.d/conda.sh ]; then' '    . /opt/conda/etc/profile.d/conda.sh' '    conda activate lpy >/dev/null 2>&1 || true' '  fi' 'fi' > /etc/profile.d/auto_activate_lpy.sh && \
    chmod +x /etc/profile.d/auto_activate_lpy.sh && \
    # Ensure login shells source /root/.bashrc for root so activation works for login shells
    echo "[ -f /root/.bashrc ] && . /root/.bashrc" >> /root/.bash_profile || true
    # conda clean -afy

# Install noVNC (web client) and websockify
RUN pip3 install websockify && \
    git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC && \
    git clone --depth 1 https://github.com/novnc/websockify /opt/noVNC/utils/websockify

# Create app dir and copy project
WORKDIR /app

# Note: For development, mount the local lpy_treesim directory to /app
# and install in editable mode. For production, uncomment the lines below to clone and install.
# RUN git clone -b docker_refactor https://github.com/OSUrobotics/lpy_treesim.git
# RUN conda run -n lpy --no-capture-output pip install ./lpy_treesim

# Create a helper for starting an interactive shell pre-activated with the lpy env
RUN printf '%s\n' "#!/bin/bash" \
    "if [ -f /opt/conda/etc/profile.d/conda.sh ]; then" \
    "  . /opt/conda/etc/profile.d/conda.sh" \
    "fi" \
    "conda activate lpy >/dev/null 2>&1 || true" \
    "exec bash -i" > /usr/local/bin/enter-lpy && chmod +x /usr/local/bin/enter-lpy

# Wrap system xterm to default to a login xterm with the lpy environment activated
RUN if [ -x /usr/bin/xterm ]; then \
            mv /usr/bin/xterm /usr/bin/xterm.bin; \
            printf '%s\n' '#!/bin/bash' 'for arg in "$@"; do' '    if [ "$arg" = "-e" ]; then' '        exec /usr/bin/xterm.bin "$@"' '    fi' 'done' 'exec /usr/bin/xterm.bin -ls -e /usr/local/bin/enter-lpy "$@"' > /usr/bin/xterm; \
            chmod +x /usr/bin/xterm; \
        fi


# Add an entrypoint script
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Provide a minimal Xorg dummy configuration to enable GLX on :0
RUN mkdir -p /etc/X11 && printf "Section \"Device\"\n    Identifier \"DummyDevice\"\n    Driver \"dummy\"\nEndSection\n\nSection \"Monitor\"\n    Identifier \"DummyMonitor\"\n    HorizSync 30-70\n    VertRefresh 50-75\nEndSection\n\nSection \"Screen\"\n    Identifier \"DummyScreen\"\n    Device \"DummyDevice\"\n    Monitor \"DummyMonitor\"\n    DefaultDepth 24\n    SubSection \"Display\"\n        Depth 24\n        Modes \"1920x1080\"\n    EndSubSection\nEndSection\n\nSection \"ServerLayout\"\n    Identifier \"DefaultLayout\"\n    Screen \"DummyScreen\"\nEndSection\n" > /etc/X11/xorg.conf

# Expose VNC and noVNC ports
EXPOSE 5900 6080

CMD ["/usr/local/bin/entrypoint.sh"]
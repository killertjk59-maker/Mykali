FROM kalilinux/kali-rolling
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv nmap sherlock whois dnsutils curl git \
    netcat-openbsd traceroute iputils-ping whatweb nano ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir python-telegram-bot==21.6
WORKDIR /work
COPY bot.py /opt/bot.py
CMD ["/opt/venv/bin/python", "/opt/bot.py"]

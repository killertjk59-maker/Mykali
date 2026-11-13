FROM kalilinux/kali-rolling
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv python3-pip \
    nmap sherlock whois dnsutils whatweb gobuster nikto hydra theharvester \
    sqlmap dirb dnsrecon sslscan john ffuf \
    curl wget git netcat-openbsd traceroute iputils-ping \
    smbclient jq nano vim-tiny unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir python-telegram-bot
WORKDIR /work
COPY bot.py /opt/bot.py
CMD ["/opt/venv/bin/python", "/opt/bot.py"]

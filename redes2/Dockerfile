# Dockerfile único para servidores e cliente
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    iputils-ping \
    net-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install matplotlib numpy

WORKDIR /app

COPY server_seq.py server_concurrent.py client_http.py metrics.py plot_results.py run_tests.sh /app/
COPY index.html /app/

RUN chmod +x /app/run_tests.sh

EXPOSE 80 8081

CMD ["tail", "-f", "/dev/null"]

# Dockerfile único para servidores e cliente
FROM ubuntu:22.04

# Evita prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive

# Atualiza e instala Python e ferramentas
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    iputils-ping \
    net-tools \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala bibliotecas Python necessárias
RUN pip3 install matplotlib numpy

# Cria diretório da aplicação
WORKDIR /app

# Copia todos os arquivos Python e scripts
COPY server_seq.py server_concurrent.py client_http.py metrics.py plot_results.py run_tests.sh /app/
COPY index.html /app/

# Torna scripts executáveis
RUN chmod +x /app/run_tests.sh

# Expõe portas dos serviços
EXPOSE 80 8081

# Comando padrão (mantém container ativo)
CMD ["tail", "-f", "/dev/null"]

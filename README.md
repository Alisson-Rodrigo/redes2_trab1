# Servidores HTTP: Sequencial vs Concorrente

Implementação e comparação de desempenho entre servidor HTTP sequencial e concorrente em Python, com testes automatizados usando Docker.

## Descrição

O projeto implementa dois servidores HTTP:
- **Sequencial**: Processa requisições uma por vez
- **Concorrente**: Usa threads para processar requisições simultaneamente

Ambos suportam os métodos GET, POST, PUT e DELETE com cabeçalhos CORS e Custom ID baseado em hash MD5.

## Requisitos

- Docker Desktop instalado e rodando
- Git Bash (Windows) ou terminal padrão (Linux/Mac)

## Execução

Para executar o projeto completo:

No terminal do git bash:

```bash
bash main.sh #comando
```

Este comando automaticamente:
1. Limpa ambientes anteriores
2. Constrói as imagens Docker
3. Inicia os containers
4. Executa testes de performance em ambos servidores
5. Gera gráficos comparativos
6. Salva resultados em `./results/`

## Acessos

Após execução:
- Dashboard Web: `http://localhost:8081`
- Servidor Sequencial: `http://localhost:8080`
- Servidor Concorrente: `http://localhost:8082`

## Estrutura dos Containers

| Container | IP | Porta |
|-----------|------------|-------|
| servidor_sequencial | 54.99.0.10 | 8080 |
| servidor_concorrente | 54.99.0.11 | 8082 |
| cliente | 54.99.0.20 | 8081 |

## Resultados

Os resultados são salvos automaticamente em:
- `./results/results.csv` - Métricas detalhadas (tempo médio, desvio padrão, throughput)
- `./results/graph.png` - Gráficos comparativos

## Comandos Adicionais

Ver logs:
```bash
docker-compose logs servidor_sequencial
docker-compose logs servidor_concorrente
```

Parar containers:
```bash
docker-compose down
```

Executar testes manualmente:
```bash
docker exec cliente python3 /app/metrics.py 54.99.0.10 sequencial 10
docker exec cliente python3 /app/metrics.py 54.99.0.11 concorrente 10
```

## Estrutura do Projeto

```
.
├── server_seq.py           # Servidor sequencial
├── server_concurrent.py    # Servidor concorrente
├── metrics.py              # Script de testes de performance
├── plot_results.py         # Geração de gráficos
├── index.html              # Dashboard web
├── docker-compose.yml      # Configuração dos containers
├── Dockerfile              # Imagem base
├── main.sh                 # Script principal
└── results/                # Resultados dos testes
```

FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3  \
    python3-dev  \
    python3-venv  \
    python3-pip \
    && pip install wheel  \
    && pip install neon-api-proxy

WORKDIR /config

ENV NEON_API_PROXY_CONFIG_PATH /config/config.json
ENV NEON_MQ_PROXY_CONFIG_PATH /config/config.json

CMD ["neon_api_proxy"]
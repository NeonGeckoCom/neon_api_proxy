FROM python:3.10-slim

LABEL vendor=neon.ai \
    ai.neon.name="neon-api-proxy"

ENV OVOS_CONFIG_BASE_FOLDER=neon
ENV OVOS_CONFIG_FILENAME=diana.yaml
ENV OVOS_DEFAULT_CONFIG=/opt/neon/diana.yaml
ENV XDG_CONFIG_HOME=/config
ENV HEALTHCHECK_PORT=8000

COPY docker_overlay/ /

RUN apt-get update && \
    apt-get install -y \
    gcc \
    curl \
    jq \
    python3  \
    python3-dev  \
    && pip install wheel

COPY . /neon_api_proxy
WORKDIR /neon_api_proxy
RUN pip install --no-cache-dir .

HEALTHCHECK CMD "/opt/neon/healthcheck.sh"
CMD ["neon_api_proxy"]

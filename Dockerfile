FROM python:3.8

ADD . /neon_api_proxy
WORKDIR /neon_api_proxy
RUN apt-get update && \
    apt-get install -y \
    gcc \
    python3  \
    python3-dev  \
    && pip install wheel  \
    && pip install .

ENV NEON_CONFIG_PATH /config

# TODO: Deprecate below after updating to neon_mq_connector 0.2.0+ DM
ENV NEON_MQ_CONFIG_PATH /config/config.json

# TODO: Deprecate below after updating to ngi_auth_vars internally
ENV NEON_API_PROXY_CONFIG_PATH /config/config.json

CMD ["neon_api_proxy"]
FROM ghcr.io/aperion/base:aperion-builder AS builder

COPY ./requirements*.txt ./

RUN --mount=type=cache,id=pip,target=/root/.cache/pip set -eux; \
    python -m venv ./.venv/; \
    . ./.venv/bin/activate; \
    pip install -r ./requirements.txt -r ./requirements-server.txt

COPY ./aperion/ ./aperion/

ARG TIMESTAMP_SETTINGS="0"

RUN set -eux; \
    python -m compileall -q ./aperion/; \
    touch -c --date=@$TIMESTAMP_SETTINGS ./aperion/settings.yml; \
    find ./aperion/static/ -type f \
        \( -name "*.html" -o -name "*.css" -o -name "*.js" -o -name "*.svg" \) \
        -exec gzip -9 -k {} + \
        -exec brotli -9 -k {} + \
        -exec gzip --test {}.gz + \
        -exec brotli --test {}.br +; \
    # Move always changing files to /usr/local/aperion/
    mv ./aperion/version_frozen.py ./

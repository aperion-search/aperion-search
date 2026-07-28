FROM ghcr.io/aperion/base:aperion AS dist

ARG CONTAINER_IMAGE_ORGANIZATION="aperion"
ARG CONTAINER_IMAGE_NAME="aperion"

COPY --chown=aperion:aperion --from=localhost/$CONTAINER_IMAGE_ORGANIZATION/$CONTAINER_IMAGE_NAME:builder /usr/local/aperion/.venv/ ./.venv/
COPY --chown=aperion:aperion --from=localhost/$CONTAINER_IMAGE_ORGANIZATION/$CONTAINER_IMAGE_NAME:builder /usr/local/aperion/aperion/ ./aperion/
COPY --chown=aperion:aperion ./container/ ./
COPY --chown=aperion:aperion --from=localhost/$CONTAINER_IMAGE_ORGANIZATION/$CONTAINER_IMAGE_NAME:builder /usr/local/aperion/version_frozen.py ./aperion/

ARG CREATED="0001-01-01T00:00:00Z"
ARG VERSION="unknown"
ARG VCS_URL="unknown"
ARG VCS_REVISION="unknown"

LABEL org.opencontainers.image.created="$CREATED" \
      org.opencontainers.image.description="aperion is a metasearch engine. Users are neither tracked nor profiled." \
      org.opencontainers.image.documentation="https://docs.aperion.org/admin/installation-docker" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later" \
      org.opencontainers.image.revision="$VCS_REVISION" \
      org.opencontainers.image.source="$VCS_URL" \
      org.opencontainers.image.title="aperion" \
      org.opencontainers.image.url="https://aperion.org" \
      org.opencontainers.image.version="$VERSION"

ENV aperion_VERSION="$VERSION" \
    aperion_SETTINGS_PATH="$CONFIG_PATH/settings.yml" \
    GRANIAN_PROCESS_NAME="aperion" \
    GRANIAN_INTERFACE="wsgi" \
    GRANIAN_HOST="::" \
    GRANIAN_PORT="8080" \
    GRANIAN_WEBSOCKETS="false" \
    GRANIAN_LOOP="uvloop" \
    GRANIAN_BLOCKING_THREADS="4" \
    GRANIAN_WORKERS_KILL_TIMEOUT="30s" \
    GRANIAN_BLOCKING_THREADS_IDLE_TIMEOUT="5m"

# "*_PATH" ENVs are defined in base images
VOLUME $CONFIG_PATH
VOLUME $DATA_PATH

EXPOSE 8080

ENTRYPOINT ["/usr/local/aperion/entrypoint.sh"]

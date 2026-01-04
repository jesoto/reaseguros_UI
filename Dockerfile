ARG BASE_IMAGE=python:3.9
FROM ${BASE_IMAGE} as runtime-environment

# Install dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install -U pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

# Add non-root user
ARG APP_UID=999
ARG APP_GID=0
RUN groupadd -f -g ${APP_GID} app_group && \
    useradd -m -d /app -s /bin/bash -g ${APP_GID} -u ${APP_UID} app_user

WORKDIR /app

# Install custom component
COPY . .
WORKDIR /app/src/components/streamlit-recaptcha/
RUN pip install --no-cache-dir -e .

# Return to the main directory
WORKDIR /app
USER app_user

FROM runtime-environment
ARG APP_UID=999
ARG APP_GID=0
COPY --chown=${APP_UID}:${APP_GID} . .

EXPOSE 8080
ENTRYPOINT ["streamlit", "run", "src/app.py", "--server.port=8080", "--server.address=0.0.0.0"]
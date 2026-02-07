# === STAGE 1: BUILDER (For installing uv and resolving/installing dependencies) ===
FROM python:3.11-slim as builder
#USER root

# 1. Install uv as a standalone, fast package manager
#    We use pipx to install it outside of the main environment
ENV PATH="/root/.local/bin:$PATH"
RUN pip install --upgrade pip \
  && pip install --no-cache-dir pipx \
  && pipx install uv

#.. install vim for quick edits directly on the image
RUN apt-get update && apt-get install -y --no-install-recommends vim-tiny \
  && rm -rf /var/lib/apt/lists/*

# 2. Set the working directory for the application
WORKDIR /app


# 4. Use uv to create the production environment and install required modules
#    'uv venv' creates the venv; 'uv pip sync' installs locked dependencies fast
RUN uv venv --system-site-packages .venv && \
    . .venv/bin/activate && \
    uv pip install webpie pythreader jinja2 \
    uv clean

# 6. copy local files as needed
WORKDIR /root

ADD start.sh ./start.sh
RUN mkdir app samples
ADD app ./app


# === STAGE 2: RUNNER (The minimal, clean production image) ===
FROM python:3.11-slim as runner

# 1. Set the working directory
WORKDIR /app

# 2. Copy the *clean virtual environment* and application files from the builder stage
#    This drastically reduces the size of the final image by excluding build tools and cache
COPY --from=builder /app /app
#COPY --from=builder /app/.venv /app/.venv

ADD start.sh ./start.sh
RUN mkdir -p /var/cache/consistency-dump /var/cache/consistency-temp /reports/unmerged
ADD app ./app
ADD reports /reports
COPY --from=builder /usr/bin/vi /usr/bin/vi

RUN chmod +x *.sh

# 3. Ensure the virtual environment is used
ENV PATH="/app/.venv/bin:$PATH"

# 4. Define how the container starts
EXPOSE 8400
#ENTRYPOINT ["/app/start.sh"]
CMD ["/app/start.sh"]

# 5. Use /bin/bash --login to ensure the PATH is correctly initialized.
#CMD [ "/bin/bash", "--login" ]

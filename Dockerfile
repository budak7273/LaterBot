FROM python:3.13.1-slim as runner

# Create app user and working directory
RUN useradd --create-home appuser
WORKDIR /home/appuser/app

# Install system deps needed by some wheels
# Git is required to use some specific versions of packages in requirements.txt
RUN apt-get update \
    # && apt-get install -y --no-install-recommends build-essential libpq-dev git \
    && apt-get install -y --no-install-recommends git \
    # Clean up apt-get update files to reduce image size
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy project requirements
COPY pyproject.toml requirements.txt ./

# Mount volume /data to hold the sqlite database file
VOLUME ["/data"]
# Make directory inside app/ to be symlinked to volume later
RUN mkdir /home/appuser/app/data/

# Instantly print any standard streams (container logs)
ENV PYTHONUNBUFFERED=1

# Install python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src ./src
COPY migrations ./migrations

# --------- Prepare to Run ---------

# The bot expects to run from the src/laterbot folder so the relative sqlite path works.
WORKDIR /home/appuser/app/

# Copy entrypoint script
COPY docker-entrypoint.sh /home/appuser/app/docker-entrypoint.sh
RUN chmod +x /home/appuser/app/docker-entrypoint.sh

# Make sure the app directory is owned by the non-root user so entrypoint script can modify it
RUN chown -R appuser:appuser /home/appuser/app

# Use a non-root user for running
USER appuser

# Create a symlink for the DB file in /data and then exec the CMD
ENTRYPOINT ["/home/appuser/app/docker-entrypoint.sh"]
CMD ["python", "./src/laterbot"]

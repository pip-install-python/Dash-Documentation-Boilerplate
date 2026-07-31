FROM python:3.11.8-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        nodejs npm curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Update pip
RUN pip install --upgrade pip

# Install core dependencies explicitly (helps with dependency resolution)
RUN pip install pandas>=1.2.3 plotly>=5.0.0 pydantic>=2.3.0

# requirements.txt installs dash-improve-my-llms from ./vendor, so the vendored
# sdist has to be in the image BEFORE the install layer — otherwise the build
# fails on a path that only appears with the final `COPY . .`. Drop this line
# when the package moves back to PyPI.
COPY vendor/ ./vendor/
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install node dependencies
COPY package.json ./
RUN npm install

COPY . .

# The 2plot.ai hub's hourly sweep probes /healthz; give the container the same
# check so an unhealthy process is visible to the orchestrator too.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8550/healthz || exit 1

EXPOSE 8550
CMD ["gunicorn", "run:server", "-b", "0.0.0.0:8550"]

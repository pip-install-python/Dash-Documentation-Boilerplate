FROM python:3.11.8-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        nodejs npm curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Update pip
RUN pip install --upgrade pip

# Install core dependencies explicitly (helps with dependency resolution)
RUN pip install pandas>=1.2.3 plotly>=5.0.0 pydantic>=2.3.0

# dash-improve-my-llms installs from PyPI. vendor/ still holds dash_clerk_auth
# (not on PyPI, deliberately outside requirements.txt) so the optional-auth
# install command in docs/authentication works inside the image.
COPY vendor/ ./vendor/
COPY requirements.txt .
RUN pip install -r requirements.txt
# markdown2dash pins gunicorn<22, conflicting with the CVE-driven gunicorn>=23
# in requirements.txt (CVE-2024-6827, CVE-2024-1135 — request smuggling). Its
# real dependencies are all in requirements.txt already, so it is installed
# alone, without letting pip see the spurious pin. CI asserts the resulting
# gunicorn version inside this image, which is what keeps the dodge honest.
RUN pip install --no-deps markdown2dash==0.1.2

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

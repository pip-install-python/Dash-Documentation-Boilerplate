FROM python:3.11.8-slim

# Unbuffered stdout, or none of the app's print() diagnostics ever reach the
# platform logs: Python block-buffers stdout when it is not a tty, so the
# boot lines this template relies on for observability ([auth] state, the
# interactive-gate summary, [satellite-traffic]/[satellite-presence] wiring)
# sat invisible in Render while logging-based lines sailed through on
# stderr. An entire misconfiguration class debugs itself once these print.
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        nodejs npm curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Update pip
RUN pip install --upgrade pip

# Install core dependencies explicitly (helps with dependency resolution)
RUN pip install pandas>=1.2.3 plotly>=5.0.0 pydantic>=2.3.0

# dash-improve-my-llms installs from PyPI. vendor/ holds dash_clerk_auth
# (not on PyPI), which requirements.txt installs from this path as of 1.4.1 —
# so vendor/ MUST be copied before the requirements install. Auth stays
# gated at runtime: no CLERK_* keys, no login wall.
#
# CACHE SEMANTICS (the round-2 fleet lesson, found by pannellum
# 2026-08-22): this layer re-runs ONLY when vendor/ or requirements.txt
# bytes change. A `>=` floor can NEVER pull a newer release through a
# cache hit — a code-only commit rebuilds the app layers below while pip
# silently keeps whatever version the image was first built with. Ship
# every dependency upgrade as a floor bump in requirements.txt (grep the
# number — it also lives in run.py's boot floor and the tests): the bump
# IS the cache bust, and the boot floor turns a stale image from a
# silent downgrade into a loud refusal to start.
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

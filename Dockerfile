# MINOR tag on purpose — never a patch pin. `3.11.8-slim` sat here while the
# matrix said 3.12 and render.yaml said 3.12.0: three declared Pythons, none
# tested against the image, and the patch pin meant the image never received
# a 3.11.x security release either (ops-seat finding, 2026-08-25). The minor
# tag tracks patch releases through Docker Hub; the minor itself is the ONE
# fleet Python, and tests/test_python_version.py pins that this tag, the CI
# matrix main and render.yaml's PYTHON_VERSION all agree — while /healthz
# reports the serving interpreter so the wire can contradict a stale image.
FROM python:3.14-slim

# Unbuffered stdout, or none of the app's print() diagnostics ever reach the
# platform logs: Python block-buffers stdout when it is not a tty, so the
# boot lines this template relies on for observability ([auth] state, the
# interactive-gate summary, [satellite-traffic]/[satellite-presence] wiring)
# sat invisible in Render while logging-based lines sailed through on
# stderr. An entire misconfiguration class debugs itself once these print.
ENV PYTHONUNBUFFERED=1

# curl only — the HEALTHCHECK below uses it. Deliberately NO nodejs/npm:
# this image once apt-installed both to `npm install` a package.json that
# was dash-mantine-components' component-build toolchain, inherited through
# the fork lineage and used by NOTHING in this repo (no webpack config, no
# src/ts, no CI job, no served asset) — while shipping a known-vulnerable
# jsonpath into every production image in the fleet (issue #12,
# CVE-2026-1615). A docs site is a Python app; if a fork genuinely builds
# JS components it adds its own toolchain knowingly, not by inheritance.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
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

COPY . .

# The 2plot.ai hub's hourly sweep probes /healthz; give the container the same
# check so an unhealthy process is visible to the orchestrator too.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:${PORT:-8550}/healthz || exit 1

EXPOSE 8550
# Shell form on purpose: exec-form CMD never expands env, so the old
# ["gunicorn", ..., "0.0.0.0:8550"] hardcoded the port no matter what the
# platform asked for. run.py has honored $PORT since 1.6.8; the container
# lane didn't, and only worked on Render because Render port-detects.
# excalidraw fixed this fork-side in its gate-wave pass and rightly refused
# to regress it on template sync (floor round, 2026-08-23) — this makes the
# template agree with the fork instead of the other way around.
CMD gunicorn run:server -b 0.0.0.0:${PORT:-8550}

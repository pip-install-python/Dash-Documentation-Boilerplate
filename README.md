# Dash Documentation Boilerplate

> A modern, responsive documentation system for Dash applications built with Dash Mantine Components

[![Dash](https://img.shields.io/badge/Dash-4.2.0-blue.svg)](https://dash.plotly.com/)
[![DMC](https://img.shields.io/badge/DMC-2.7.0-teal.svg)](https://www.dash-mantine-components.com/)
[![Backends](https://img.shields.io/badge/Backends-Flask%20%7C%20FastAPI%20%7C%20Quart-orange.svg)](https://dash.plotly.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


A comprehensive boilerplate for creating beautiful, interactive documentation for your Dash components, data science workflows, and applications. Features markdown-driven content, live code examples, and automatic theme persistence.

![Documentation Preview](assets/intro_img.jpg)

---

## ✨ Features

### 📝 Markdown-Driven Documentation
- Write documentation in Markdown with Python integration
- Custom directives for interactive examples, code highlighting, and component props
- Automatic page generation from markdown files with frontmatter metadata
- Table of contents generation for easy navigation

### 🎨 Modern UI/UX
- Built with [Dash Mantine Components](https://www.dash-mantine-components.com/)
- Responsive design for mobile, tablet, and desktop
- Dark and light theme support with **automatic preference persistence**
- Smooth transitions and professional styling
- Customizable color schemes and theming

### 🔍 Developer Experience
- Hot reload during development
- Searchable component navigation
- Syntax highlighting for multiple languages
- Interactive code examples with live callbacks
- Component props documentation auto-generation

### 🤖 AI/LLM & SEO Integration
- **`LLMS_DOC` pattern** — write a module-level prose string per page; served verbatim at `/<page>/llms.txt`
- **Multi-backend** — `add_llms_routes(app)` auto-detects Flask, FastAPI, or Quart and dispatches to the matching adapter
- **MCP bridge** — each page's prose registers as a `dash.mcp` resource on Dash 4.3+ (silent no-op otherwise)
- **SEO** — `sitemap.xml` with intelligent priority inference; respects `mark_hidden()`
- **Bot management** — training crawlers blocked (configurable), AI search citations allowed, browsers untouched
- **Privacy controls** — `mark_hidden()` to exclude pages from sitemap, robots, MCP, and crawler prerender
- **Share with AI** — paste the app URL into ChatGPT/Claude/etc.; they fetch the prose docs directly
- Powered by [dash-improve-my-llms 2.0](https://pypi.org/project/dash-improve-my-llms/)

### 🔌 Pluggable Backends (Dash 4.x)
- Run the **same app** on **Flask**, **FastAPI**, or **Quart** — switch with a single `DASH_BACKEND` environment variable
- Backend selection centralized in [`lib/backend.py`](lib/backend.py); a live badge shows which backend is serving the page
- FastAPI/Quart (ASGI) unlock async callbacks, websocket callbacks, OpenAPI docs, a native JSON API (`/api/backend`, `/api/pages`, `/healthz`), and ASGI middleware
- Dedicated docs: **Pluggable Backends**, **Backend Deep Dive**, and a **FastAPI Showcase**

### 🐋 Production Ready
- Docker and docker-compose support
- Gunicorn (WSGI) and Uvicorn (ASGI) production servers
- Optimized for deployment
- Environment-based configuration

### 🚀 Built With Latest Technologies
- **Dash 4.2.0** - Modern Plotly Dash framework with pluggable backends
- **DMC 2.7.0** - Dash Mantine Components
- **Mantine 8.3.6** - Beautiful React UI library
- **React 18** - Latest React features
- **Python 3.11+** - Modern Python

---

## 📋 Requirements

### System Requirements
- **Python**: 3.11 or higher
- **Node.js**: 14+ (for npm dependencies)
- **npm**: 6+

### Python Dependencies
- dash >= 4.1.0
- dash-mantine-components >= 2.7.0
- dash-ag-grid
- dash-improve-my-llms[flask] >= 2.0.0
- flask >= 3.0.0 (default backend)
- plotly >= 5.0.0
- pandas >= 1.2.3
- pydantic >= 2.3.0
- python-frontmatter >= 1.0.0
- markdown2dash
- gunicorn >= 21.2.0 (WSGI production server)

**Optional backends** (install the matching extra to switch off Flask):
```bash
pip install "dash[fastapi]"   # FastAPI (ASGI) backend
pip install "dash[quart]"     # Quart (ASGI) backend
# then run with: DASH_BACKEND=fastapi python run.py  (needs uvicorn)
```

See [`requirements.txt`](requirements.txt) for the complete list.

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/pip-install-python/Dash-Documentation-Boilerplate.git
cd Dash-Documentation-Boilerplate
```

### 2. Install Dependencies

**Python packages:**
```bash
pip install -r requirements.txt
```

**Node packages** (for DMC frontend components):
```bash
npm install
```

### 3. Run the Development Server

```bash
python run.py
```

Visit **http://localhost:8553** in your browser.

### 4. Start Documenting!

Create your documentation in the `docs` folder:

```bash
docs/
├── your-component/
│   ├── your-component.md     # Markdown documentation
│   └── examples.py           # Python code examples (optional)
```

---

## 📁 Project Structure

```
dash-documentation-boilerplate/
├── assets/                      # Static assets and CSS
│   ├── m2d.css                 # Markdown-to-Dash styling (theme-aware)
│   ├── main.css                # Custom styles (theme-aware)
│   └── llms_copy.js            # "Copy for LLM" button handler
│
├── components/                  # Reusable UI components
│   ├── appshell.py             # Main app layout with MantineProvider
│   ├── header.py               # Header with search and theme toggle
│   ├── navbar.py               # Navigation sidebar and drawer
│   └── backend_badge.py        # Badge showing the active backend
│
├── docs/                        # Documentation content
│   ├── example/                # Getting Started guide
│   ├── directives/             # Custom Directives guide
│   ├── interactive-components/ # Callback patterns guide
│   ├── data-visualization/     # Theme-aware charts guide
│   ├── ai-integration/         # AI/LLM integration (dash-improve-my-llms 2.0)
│   ├── backends/               # Pluggable Backends guide
│   ├── backend-comparison/     # Flask vs FastAPI vs Quart deep dive
│   └── fastapi-showcase/       # What the FastAPI backend unlocks
│
├── lib/                         # Utility libraries
│   ├── constants.py            # App-wide constants (APP_VERSION, colors)
│   ├── backend.py              # Backend selection (DASH_BACKEND)
│   ├── asgi_middleware.py      # ASGI middleware (FastAPI/Quart)
│   ├── asgi_routes.py          # Showcase routes (/healthz, /api/*)
│   ├── analytics_tracker.py    # Lightweight visitor analytics
│   └── directives/             # Custom markdown directives
│       ├── kwargs.py           # Component props table generator
│       ├── source.py           # Source code display directive
│       ├── toc.py              # Table of contents directive
│       └── llms_copy.py        # "Copy for LLM" button directive
│
├── pages/                       # Dash multi-page app pages
│   ├── home.md                 # Home page content
│   ├── home.py                 # Home page layout (exports LLMS_DOC)
│   └── markdown.py             # Dynamic markdown page loader
│
├── templates/
│   └── index.html              # SEO-optimized HTML template
│
├── .gitignore
├── CHANGELOG.md                # Version history and changes
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Docker compose configuration
├── package.json                # Node.js dependencies
├── package-lock.json           # Locked npm versions
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── run.py                      # Application entry point
```

---

## 📖 Usage Guide

### Creating Documentation Pages

1. **Create a new folder** in the `docs/` directory:
   ```bash
   mkdir -p docs/my-component
   ```

2. **Create a markdown file** with frontmatter:
   ```markdown
   ---
   name: My Component
   description: A description of my component
   endpoint: /components/my-component
   icon: mdi:code-tags
   ---

   ## My Component

   Your documentation content here...
   ```

3. **Add interactive examples** (optional):
   ```python
   # docs/my-component/example.py
   import dash_mantine_components as dmc

   component = dmc.Button("Click Me!", id="my-button")
   ```

4. **Use directives** in your markdown:
   ```markdown
   .. toc::

   .. exec::docs.my-component.example

   .. source::docs/my-component/example.py
   ```

### Custom Markdown Directives

#### `.. toc::`
Generates a table of contents from your markdown headings.

#### `.. exec::module.path.to.component`
Renders an executable Python component from a module.

#### `.. source::path/to/file.py`
Displays source code with syntax highlighting.

#### `.. kwargs::ComponentName`
Generates a props documentation table for a component.

#### `.. llms_copy::Page Title`
Adds a "Copy for LLM" button that copies the page's `/<page>/llms.txt` URL to the clipboard for sharing with ChatGPT, Claude, and other AI assistants.

### Customizing Themes

Modify `lib/constants.py` to change the primary color:

```python
PRIMARY_COLOR = "teal"  # Change to any Mantine color
```

Customize CSS in:
- `assets/main.css` - General styling
- `assets/m2d.css` - Markdown-specific styling

### Theme Persistence

The boilerplate automatically saves user theme preference (light/dark) in localStorage:
- First visit: Detects browser preference or defaults to light
- Theme toggle: Saves preference automatically
- Return visits: Restores saved theme preference

---

## 🐳 Docker Deployment

### Build the Docker Image

```bash
docker build -t dash-docs-boilerplate .
```

### Run with Docker

```bash
docker run -p 8550:8550 dash-docs-boilerplate
```

Visit **http://localhost:8550**

### Using Docker Compose

```bash
docker-compose up
```

The app will be available at **http://localhost:8550**

### Production Deployment

The Docker container uses **Gunicorn** for production-ready serving:
- Multiple workers for better performance
- Automatic worker restart on failure
- Suitable for production environments

---

## 🛠️ Development

### Setting Up Development Environment

1. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. **Run in debug mode**:
   ```python
   # Modify run.py
   app.run(debug=True, host='0.0.0.0', port='8553')
   ```

### Adding New Components

1. Create your component in a separate module
2. Add documentation in `docs/your-component/`
3. The app automatically discovers and registers pages from markdown files
4. Restart the server to see your new documentation

### Modifying the Layout

Main layout components:
- **Header**: `components/header.py` - Logo, search, theme toggle
- **Navbar**: `components/navbar.py` - Sidebar navigation
- **AppShell**: `components/appshell.py` - Overall layout structure

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```env
DASH_DEBUG=False
DASH_HOST=0.0.0.0
DASH_PORT=8553
DASH_BACKEND=flask     # flask | fastapi | quart (requires the matching dash extra)
```

### Customization Points

| File | Purpose |
|------|---------|
| `lib/constants.py` | App-wide constants (colors, titles) |
| `assets/main.css` | Custom CSS styles |
| `templates/index.html` | HTML template (for analytics, meta tags) |
| `components/appshell.py` | Theme configuration, MantineProvider settings |

---

## 📚 Documentation

### User Documentation
- **Getting Started**: This README
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md)
- **Examples**: Check the `/docs/example/` folder

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**: Ensure the app runs without errors
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add docstrings to functions and classes
- Test your changes before submitting
- Update documentation if adding new features
- Keep commits atomic and well-described

---

## 🐛 Known Issues & Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'dash_html_components'`
- **Solution**: You're on an old version. Update to 1.0.0+ and import from the main package (`from dash import html, dcc`); 1.0.0 runs on Dash 4.x.

**Issue**: `DASH_BACKEND=fastapi` (or `quart`) fails to start
- **Solution**: Install the matching extra — `pip install "dash[fastapi]"` (or `[quart]`) — and serve with an ASGI server (`uvicorn`). The app falls back to Flask if the backend is unavailable.

**Issue**: Theme doesn't persist
- **Solution**: Check browser localStorage is enabled and not blocked

**Issue**: npm install fails
- **Solution**: Update Node.js to 14+ and npm to 6+

**Issue**: Port already in use
- **Solution**: Change port in `run.py` or stop the conflicting process

For more issues, check [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues)

---

## 📊 Version Information

**Current Version**: 1.0.0

| Component | Version |
|-----------|---------|
| Dash | 4.2.0 |
| Dash Mantine Components | 2.7.0+ |
| Mantine | 8.3.6 |
| Python | 3.11+ |
| React | 18.2.0 |
| Flask / FastAPI / Quart | pluggable backends |
| dash-improve-my-llms | 2.0.0+ |

See [CHANGELOG.md](CHANGELOG.md) for version history.

### What's New in 1.0.0

First stable release — a major architectural milestone:

- 🚀 **Dash 4.x (4.2.0)** and **DMC 2.7.0** — modern framework with pluggable backends.
- 🔌 **Pluggable backends**: run the same app on **Flask**, **FastAPI**, or **Quart** by setting `DASH_BACKEND` — no code changes. ASGI backends add async/websocket callbacks, OpenAPI docs, a native JSON API, and ASGI middleware. New **Pluggable Backends**, **Backend Deep Dive**, and **FastAPI Showcase** docs.
- 🎯 **dash-improve-my-llms 2.0**: the `LLMS_DOC` pattern (per-page prose served at `/<page>/llms.txt`), multi-backend AI/LLM surfaces, and an MCP resource bridge on Dash 4.3+.
- 🧹 **Removed the TOON format** entirely — `lib/toon_generator.py`, the TOON docs/dashboard, and `/llms.toon` routes are gone (the package no longer exports `TOONConfig`, `toon_encode`, `generate_*_toon`).
- ⚠️ **Removed `mark_important()` / `mark_component_hidden()`** (now no-ops) and the `/page.json` / `/architecture.txt` routes — Dash 4.3 MCP covers structured introspection. Write emphasis directly into a page's `LLMS_DOC` markdown.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Built With
- [Plotly Dash](https://dash.plotly.com/) - The web framework
- [Dash Mantine Components](https://www.dash-mantine-components.com/) - Beautiful UI components
- [Mantine](https://mantine.dev/) - React component library

### Inspired By
- [dmc-docs](https://github.com/snehilvj/dmc-docs) - Documentation framework inspiration

### Special Thanks
- [@AnnMarieW](https://github.com/AnnMarieW) for suggested improvements
- The Dash community for continuous support

---

## 📞 Support & Community

### Get Help
[![Discord Invite](https://img.shields.io/discord/396334922522165248?color=4A55CC&label=Discord&logo=discord&style=for-the-badge)](https://discord.gg/uwQ2f3KCad)

- **Documentation**: You're reading it!
- **Issues**: [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/discussions)
- **Dash Community**: [Plotly Community Forum](https://community.plotly.com/)

### Stay Connected

**GitHub**: [@pip-install-python](https://github.com/pip-install-python)
![GitHub Followers](https://img.shields.io/github/followers/pip-install-python?style=social)

**YouTube**: [Pip Install Python](https://www.youtube.com/channel/UC-pBvv8mzLpj0k-RIbc2Nog?sub_confirmation=1)
![YouTube Subscribers](https://img.shields.io/youtube/channel/subscribers/UC-pBvv8mzLpj0k-RIbc2Nog?style=social)

---

### Want to Contribute?
Check out open issues labeled [`good first issue`](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/labels/good%20first%20issue)

---

<div align="center">

**[⬆ Back to Top](#dash-documentation-boilerplate)**

Made with ❤️ by the Dash community

Pip Install Python LLC @ https://plotly.pro

**Star this repo** if you find it useful! ⭐

</div>

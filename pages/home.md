# Welcome to Dash Documentation Boilerplate

![logo](assets/intro_img.png)

> **A modern, responsive documentation system for Dash applications built with Dash Mantine Components**

Create beautiful, interactive documentation for your Dash components, data science workflows, and applications with markdown-driven content, live code examples, and automatic theme persistence.

---

## What is This?

The Dash Documentation Boilerplate is a **production-ready framework** for creating professional documentation sites for your Dash projects. Whether you're documenting a component library, showcasing data visualizations, or building a comprehensive application guide, this boilerplate provides everything you need.

### Built With Modern Technologies

- **Dash 3.2.0** - Latest Plotly Dash framework
- **Dash Mantine Components 2.4.0** - Beautiful, accessible UI components
- **Mantine 8.3.6** - Modern React component library
- **React 18** - Latest React features
- **Python 3.11+** - Modern Python with type hints

---

## Key Features

### 📝 Markdown-Driven Documentation
Write your documentation in **markdown files** with full Python integration. The framework automatically discovers markdown files in the `docs/` directory and generates pages with:

- **Frontmatter metadata** for page configuration
- **Custom directives** for interactive examples
- **Automatic routing** based on your file structure
- **Table of contents** generation

### 🎨 Beautiful UI/UX
Built with Dash Mantine Components for a modern, professional look:

- **Responsive design** - Works beautifully on mobile, tablet, and desktop
- **Dark & Light themes** - Automatic theme persistence via localStorage
- **Smooth transitions** - Professional animations and interactions
- **Customizable** - Easy to theme with your brand colors
- **Accessible** - WCAG compliant components

### 🔧 Custom Directives
Powerful directives to enhance your documentation:

- `.. toc::` - Generate table of contents from headings
- `.. exec::module.path` - Embed interactive Python components
- `.. source::path/to/file.py` - Display source code with syntax highlighting
- `.. kwargs::ComponentName` - Auto-generate component props documentation

### 🤖 AI/LLM Integration
**New in v0.2.0!** Powered by [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/):

- **Automatic AI-friendly documentation** - llms.txt, page.json, architecture.txt
- **SEO optimization** - sitemap.xml with intelligent priority inference
- **Bot management** - Control which bots can access your app
- **Structured data** - Schema.org JSON-LD for better search engines
- **Share with AI** - Users can share your URL with ChatGPT/Claude for help

### 🐋 Production Ready

- **Docker support** - Dockerfile and docker-compose included
- **Gunicorn server** - Production-ready WSGI server
- **Environment config** - Easy deployment configuration
- **Optimized builds** - Fast loading and rendering

---

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/pip-install-python/Dash-Documentation-Boilerplate.git
cd Dash-Documentation-Boilerplate

# Install Python dependencies
pip install -r requirements.txt

# Install Node dependencies (for Mantine components)
npm install
```

### 2. Run the Development Server

```bash
python run.py
```

Visit **http://localhost:8553** in your browser.

### 3. Create Your First Documentation Page

Create a new folder in `docs/` with a markdown file:

```markdown
---
name: My Component
description: Description of my awesome component
endpoint: /components/my-component
icon: mdi:code-tags
---

## My Component

Your documentation content here...

.. toc::

## Features

- Feature 1
- Feature 2
```

That's it! Your page will automatically appear in the navigation.

---

## Example Documentation

This site includes several example pages to demonstrate the capabilities:

- **Getting Started** - Learn how to create documentation pages
- **Custom Directives** - See all available directives in action
- **Interactive Components** - Examples of callbacks and state management
- **Data Visualization** - Plotly integration examples
- **AI Integration** - Showcase AI/LLM features

---

## Project Structure

```
dash-documentation-boilerplate/
├── assets/                      # Static assets and CSS
│   ├── intro_img.png
│   ├── m2d.css                 # Markdown-to-Dash styling
│   └── main.css                # Custom styles
│
├── components/                  # Reusable UI components
│   ├── appshell.py             # Main app layout
│   ├── header.py               # Header with search and theme toggle
│   └── navbar.py               # Navigation sidebar
│
├── docs/                        # Your documentation content
│   └── your-component/
│       ├── component.md        # Markdown documentation
│       └── examples.py         # Python interactive examples
│
├── lib/                         # Utility libraries
│   ├── constants.py            # App-wide constants
│   └── directives/             # Custom markdown directives
│       ├── kwargs.py           # Component props tables
│       ├── source.py           # Source code display
│       └── toc.py              # Table of contents
│
├── pages/                       # Dash multi-page app
│   ├── home.md                 # This home page
│   ├── home.py                 # Home page layout
│   └── markdown.py             # Dynamic markdown loader
│
├── templates/
│   └── index.html              # Custom HTML template
│
├── CHANGELOG.md                # Version history
├── README.md                   # Full documentation
├── LLMS_INTEGRATION.md         # AI/LLM integration guide
├── requirements.txt            # Python dependencies
├── package.json                # Node dependencies
├── Dockerfile                  # Docker container
└── run.py                      # Application entry point
```

---

## Customization

### Change Primary Color

Edit `lib/constants.py`:

```python
PRIMARY_COLOR = "teal"  # Change to any Mantine color
```

### Modify Styles

- `assets/main.css` - General application styling
- `assets/m2d.css` - Markdown-specific styling

### Configure AI/LLM Integration

Update `run.py` to configure bot management and SEO:

```python
from dash_improve_my_llms import RobotsConfig

app._base_url = "https://your-production-url.com"
app._robots_config = RobotsConfig(
    block_ai_training=True,
    allow_ai_search=True,
    crawl_delay=10
)
```

---

## Deployment

### Docker

```bash
# Build the image
docker build -t dash-docs-boilerplate .

# Run the container
docker run -p 8550:8550 dash-docs-boilerplate
```

### Docker Compose

```bash
docker-compose up
```

Visit **http://localhost:8550**

---

## Resources

- **GitHub Repository**: [Dash-Documentation-Boilerplate](https://github.com/pip-install-python/Dash-Documentation-Boilerplate)
- **Full Documentation**: See [README.md](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/blob/main/README.md)
- **Changelog**: [CHANGELOG.md](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/blob/main/CHANGELOG.md)
- **AI Integration Guide**: [LLMS_INTEGRATION.md](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/blob/main/LLMS_INTEGRATION.md)

### Community

- **GitHub**: [@pip-install-python](https://github.com/pip-install-python) ![GitHub](https://img.shields.io/github/followers/pip-install-python?style=social)
- **YouTube**: [Pip Install Python](https://www.youtube.com/channel/UC-pBvv8mzLpj0k-RIbc2Nog?sub_confirmation=1) ![YouTube](https://img.shields.io/youtube/channel/subscribers/UC-pBvv8mzLpj0k-RIbc2Nog?style=social)

---

## License

MIT License - see [LICENSE](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/blob/main/LICENSE) for details.

---

**Ready to start?** Check out the example documentation pages to see what you can build!

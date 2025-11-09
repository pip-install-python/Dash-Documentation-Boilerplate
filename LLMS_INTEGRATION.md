# AI/LLM Integration Guide - dash-improve-my-llms

This documentation boilerplate is now integrated with **dash-improve-my-llms v0.3.0**, providing automatic AI-friendly documentation, bot management, and SEO optimization.

---

## ✨ What's Included

Your Dash Documentation Boilerplate now automatically generates:

### 📄 AI Documentation (v0.1.0)
1. **`/llms.txt`** - Comprehensive markdown optimized for LLM understanding
2. **`/page.json`** - Technical architecture with component details
3. **`/architecture.txt`** - ASCII art overview of entire application

### 🤖 Bot Management & SEO (v0.2.0+)
4. **`/robots.txt`** - Intelligent bot control (blocks AI training bots)
5. **`/sitemap.xml`** - SEO-optimized sitemap with smart priorities
6. **Static HTML for Bots** - Schema.org structured data for better crawling

### 🔍 Discovery
- **Meta tags** in HTML for LLM discovery
- **Structured data** (Schema.org JSON-LD)
- **Noscript fallback** for non-JS bots

---

## 🚀 Quick Test

After running your app, visit these URLs:

```bash
# Start the app
python run.py

# Visit in browser:
http://localhost:8553/llms.txt          # LLM-friendly documentation
http://localhost:8553/page.json         # Technical architecture
http://localhost:8553/architecture.txt  # App overview
http://localhost:8553/robots.txt        # Bot access control
http://localhost:8553/sitemap.xml       # SEO sitemap

# Page-specific documentation:
http://localhost:8553/llms.txt          # Home page
http://localhost:8553/pip/example/llms.txt  # Example page
```

---

## 📖 Configuration Details

### 1. Base URL (run.py:39)

```python
app._base_url = "https://your-app-url.com"  # Update this!
```

**Important:** Change this to your production URL for proper sitemap generation.

### 2. Bot Policies (run.py:42-48)

```python
app._robots_config = RobotsConfig(
    block_ai_training=True,      # Block GPTBot, CCBot, anthropic-ai
    allow_ai_search=True,         # Allow ChatGPT-User, ClaudeBot
    allow_traditional=True,       # Allow Googlebot, Bingbot
    crawl_delay=10,               # Delay between requests (seconds)
    disallowed_paths=[],          # Paths to block
)
```

**Bot Types:**
- **AI Training Bots (Blocked):** GPTBot, Claude-Web, CCBot, Google-Extended, anthropic-ai
- **AI Search Bots (Allowed):** ChatGPT-User, ClaudeBot, PerplexityBot
- **Traditional (Allowed):** Googlebot, Bingbot, Yahoo, DuckDuckBot

### 3. Page Metadata (run.py:54-58)

```python
register_page_metadata(
    path="/",
    name="Dash Documentation Boilerplate",
    description="A modern, responsive documentation system..."
)
```

**Why:** Improves SEO and helps AI understand page purpose.

---

## 🎯 Using in Your Documentation Pages

### Marking Important Content

Use `mark_important()` to highlight key elements for AI understanding:

```python
# In your docs/your-page/example.py
from dash_improve_my_llms import mark_important
from dash import html, dcc

# Mark important interactive sections
component = html.Div([
    html.H1("Your Component"),

    # Highlight key controls
    mark_important(
        html.Div([
            dcc.Input(id='search', placeholder='Search...'),
            dcc.Dropdown(id='filter', options=[...]),
        ], id='filters'),
        component_id='filters'
    ),

    html.Div(id='results')
])
```

**Benefits:**
- LLMs understand these are key interactive elements
- Appears prominently in llms.txt
- Helps AI assistants guide users better

### Adding Page Metadata

Add metadata to your documentation markdown files:

```markdown
---
name: Your Component
description: A detailed description of what this component does
endpoint: /components/your-component
icon: mdi:code-tags
---

.. toc::

## Your Component

Documentation content here...

.. exec::docs.your-component.example
```

Or register metadata programmatically:

```python
# In run.py, after add_llms_routes(app)
register_page_metadata(
    path="/components/your-component",
    name="Your Component Name",
    description="What it does and why it's useful"
)
```

---

## 🔒 Privacy Controls

### Hiding Sensitive Pages

Use `mark_hidden()` to exclude pages from AI/bots:

```python
# In run.py
from dash_improve_my_llms import mark_hidden

# Hide admin or internal pages
mark_hidden("/admin")
mark_hidden("/internal/metrics")

# These pages will:
# - Not appear in sitemap.xml
# - Be blocked in robots.txt
# - Return 404 for /admin/llms.txt
```

### Hiding Components

```python
from dash_improve_my_llms import mark_component_hidden
from dash import html

# Hide sensitive information from extraction
api_keys = html.Div([
    html.P("API Key: sk-..."),
    html.P("Secret: abc123")
], id="api-keys")

mark_component_hidden(api_keys)
```

---

## 📊 What Gets Generated

### llms.txt Example

```markdown
# Dash Documentation Boilerplate

> A modern, responsive documentation system for Dash applications

## Application Context
This page is part of a multi-page Dash application with 2 total pages.

## Page Purpose
- **Interactive**: Responds to user interactions

## Interactive Elements
**User Inputs:**
- Button (ID: update-button)

**Outputs:**
- Graph (ID: example-graph)

## Data Flow & Callbacks
**Callback 1:**
- Updates: example-graph.figure
- Triggered by: update-button.n_clicks
```

### robots.txt Example

```
# Robots.txt for Dash Application

# Block AI Training Bots
User-agent: GPTBot
Disallow: /

User-agent: anthropic-ai
Disallow: /

# Allow AI Search Bots
User-agent: ChatGPT-User
Allow: /

User-agent: ClaudeBot
Allow: /

# Traditional Search Engines
User-agent: *
Allow: /
Crawl-delay: 10

Sitemap: https://your-app-url.com/sitemap.xml
```

### sitemap.xml Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://your-app-url.com/</loc>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://your-app-url.com/pip/example</loc>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
```

---

## 🧪 Testing Bot Responses

### Test with Different User Agents

```bash
# AI Search Bot (will see static HTML with llms.txt content)
curl -H "User-Agent: Mozilla/5.0 (compatible; ClaudeBot/1.0)" \
  http://localhost:8553/ | head -50

# AI Training Bot (will get 403 Forbidden)
curl -H "User-Agent: Mozilla/5.0 (compatible; GPTBot/1.0)" \
  http://localhost:8553/

# Regular Browser (will get full React app)
curl http://localhost:8553/ | head -50
```

---

## 🎨 Customization

### Custom Bot Rules

```python
from dash_improve_my_llms import RobotsConfig

app._robots_config = RobotsConfig(
    block_ai_training=True,
    allow_ai_search=True,
    allow_traditional=True,
    crawl_delay=15,
    disallowed_paths=["/admin", "/api/*", "/internal/*"],
    custom_rules=[
        "User-agent: MyCustomBot",
        "Disallow: /private"
    ]
)
```

### Custom Sitemap Priorities

Priorities are auto-inferred, but you can customize:

```python
register_page_metadata(
    path="/important-page",
    name="Important Page",
    description="This is important",
    priority=0.95,  # Custom priority (0.0-1.0)
    changefreq="daily"  # daily, weekly, monthly, yearly
)
```

---

## 📚 Integration with markdown2dash

The hook works seamlessly with your markdown-driven documentation:

1. **Markdown files** with frontmatter are automatically discovered
2. **Custom directives** (exec, toc, source, kwargs) are extracted
3. **Interactive components** from Python files are documented
4. **Callbacks** are tracked and documented in llms.txt

**Example workflow:**

```markdown
<!-- docs/my-component/component.md -->
---
name: My Component
description: An awesome component
endpoint: /components/my-component
---

.. toc::

## Overview
Description of the component

.. exec::docs.my-component.example
```

```python
# docs/my-component/example.py
from dash_improve_my_llms import mark_important
from dash import html, dcc, callback, Input, Output

# Mark key sections
component = mark_important(
    html.Div([
        dcc.Input(id='input'),
        html.Div(id='output')
    ]),
    component_id='main-component'
)

@callback(Output('output', 'children'), Input('input', 'value'))
def update(value):
    return f"You entered: {value}"
```

**Result:** The LLM will understand:
- Component purpose from markdown
- Interactive elements from mark_important
- Data flow from callback tracking
- Complete context for better assistance

---

## 🚀 Benefits

### For Documentation Users
- **Share with AI:** Users can share your app URL with ChatGPT/Claude
- **Better Help:** AI can see actual structure and guide users
- **Faster Learning:** LLMs understand your app quickly

### For SEO
- **Better Indexing:** Search engines get proper sitemaps
- **Structured Data:** Schema.org helps Google understand
- **Bot Control:** Block training bots, allow search bots

### For Developers
- **Auto-Generated:** Documentation stays in sync with code
- **Zero Maintenance:** Updates automatically when you change code
- **Comprehensive:** Covers structure, components, callbacks, data flow

---

## 🔗 Resources

- **Package:** [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/)
- **GitHub:** Your package GitHub URL
- **llms.txt Spec:** [llmstxt.org](https://llmstxt.org/)
- **Dash Docs:** [dash.plotly.com](https://dash.plotly.com/)

---

## 📝 Quick Reference

### Available Routes
- `/llms.txt` - LLM-friendly documentation
- `/page.json` - Technical architecture
- `/architecture.txt` - App overview
- `/robots.txt` - Bot access control
- `/sitemap.xml` - SEO sitemap
- `/<page-path>/llms.txt` - Page-specific docs
- `/<page-path>/page.json` - Page-specific architecture

### Key Functions
```python
from dash_improve_my_llms import (
    add_llms_routes,           # Add all routes
    mark_important,            # Highlight components
    mark_hidden,               # Hide pages from bots
    register_page_metadata,    # Add custom metadata
    RobotsConfig              # Configure bot policies
)
```

### Configuration Points
- `app._base_url` - Production URL for SEO
- `app._robots_config` - Bot management policies
- `templates/index.html` - LLM discovery meta tags
- `register_page_metadata()` - Page-specific metadata

---

**Your documentation is now AI-friendly!** 🎉

When users share your app with ChatGPT or Claude, the AI will understand your app structure and help them effectively.

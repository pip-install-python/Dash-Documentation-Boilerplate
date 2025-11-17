---
name: AI/LLM Integration
description: Make your documentation AI-friendly with automatic generation of llms.txt, robots.txt, and SEO optimization
endpoint: /examples/ai-integration
package: ai-integration
icon: mdi:robot-outline
---

.. llms_copy::AI/LLM Integration

.. toc::

### Introduction

This documentation boilerplate includes **AI/LLM integration** powered by [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/) v0.3.0. This feature automatically generates AI-friendly documentation, manages bot access, and optimizes your site for search engines.

---

### What Gets Generated

The integration automatically creates several files that help AI assistants understand your application:

#### 1. `/llms.txt` - AI-Friendly Documentation

A markdown file optimized for Large Language Models that includes:

- **Application overview** and purpose
- **Interactive elements** (buttons, inputs, graphs)
- **Data flow** and callback descriptions
- **Component hierarchy** and relationships
- **Key features** and capabilities

Visit: [/llms.txt](https://dash-documentation-boilerplate.onrender.com/llms.txt)

#### 2. `/page.json` - Technical Architecture

A JSON file with technical details:

```json
{
  "app_name": "Dash Documentation Boilerplate",
  "version": "0.2.0",
  "components": [...],
  "callbacks": [...],
  "routes": [...]
}
```

Visit: [/page.json](https://dash-documentation-boilerplate.onrender.com/page.json)

#### 3. `/architecture.txt` - ASCII Overview

A text-based visual representation of your application structure.

Visit: [/architecture.txt](https://dash-documentation-boilerplate.onrender.com/architecture.txt)

#### 4. `/robots.txt` - Bot Management

Controls which bots can access your application:

- ✅ **Allows**: AI search bots (ChatGPT-User, ClaudeBot, PerplexityBot)
- ❌ **Blocks**: AI training bots (GPTBot, CCBot, anthropic-ai, Google-Extended)
- ✅ **Allows**: Traditional search engines (Googlebot, Bingbot)

Visit: [/robots.txt](https://dash-documentation-boilerplate.onrender.com/robots.txt)

#### 5. `/sitemap.xml` - SEO Optimization

An SEO-optimized sitemap with intelligent priority inference.

Visit: [/sitemap.xml](https://dash-documentation-boilerplate.onrender.com/sitemap.xml)

---

### Configuration

All configuration is done in `run.py`:

#### Base URL Configuration

```python
# Set your production URL for proper sitemap generation
app._base_url = "https://your-app-url.com"
```

#### Bot Management

```python
from dash_improve_my_llms import RobotsConfig

app._robots_config = RobotsConfig(
    block_ai_training=True,      # Block GPTBot, CCBot, etc.
    allow_ai_search=True,         # Allow ChatGPT-User, ClaudeBot
    allow_traditional=True,       # Allow Googlebot, Bingbot
    crawl_delay=10,               # Delay between requests (seconds)
    disallowed_paths=[],          # Paths to block
)
```

#### Page Metadata

```python
from dash_improve_my_llms import register_page_metadata

register_page_metadata(
    path="/",
    name="Dash Documentation Boilerplate",
    description="A modern, responsive documentation system for Dash applications"
)
```

---

### Highlighting Important Components

Use `mark_important()` to help AI understand key interactive elements:

#### Example Usage

```python
from dash_improve_my_llms import mark_important
from dash import html, dcc

component = html.Div([
    html.H2("Search Feature"),

    # Mark key interactive sections
    mark_important(
        html.Div([
            dcc.Input(id='search', placeholder='Search...'),
            dcc.Dropdown(id='filter', options=[...]),
        ], id='search-controls'),
        component_id='search-controls'
    ),

    html.Div(id='results')
])
```

#### Benefits

- LLMs recognize these as key interactive elements
- Appears prominently in llms.txt
- Helps AI assistants guide users more effectively

---

### Privacy Controls

#### Hiding Sensitive Pages

Use `mark_hidden()` to exclude pages from bots and AI:

```python
from dash_improve_my_llms import mark_hidden

# Hide admin or internal pages
mark_hidden("/admin")
mark_hidden("/internal/metrics")

# These pages will:
# - Not appear in sitemap.xml
# - Be blocked in robots.txt
# - Return 404 for /admin/llms.txt
```

#### Hiding Components

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

### How Users Can Share Your Docs with AI

Your users can now share your documentation URL directly with AI assistants:

#### With ChatGPT

1. User: "Can you help me understand this documentation? https://your-app.com"
2. ChatGPT fetches `/llms.txt` automatically
3. ChatGPT understands your app structure and helps the user

#### With Claude

1. User: "Here's a Dash app I'm using: https://your-app.com"
2. Claude fetches `/llms.txt` automatically
3. Claude provides context-aware assistance

#### What AI Sees

The AI assistant receives structured information about:

- Your app's purpose and capabilities
- Interactive components and their IDs
- Data flow and callback logic
- How to use different features
- Component relationships

---

### Bot Types Explained

#### AI Training Bots (Blocked by Default)

These bots train AI models on web content:

- **GPTBot** (OpenAI)
- **CCBot** (Common Crawl)
- **anthropic-ai** (Anthropic)
- **Google-Extended** (Google AI training)
- **FacebookBot** (Meta AI)

**Why block?** Prevent your content from being used in AI training datasets.

#### AI Search Bots (Allowed by Default)

These bots help AI assistants answer user queries:

- **ChatGPT-User** (OpenAI)
- **ClaudeBot** (Anthropic)
- **PerplexityBot** (Perplexity)
- **YouBot** (You.com)

**Why allow?** Enable users to get help from AI assistants.

#### Traditional Search Engines (Allowed by Default)

Standard search engine crawlers:

- **Googlebot** (Google)
- **Bingbot** (Microsoft)
- **Slurp** (Yahoo)
- **DuckDuckBot** (DuckDuckGo)

**Why allow?** Improve SEO and discoverability.

---

### SEO Benefits

The integration provides several SEO advantages:

#### 1. Sitemap Generation

Automatic sitemap with smart priorities:

- Home page: Priority 1.0
- Documentation pages: Priority 0.7-0.9
- Example pages: Priority 0.5-0.7
- Change frequency inference

#### 2. Structured Data

Schema.org JSON-LD in HTML:

```json
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "Your App",
  "description": "Your description",
  "documentation": {...}
}
```

#### 3. Meta Tags

LLM discovery meta tags:

```html
<meta name="llms-txt" content="/llms.txt">
<meta name="llms-page-json" content="/page.json">
<meta name="llms-architecture" content="/architecture.txt">
```

#### 4. Noscript Fallback

For bots that don't execute JavaScript:

```html
<noscript>
  <div>
    <h1>App Name</h1>
    <ul>
      <li><a href="/llms.txt">LLM Documentation</a></li>
      <li><a href="/sitemap.xml">Sitemap</a></li>
    </ul>
  </div>
</noscript>
```

---

### Testing the Integration

#### Test Different User Agents

```bash
# AI Search Bot (will see static HTML with llms.txt content)
curl -H "User-Agent: Mozilla/5.0 (compatible; ClaudeBot/1.0)" \\
  http://localhost:8553/ | head -50

# AI Training Bot (will get 403 Forbidden)
curl -H "User-Agent: Mozilla/5.0 (compatible; GPTBot/1.0)" \\
  http://localhost:8553/

# Regular Browser (will get full React app)
curl http://localhost:8553/ | head -50
```

#### Verify Routes

```bash
# Start your app
python run.py

# Test all routes
curl http://localhost:8553/llms.txt
curl http://localhost:8553/page.json
curl http://localhost:8553/architecture.txt
curl http://localhost:8553/robots.txt
curl http://localhost:8553/sitemap.xml

# Test page-specific docs
curl http://localhost:8553/getting-started/llms.txt
```

---

### Advanced Configuration

#### Custom Bot Rules

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
        "Disallow: /private",
        "",
        "User-agent: AnotherBot",
        "Allow: /public"
    ]
)
```

#### Custom Sitemap Priorities

```python
from dash_improve_my_llms import register_page_metadata

register_page_metadata(
    path="/important-page",
    name="Important Page",
    description="This is important",
    priority=0.95,  # Custom priority (0.0-1.0)
    changefreq="daily"  # daily, weekly, monthly, yearly
)
```

---

### Best Practices

#### 1. Update Base URL

Always set your production URL:

```python
app._base_url = "https://docs.yourcompany.com"
```

#### 2. Mark Important Sections

Use `mark_important()` for key UI elements:

```python
mark_important(
    my_search_component,
    component_id='main-search'
)
```

#### 3. Hide Sensitive Pages

Protect internal pages:

```python
mark_hidden("/admin")
mark_hidden("/api/internal")
```

#### 4. Provide Good Metadata

Register metadata for all important pages:

```python
register_page_metadata(
    path="/my-feature",
    name="My Feature",
    description="Clear, descriptive text about this feature"
)
```

#### 5. Test Regularly

Verify your AI-friendly docs are working:

```bash
curl http://localhost:8553/llms.txt
```

---

### Resources

- **Package**: [dash-improve-my-llms on PyPI](https://pypi.org/project/dash-improve-my-llms/)
- **llms.txt Spec**: [llmstxt.org](https://llmstxt.org/)
- **Integration Guide**: [LLMS_INTEGRATION.md](/LLMS_INTEGRATION.md)
- **Schema.org**: [schema.org](https://schema.org/)
- **Robots.txt**: [robotstxt.org](https://www.robotstxt.org/)

---

### Quick Reference

#### Available Routes

| Route | Purpose |
|-------|---------|
| `/llms.txt` | LLM-friendly documentation |
| `/page.json` | Technical architecture |
| `/architecture.txt` | App overview |
| `/robots.txt` | Bot access control |
| `/sitemap.xml` | SEO sitemap |
| `/<page>/llms.txt` | Page-specific docs |

#### Key Functions

```python
from dash_improve_my_llms import (
    add_llms_routes,           # Add all routes
    mark_important,            # Highlight components
    mark_hidden,               # Hide pages from bots
    register_page_metadata,    # Add custom metadata
    RobotsConfig              # Configure bot policies
)
```

---

### Example: Complete Setup

Here's a complete example showing all features:

```python
from dash import Dash
from dash_improve_my_llms import (
    add_llms_routes,
    RobotsConfig,
    register_page_metadata,
    mark_hidden
)

app = Dash(__name__, use_pages=True)

# Configure base URL
app._base_url = "https://docs.myapp.com"

# Configure bots
app._robots_config = RobotsConfig(
    block_ai_training=True,
    allow_ai_search=True,
    allow_traditional=True,
    crawl_delay=10,
    disallowed_paths=["/admin", "/internal"]
)

# Add LLMS routes
add_llms_routes(app)

# Register page metadata
register_page_metadata(
    path="/",
    name="My App",
    description="A comprehensive Dash application"
)

# Hide sensitive pages
mark_hidden("/admin")
mark_hidden("/api/secrets")

app.layout = # your layout

if __name__ == "__main__":
    app.run(debug=False)
```

---

Your documentation is now **AI-friendly and SEO-optimized**! 🤖✨

Users can share your URL with ChatGPT, Claude, or other AI assistants, and they'll understand your app structure to provide better help.

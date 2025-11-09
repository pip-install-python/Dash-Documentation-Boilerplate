---
name: Getting Started
description: Learn how to create documentation pages with markdown and Python
endpoint: /getting-started
package: example
icon: mdi:rocket-launch-outline
---

.. toc::

## Introduction

Welcome to the Dash Documentation Boilerplate! This guide will teach you how to create beautiful, interactive documentation pages using markdown and Python.

The boilerplate uses a **markdown-driven approach** where you write documentation in `.md` files and supplement them with interactive Python components. The framework automatically discovers your documentation and generates pages with routing.

---

## Creating Your First Page

### Step 1: Create a Folder

Create a new folder in the `docs/` directory for your component or feature:

```bash
mkdir -p docs/my-component
```

### Step 2: Create a Markdown File

Create a markdown file with **frontmatter metadata** at the top:

```markdown
---
name: My Component
description: A description of my awesome component
endpoint: /components/my-component
package: my-component
icon: mdi:code-tags
---

## My Component

Your documentation content here...
```

#### Frontmatter Fields

- **name** (required): Display name in the navigation
- **description** (required): Short description for SEO and navigation
- **endpoint** (required): URL path for the page (e.g., `/components/my-component`)
- **package** (optional): Package name for organization
- **icon** (optional): Material Design icon (from [Iconify](https://icon-sets.iconify.design/mdi/))

### Step 3: Write Your Content

Use standard markdown syntax for your documentation:

```markdown
## Features

This component provides:

- Feature 1
- Feature 2
- Feature 3

### Usage

Here's how to use it:

\`\`\`python
import dash_mantine_components as dmc

component = dmc.Button("Click me!")
\`\`\`

### Advanced Examples

More detailed examples below...
```

That's it! The page will automatically appear in the navigation when you restart the server.

---

## Using Custom Directives

The boilerplate provides powerful **custom directives** to enhance your documentation:

### Table of Contents - `.. toc::`

Automatically generate a table of contents from your headings:

```markdown
.. toc::

## Section 1
Content here...

## Section 2
Content here...
```

### Execute Python Components - `.. exec::`

Embed interactive Dash components from Python modules:

```markdown
.. exec::docs.my-component.example
```

This will import and render the `component` variable from `docs/my-component/example.py`.

**Tip:** Use `:code: false` to hide the code and show only the rendered output:

```markdown
.. exec::docs.my-component.example
    :code: false
```

### Display Source Code - `.. source::`

Show syntax-highlighted source code:

```markdown
.. source::docs/my-component/example.py
```

**Tip:** Make long code collapsible:

```markdown
.. source::docs/my-component/example.py
    :defaultExpanded: false
    :withExpandedButton: true
```

### Component Props - `.. kwargs::`

Auto-generate a props documentation table:

```markdown
.. kwargs::dmc.Button
```

---

## Directive Options

The custom directives support **options** that control how content is displayed. Options are specified using a colon syntax after the directive.

### Common Directive Options

#### Option: code false - Hide Source Code Display

Use with `.. exec::` to show only the rendered component without the code:

```markdown
.. exec::docs.my-component.example
    :code: false
```

**When to use:**
- ✅ You want to show the interactive demo without cluttering the page
- ✅ The code will be shown separately with `.. source::`
- ✅ The example is self-explanatory and code isn't needed inline

**Example:**
```markdown
Here's an interactive demo:

.. exec::docs.data-visualization.basic_chart
    :code: false

Source code:

.. source::docs/data-visualization/basic_chart.py
```

#### Option: defaultExpanded false - Collapse Code by Default

Use with `.. source::` to show code in a collapsed state initially:

```markdown
.. source::docs/my-component/example.py
    :defaultExpanded: false
```

**When to use:**
- ✅ Long source files that might overwhelm the page
- ✅ Optional/advanced code that users can view if interested
- ✅ Multiple code examples on one page

#### Option: withExpandedButton true - Add Expand/Collapse Button

Use with `.. source::` to add an interactive expand/collapse button:

```markdown
.. source::docs/my-component/example.py
    :defaultExpanded: false
    :withExpandedButton: true
```

**When to use:**
- ✅ Combined with `:defaultExpanded: false` for collapsible code
- ✅ Giving users control over viewing source code
- ✅ Keeping documentation clean while making code accessible

### Combining Options

You can combine multiple options for fine-grained control:

```markdown
## Interactive Demo

The component in action:

.. exec::docs.components.advanced-example
    :code: false

<Click to view source code>

.. source::docs/components/advanced-example.py
    :defaultExpanded: false
    :withExpandedButton: true
```

This pattern creates a clean documentation flow:
1. User sees the interactive demo first
2. User can optionally expand to view the source code
3. Page stays uncluttered for quick scanning

### Complete Example

Here's a real-world example combining all these options:

```markdown
---
name: My Component
description: An awesome interactive component
endpoint: /components/my-component
---

.. toc::

## Overview

This component provides interactive data filtering...

## Live Demo

Try it out below:

.. exec::docs.components.my-component.demo
    :code: false

Want to see how it works? View the source:

.. source::docs/components/my-component/demo.py
    :defaultExpanded: false
    :withExpandedButton: true

## API Reference

Component props documentation:

.. kwargs::dmc.MyComponent
```

### Best Practices

**✅ Do:**
- Use `:code: false` when showing code separately with `.. source::`
- Collapse long code files with `:defaultExpanded: false`
- Add expand buttons for optional code viewing
- Keep the user experience in mind - don't overwhelm with code

**❌ Don't:**
- Hide code without providing a way to view it
- Use `:code: false` for simple examples where seeing code helps understanding
- Collapse very short code snippets (< 20 lines)

---

## Creating Interactive Examples

### Basic Example

Create a Python file in your docs folder (e.g., `docs/my-component/example.py`):

```python
from dash import html, dcc
import dash_mantine_components as dmc

component = dmc.Button(
    "Click Me!",
    id="my-button",
    variant="filled",
    color="blue"
)
```

Then reference it in your markdown:

```markdown
.. exec::docs.my-component.example
```

### Example with Callbacks

You can create interactive examples with callbacks:

```python
from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc

component = html.Div([
    dmc.Button("Click Me!", id="click-button", n_clicks=0),
    html.Div(id="click-output")
])

@callback(
    Output("click-output", "children"),
    Input("click-button", "n_clicks")
)
def update_output(n_clicks):
    return f"Button clicked {n_clicks} times!"
```

---

## Interactive Example

Below is a working example showing a button that updates a graph. You can interact with it right here in the documentation!

.. exec::docs.example.introduction

The source code for this example is shown below:

.. source::docs/example/introduction.py

---

## Highlighting Important Elements for AI

If you want AI assistants (like ChatGPT or Claude) to better understand your interactive components, use the `mark_important()` function:

```python
from dash_improve_my_llms import mark_important
from dash import html, dcc

# Mark key interactive sections
component = html.Div([
    html.H2("My Feature"),

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

This helps when users share your documentation URL with AI assistants for help.

---

## File Structure Example

Here's a complete example of a documentation folder structure:

```
docs/
└── my-component/
    ├── my-component.md       # Main documentation
    ├── basic-example.py      # Basic usage example
    ├── advanced-example.py   # Advanced usage example
    └── callbacks-example.py  # Interactive callback example
```

In your markdown file:

```markdown
---
name: My Component
description: An awesome component
endpoint: /components/my-component
icon: mdi:star
---

.. toc::

## Overview
Description of the component...

## Basic Usage
.. exec::docs.my-component.basic-example
.. source::docs/my-component/basic-example.py

## Advanced Usage
.. exec::docs.my-component.advanced-example
.. source::docs/my-component/advanced-example.py

## Interactive Example
.. exec::docs.my-component.callbacks-example
.. source::docs/my-component/callbacks-example.py

## Component Props
.. kwargs::MyComponent
```

---

## Markdown Formatting Tips

### Code Blocks

Use triple backticks with language specification:

```python
def hello_world():
    print("Hello, World!")
```

```javascript
function helloWorld() {
    console.log("Hello, World!");
}
```

```bash
pip install dash-mantine-components
```

### Emphasis

- **Bold text** with `**text**`
- *Italic text* with `*text*`
- `Inline code` with backticks

### Links

- [External link](https://dash.plotly.com/)
- [Internal link](/getting-started)

### Lists

Unordered:
- Item 1
- Item 2
  - Nested item

Ordered:
1. First item
2. Second item
3. Third item

### Blockquotes

> This is a blockquote
> It can span multiple lines

### Tables

| Feature | Support |
|---------|---------|
| Markdown | ✅ |
| Python | ✅ |
| Callbacks | ✅ |

---

## Best Practices

### 1. Use Descriptive Names

Choose clear, descriptive names for your pages and components:

✅ Good: `name: Button Component`
❌ Bad: `name: Comp1`

### 2. Organize by Feature

Group related documentation together:

```
docs/
├── components/
│   ├── button/
│   └── input/
├── layouts/
│   ├── grid/
│   └── stack/
└── examples/
    ├── dashboard/
    └── form/
```

### 3. Add Table of Contents

Always include `.. toc::` at the top of long documentation pages.

### 4. Show Code and Results

Use `.. exec::` and `.. source::` together to show both the code and the result. Consider using `:code: false` with exec and `:defaultExpanded: false` with source for cleaner presentation.

### 5. Test Your Examples

Make sure your interactive examples actually work before documenting them!

---

## Next Steps

Now that you know the basics, check out these example pages:

- **Custom Directives** - See all directives in action with examples
- **Interactive Components** - Advanced callback patterns and state management
- **Data Visualization** - Plotly charts and graphs integration
- **AI Integration** - Using the dash-improve-my-llms features

---

## Need Help?

- **Documentation**: Check the [README.md](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/blob/main/README.md)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues)
- **Community**: Join the [Dash Community Forum](https://community.plotly.com/)

---

Happy documenting! 🚀

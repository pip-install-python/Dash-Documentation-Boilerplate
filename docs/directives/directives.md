---
name: Custom Directives
description: Comprehensive guide to all custom markdown directives available
endpoint: /examples/directives
package: directives
icon: mdi:code-braces
---

.. toc::

## Introduction

This documentation boilerplate comes with **powerful custom directives** that extend standard markdown with interactive features. Directives are special commands that let you embed Python components, display source code, generate tables of contents, and more.

All directives use the syntax: `.. directive_name::optional_argument`

---

## Available Directives

### 1. Table of Contents - `.. toc::`
### 2. Execute Python - `.. exec::`
### 3. Source Code Display - `.. source::`
### 4. Component Props - `.. kwargs::`

---

## 1. Table of Contents Directive

The `.. toc::` directive automatically generates a navigable table of contents from your markdown headings.

### Usage

Simply add `.. toc::` anywhere in your markdown (typically at the top):

```markdown
.. toc::

## Section 1
Content...

## Section 2
Content...

### Subsection 2.1
More content...
```

### Features

- **Auto-generates** from H2 and H3 headings
- **Clickable links** that scroll to sections
- **Hierarchical structure** showing document organization
- **Automatically updates** when you add new sections

### Example

The table of contents at the top of this page was generated using `.. toc::`!

---

## 2. Execute Python Directive

The `.. exec::` directive embeds interactive Dash components from Python modules.

### Usage

```markdown
.. exec::docs.module.submodule
```

This imports and renders the `component` variable from the specified module path.

### How It Works

1. Create a Python file (e.g., `docs/directives/button_example.py`)
2. Define a `component` variable with your Dash component
3. Reference it in markdown with `.. exec::docs.directives.button_example`

### Example: Simple Button

**Markdown:**
```markdown
.. exec::docs.directives.button_example
```

**Python file** (`docs/directives/button_example.py`):
```python
import dash_mantine_components as dmc

component = dmc.Button(
    "Click me!",
    variant="filled",
    color="teal"
)
```

**Result:**

.. exec::docs.directives.button_example

---

## 3. Source Code Display Directive

The `.. source::` directive displays syntax-highlighted source code from files.

### Usage

```markdown
.. source::path/to/file.py
```

### Features

- **Syntax highlighting** for Python code
- **Line numbers** for easy reference
- **Copy-to-clipboard** functionality (if enabled)
- **Clean formatting** with proper indentation

### Example: Display Source

Let's display the source code of the button example we just saw:

**Markdown:**
```markdown
.. source::docs/directives/button_example.py
```

**Result:**

.. source::docs/directives/button_example.py

---

## 4. Component Props Directive

The `.. kwargs::` directive auto-generates a documentation table for component properties.

### Usage

```markdown
.. kwargs::ComponentName
```

For Dash Mantine Components:
```markdown
.. kwargs::dmc.Button
.. kwargs::dmc.TextInput
.. kwargs::dmc.Select
```

### Features

- **Automatic extraction** of component properties
- **Type information** for each prop
- **Default values** when available
- **Descriptions** of what each prop does

### Example: Button Props

**Markdown:**
```markdown
.. kwargs::dmc.Button
```

**Result:**

.. kwargs::dmc.Button

---

## Interactive Examples with Callbacks

You can create fully interactive examples with callbacks using the `.. exec::` directive.

### Example: Counter

Here's an interactive counter that demonstrates callbacks:

.. exec::docs.directives.counter_example

The source code:

.. source::docs/directives/counter_example.py

---

## Complex Example: Form with Validation

Let's create a more complex example with form inputs and validation:

.. exec::docs.directives.form_example

Source code for this example:

.. source::docs/directives/form_example.py

---

## Combining Directives

The real power comes from **combining multiple directives** in one documentation page:

### Pattern 1: Show Code & Result

```markdown
## My Feature

Description of the feature...

### Interactive Demo

.. exec::docs.my-feature.demo

### Source Code

.. source::docs/my-feature/demo.py
```

### Pattern 2: Documentation with Props

```markdown
## Component API

### Example Usage

.. exec::docs.component.example

### Component Properties

.. kwargs::MyComponent

### Full Source

.. source::docs/component/example.py
```

### Pattern 3: Comprehensive Page

```markdown
---
name: My Component
description: Full documentation
endpoint: /components/my-component
---

.. toc::

## Overview
Description...

## Basic Example
.. exec::docs.component.basic
.. source::docs/component/basic.py

## Advanced Example
.. exec::docs.component.advanced
.. source::docs/component/advanced.py

## API Reference
.. kwargs::MyComponent

## Related Components
Links to other docs...
```

---

## Best Practices

### 1. Use Meaningful Module Names

✅ Good:
```markdown
.. exec::docs.buttons.primary_button_example
```

❌ Bad:
```markdown
.. exec::docs.ex1
```

### 2. Show Code and Result Together

Always pair `.. exec::` with `.. source::` so users can see both the result and how it's made:

```markdown
.. exec::docs.component.example
.. source::docs/component/example.py
```

### 3. Add Context with Markdown

Explain what the example demonstrates before showing it:

```markdown
This example demonstrates how to handle form validation:

.. exec::docs.forms.validation_example
```

### 4. Use Table of Contents for Long Pages

For documentation pages with multiple sections, always include:

```markdown
.. toc::
```

### 5. Document Component Props

When documenting a new component, include the props table:

```markdown
.. kwargs::YourComponent
```

---

## Advanced Tips

### Organizing Python Examples

Keep your Python examples organized by feature:

```
docs/
├── buttons/
│   ├── buttons.md
│   ├── basic_button.py
│   ├── icon_button.py
│   └── loading_button.py
├── forms/
│   ├── forms.md
│   ├── text_input.py
│   ├── select.py
│   └── validation.py
```

### Reusing Components

You can reference the same Python component from multiple markdown files:

```markdown
# In docs/examples/page1.md
.. exec::docs.shared.common_example

# In docs/examples/page2.md
.. exec::docs.shared.common_example
```

### Error Handling

If a directive fails to render:

1. Check the module path is correct
2. Ensure the Python file has a `component` variable
3. Check for syntax errors in your Python code
4. Look at the server logs for detailed error messages

---

## Directive Reference

### Quick Reference Table

| Directive | Syntax | Purpose |
|-----------|--------|---------|
| `toc` | `.. toc::` | Generate table of contents |
| `exec` | `.. exec::module.path` | Render Python component |
| `source` | `.. source::file/path.py` | Display source code |
| `kwargs` | `.. kwargs::ComponentName` | Show component props |

---

## Next Steps

- **Interactive Components** - Learn advanced callback patterns
- **Data Visualization** - Create beautiful charts and graphs
- **AI Integration** - Make your docs AI-friendly

---

## Need Help?

If you're having trouble with directives:

1. Check the Python module path is correct (use dots, not slashes)
2. Ensure your Python file exports a `component` variable
3. Look for syntax errors in your code
4. Check the terminal for error messages

For more help, visit the [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues).

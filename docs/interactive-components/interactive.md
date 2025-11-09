---
name: Interactive Components
description: Advanced callback patterns and state management examples
endpoint: /examples/interactive
package: interactive
icon: mdi:gesture-tap
---

.. toc::

## Introduction

This page demonstrates **advanced interactive patterns** using Dash callbacks, state management, and component interactions. Learn how to build complex, responsive user interfaces with real-time updates.

---

## Callback Basics

Callbacks are the heart of interactivity in Dash. They connect component properties and define how your app responds to user actions.

### Simple Callback Example

A basic button that updates text:

.. exec::docs.interactive-components.simple_callback
    :code: false
Source code:

.. source::docs/interactive-components/simple_callback.py

---

## Multiple Inputs

Handle multiple input sources in a single callback:

.. exec::docs.interactive-components.multiple_inputs
    :code: false
Source code:

.. source::docs/interactive-components/multiple_inputs.py

---

## State Management

Use `State` to access component values without triggering the callback:

.. exec::docs.interactive-components.state_example
    :code: false
Source code:

.. source::docs/interactive-components/state_example.py

---

## Pattern Matching Callbacks

Create dynamic components with pattern-matching callbacks:

.. exec::docs.interactive-components.pattern_matching
    :code: false
Source code:

.. source::docs/interactive-components/pattern_matching.py

---

## Chained Callbacks

Connect multiple callbacks to create complex workflows:

.. exec::docs.interactive-components.chained_callbacks
    :code: false
Source code:

.. source::docs/interactive-components/chained_callbacks.py

---

## Loading States

Provide visual feedback during long-running operations:

.. exec::docs.interactive-components.loading_states
    :code: false
Source code:

.. source::docs/interactive-components/loading_states.py

---

## Callback Patterns Reference

### Common Callback Patterns

#### Pattern 1: Single Input, Single Output

```python
@callback(
    Output("output-id", "children"),
    Input("input-id", "value")
)
def update_output(input_value):
    return f"You entered: {input_value}"
```

#### Pattern 2: Multiple Inputs, Single Output

```python
@callback(
    Output("result", "children"),
    Input("input1", "value"),
    Input("input2", "value")
)
def combine_inputs(val1, val2):
    return f"{val1} + {val2} = {val1 + val2}"
```

#### Pattern 3: Single Input, Multiple Outputs

```python
@callback(
    Output("output1", "children"),
    Output("output2", "children"),
    Input("trigger", "n_clicks")
)
def update_multiple(n_clicks):
    return f"Clicks: {n_clicks}", f"Double: {n_clicks * 2}"
```

#### Pattern 4: Using State

```python
@callback(
    Output("display", "children"),
    Input("submit-btn", "n_clicks"),
    State("input-field", "value")
)
def submit_form(n_clicks, value):
    if n_clicks is None:
        return "Click submit to see value"
    return f"Submitted: {value}"
```

#### Pattern 5: Pattern Matching with ALL

```python
@callback(
    Output("summary", "children"),
    Input({"type": "dynamic-input", "index": ALL}, "value")
)
def aggregate_inputs(values):
    return f"Total: {sum(v or 0 for v in values)}"
```

#### Pattern 6: Pattern Matching with MATCH

```python
@callback(
    Output({"type": "output", "index": MATCH}, "children"),
    Input({"type": "input", "index": MATCH}, "value")
)
def update_matching(value):
    return f"Value: {value}"
```

---

## Advanced Techniques

### Preventing Initial Calls

Prevent callbacks from firing on page load:

```python
@callback(
    Output("output", "children"),
    Input("button", "n_clicks"),
    prevent_initial_call=True
)
def update(n_clicks):
    return f"Button clicked {n_clicks} times"
```

### Circular Callbacks

Allow circular callback chains with `allow_duplicate=True`:

```python
@callback(
    Output("value", "data", allow_duplicate=True),
    Input("increment", "n_clicks"),
    State("value", "data"),
    prevent_initial_call=True
)
def increment_value(n_clicks, current):
    return (current or 0) + 1
```

### Determining Trigger

Find out which input triggered the callback:

```python
from dash import ctx

@callback(
    Output("output", "children"),
    Input("btn1", "n_clicks"),
    Input("btn2", "n_clicks")
)
def update(btn1_clicks, btn2_clicks):
    trigger_id = ctx.triggered_id

    if trigger_id == "btn1":
        return "Button 1 was clicked"
    elif trigger_id == "btn2":
        return "Button 2 was clicked"

    return "No button clicked yet"
```

### Background Callbacks

For long-running operations (requires `diskcache` or `celery`):

```python
from dash import DiskcacheManager
import diskcache

cache = diskcache.Cache("./cache")
background_callback_manager = DiskcacheManager(cache)

@callback(
    Output("result", "children"),
    Input("submit", "n_clicks"),
    background=True,
    manager=background_callback_manager
)
def long_running_task(n_clicks):
    # Simulate long operation
    time.sleep(10)
    return "Task complete!"
```

---

## Best Practices

### 1. Keep Callbacks Simple

Break complex logic into multiple callbacks:

✅ **Good:**
```python
@callback(Output("processed", "data"), Input("raw", "data"))
def process_data(raw):
    return process(raw)

@callback(Output("chart", "figure"), Input("processed", "data"))
def create_chart(processed):
    return make_figure(processed)
```

❌ **Bad:**
```python
@callback(Output("chart", "figure"), Input("raw", "data"))
def do_everything(raw):
    processed = process(raw)
    return make_figure(processed)
```

### 2. Use State for Form Inputs

Use `State` to avoid triggering callbacks on every keystroke:

```python
# Good for forms
@callback(
    Output("result", "children"),
    Input("submit-button", "n_clicks"),
    State("text-input", "value")
)
```

### 3. Validate Inputs

Always validate input values:

```python
@callback(Output("output", "children"), Input("input", "value"))
def update(value):
    if value is None or value == "":
        return "Please enter a value"

    if not isinstance(value, str):
        return "Invalid input type"

    return f"Valid input: {value}"
```

### 4. Handle None Values

Check for `None` to handle initial callbacks:

```python
@callback(Output("output", "children"), Input("input", "value"))
def update(value):
    if value is None:
        return "Waiting for input..."

    return f"Processing: {value}"
```

### 5. Use Proper IDs

Choose descriptive, unique IDs:

✅ Good: `"user-email-input"`, `"submit-form-button"`
❌ Bad: `"input1"`, `"btn"`

---

## Performance Tips

### 1. Memoization

Cache expensive computations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(param):
    # Heavy processing here
    return result
```

### 2. Clientside Callbacks

Use JavaScript callbacks for simple UI updates:

```python
app.clientside_callback(
    """
    function(n_clicks) {
        return n_clicks || 0;
    }
    """,
    Output("counter", "children"),
    Input("button", "n_clicks")
)
```

### 3. Partial Updates

Update only what changed:

```python
@callback(
    Output("table", "data"),
    Input("refresh", "n_clicks"),
    State("table", "data")
)
def update_table(n_clicks, current_data):
    # Only update specific rows
    new_data = current_data.copy()
    new_data[0] = updated_row
    return new_data
```

---

## Common Pitfalls

### 1. Circular Dependency

❌ **Wrong:**
```python
@callback(Output("a", "value"), Input("b", "value"))
def update_a(b): return b

@callback(Output("b", "value"), Input("a", "value"))
def update_b(a): return a
```

✅ **Fixed:**
```python
@callback(
    Output("a", "value", allow_duplicate=True),
    Input("b", "value"),
    prevent_initial_call=True
)
def update_a(b): return b
```

### 2. Modifying Global State

❌ **Wrong:**
```python
global_data = []

@callback(Output("out", "children"), Input("btn", "n_clicks"))
def update(n):
    global_data.append(n)  # Don't do this!
    return len(global_data)
```

✅ **Fixed:**
```python
@callback(
    Output("store", "data"),
    Output("out", "children"),
    Input("btn", "n_clicks"),
    State("store", "data")
)
def update(n, data):
    data = data or []
    data.append(n)
    return data, len(data)
```

---

## Testing Callbacks

### Example Test

```python
from dash.testing import DashComposite

def test_callback(dash_duo):
    app = create_app()
    dash_duo.start_server(app)

    # Find input and click button
    input_elem = dash_duo.find_element("#my-input")
    input_elem.send_keys("test value")

    button = dash_duo.find_element("#submit-button")
    button.click()

    # Wait for callback to complete
    dash_duo.wait_for_text_to_equal("#output", "Expected text")
```

---

## Next Steps

- **Data Visualization** - Create interactive charts
- **AI Integration** - Make your components AI-friendly
- **Getting Started** - Learn the basics

---

Happy coding! 🚀

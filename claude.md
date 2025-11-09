# Dash Documentation Boilerplate - Migration Guide

## Project Overview

This project is a documentation boilerplate for Dash applications, inspired by the [dmc-docs](https://github.com/snehilvj/dmc-docs) project. It provides a markdown-driven documentation system with interactive examples using Dash and Dash Mantine Components (DMC).

**Last Updated:** November 2024 (project ~1 year old)
**Migration Target:** Dash 3.x and DMC 2.4.0 (latest)

---

## Current State Analysis

### Installed Dependencies (as of analysis)
```
dash: 3.2.0
dash-mantine-components: 2.3.0
plotly: 6.1.2
dash-iconify: 0.1.2
```

### requirements.txt (outdated)
```
dash>=2.5.0
dash-mantine-components>=0.14.7  # VERY OUTDATED - from 2024
dash-html-components>=2.0.0      # DEPRECATED - removed in Dash 3.0
dash_table>=5.0.0                # DEPRECATED - removed in Dash 3.0
dash-core-components>=2.0.0      # DEPRECATED - removed in Dash 3.0
```

### package.json (misaligned)
```
@mantine/core: 7.14.1            # DMC 2.3.0 uses Mantine 8.3.1
@mantine/carousel: 7.14.1        # Should be 8.3.6 for DMC 2.4.0
```

---

## Project Structure

```
dash-documentation-boilerplate/
├── assets/                      # Static assets and CSS
│   ├── m2d.css                 # Markdown-to-Dash styling
│   ├── main.css                # Custom styling
│   └── *.png                   # Images
├── components/                  # Reusable UI components
│   ├── appshell.py             # Main app shell with MantineProvider
│   ├── header.py               # Header with search and theme toggle
│   └── navbar.py               # Navigation sidebar
├── docs/                        # Documentation content
│   └── example/
│       ├── example.md          # Markdown documentation
│       └── introduction.py     # Python code examples
├── lib/                         # Utility libraries
│   ├── constants.py            # App constants
│   └── directives/             # Custom markdown directives
│       ├── kwargs.py           # Component props table generator
│       ├── source.py           # Source code display
│       └── toc.py              # Table of contents generator
├── pages/                       # Dash pages
│   ├── home.py                 # Home page
│   ├── home.md                 # Home page content
│   └── markdown.py             # Dynamic markdown page generator
├── templates/
│   └── index.html              # HTML template
├── run.py                       # Application entry point
├── requirements.txt
├── package.json
├── Dockerfile
└── docker-compose.yml
```

---

## Key Components Analysis

### 1. run.py (Application Entry)
- ✅ Already using React 18.2.0 (`_dash_renderer._set_react_version("18.2.0")`)
- ✅ Using `dmc.styles.ALL` for stylesheets
- ⚠️ Uses deprecated `app.run_server()` (should be `app.run()` in Dash 3.0, but still works)
- ✅ Using `use_pages=True` for multi-page apps

### 2. components/appshell.py
- ⚠️ Uses `dmc.NotificationProvider()` - **DEPRECATED** in DMC 2.0+
  - Should migrate to `dmc.NotificationContainer`
- ✅ Uses `dmc.MantineProvider` with proper theme configuration
- ✅ AppShell structure looks compatible with DMC 2.x
- ✅ Clientside callbacks for theme switching

### 3. components/header.py
- ✅ Uses modern DMC components (ActionIcon, Select, Anchor)
- ✅ Proper use of `visibleFrom` and `hiddenFrom` props
- ✅ Clientside callbacks properly structured

### 4. components/navbar.py
- ✅ Uses AppShellNavbar and Drawer properly
- ✅ Modern DMC component usage

### 5. pages/markdown.py
- Uses `markdown2dash` library for parsing
- Custom directives: Admonition, BlockExec, Divider, Image, Kwargs, SC, TOC
- Registers pages dynamically from markdown files
- Uses frontmatter for metadata

---

## Migration Breaking Changes to Address

### 1. Dash 3.0 Breaking Changes

#### Removed Imports (CRITICAL)
```python
# ❌ OLD (no longer works in Dash 3.0)
import dash_core_components as dcc
import dash_html_components as html
import dash_table

# ✅ NEW (required for Dash 3.0)
from dash import dcc, html, dash_table
```

**Status:** Code appears to already use correct imports in most places, but requirements.txt needs updating.

#### app.run_server() → app.run()
```python
# ❌ OLD (deprecated but still works)
app.run_server(debug=False, host='0.0.0.0', port='8552')

# ✅ NEW (recommended)
app.run(debug=False, host='0.0.0.0', port='8552')
```

**Location:** `/run.py:38`

#### React Version
```python
# Already correct in run.py:8
dash._dash_renderer._set_react_version("18.2.0")
```

---

### 2. DMC 0.14.7 → 2.4.0 Breaking Changes

#### NotificationProvider → NotificationContainer (CRITICAL)
```python
# ❌ OLD (appshell.py:51)
dmc.NotificationProvider(),

# ✅ NEW
dmc.NotificationContainer(),
```

**Impact:** This is a major API change. See DMC migration guide for details.

#### Switch Component (if used)
- Default styles now include checked state indicator
- Set `withThumbIndicator=False` if old styles needed

#### DatePicker/DateTimePicker
- `DatePicker` renamed to `DatePickerInput` in 0.15.0
- New standalone `DatePicker` component added in 2.0.0
- `DateTimePicker` no longer accepts `timeInputProps`, use `timePickerProps`

#### Popover
- `hideDetached` now enabled by default (auto-closes when target removed)
- May need to disable globally if old behavior needed

#### Carousel
- `draggable` and `speed` props removed (no longer supported by Embla v8)
- Embla options now passed via `emblaOptions` prop

#### Portal
- `reuseTargetNode` now enabled by default (performance improvement)
- May cause z-index issues in edge cases

#### Menu
- No longer uses `data-hovered` attribute
- Use `:hover` and `:focus` selectors in CSS instead

#### Stylesheets
- Since DMC 1.2.0, optional stylesheets auto-included (Carousel, CodeHighlight, etc.)
- `dmc.styles.ALL` already in use ✅

---

### 3. Mantine 7.14.1 → 8.3.6 (package.json)

The package.json currently uses Mantine 7.14.1, but DMC 2.4.0 is built on Mantine 8.3.6.

**Required Updates:**
```json
{
  "dependencies": {
    "@mantine/carousel": "8.3.6",
    "@mantine/charts": "8.3.6",
    "@mantine/code-highlight": "8.3.6",
    "@mantine/core": "8.3.6",
    "@mantine/dates": "8.3.6",
    "@mantine/hooks": "8.3.6",
    "@mantine/notifications": "8.3.6",
    "@mantine/nprogress": "8.3.6",
    "@mantine/spotlight": "8.3.6"
  }
}
```

---

## Migration Checklist

### Phase 1: Dependency Updates
- [ ] Update `requirements.txt`
  - [ ] Remove deprecated package lines (dash-html-components, dash-core-components, dash_table)
  - [ ] Update `dash>=3.0.0`
  - [ ] Update `dash-mantine-components>=2.4.0`
  - [ ] Verify all other dependencies compatible with Dash 3.0
- [ ] Update `package.json`
  - [ ] Update all @mantine/* packages to 8.3.6
  - [ ] Update embla-carousel packages if needed
- [ ] Run `pip install -r requirements.txt --upgrade`
- [ ] Run `npm install` to update node dependencies

### Phase 2: Code Updates
- [ ] Update `run.py`
  - [ ] Change `app.run_server()` to `app.run()`
  - [ ] Verify React version setting still needed (should be default in Dash 3.0)
- [ ] Update `components/appshell.py`
  - [ ] Replace `dmc.NotificationProvider()` with `dmc.NotificationContainer()`
  - [ ] Test theme switching still works
  - [ ] Verify AppShell props compatibility
- [ ] Review all DMC component usage
  - [ ] Check for deprecated props
  - [ ] Update any Carousel usage (embla options)
  - [ ] Verify Table component usage
  - [ ] Check DatePicker/DateTimePicker usage
- [ ] Update CSS if needed
  - [ ] Check for Menu `data-hovered` selectors in main.css
  - [ ] Verify z-index stacking still works

### Phase 3: Testing
- [ ] Test local development server
  - [ ] `python run.py` runs without errors
  - [ ] Home page loads correctly
  - [ ] Example documentation page loads
- [ ] Test functionality
  - [ ] Theme toggle (light/dark) works
  - [ ] Navigation and search work
  - [ ] Mobile responsive design works
  - [ ] All markdown directives render correctly
  - [ ] Code highlighting works
  - [ ] Interactive examples work
- [ ] Test Docker deployment
  - [ ] Update Dockerfile if needed
  - [ ] `docker build -t dash-docs-boilerplate .` succeeds
  - [ ] `docker run -p 8050:8050 dash-docs-boilerplate` works
  - [ ] Test in container

### Phase 4: Documentation
- [ ] Update README.md with new dependency versions
- [ ] Document any breaking changes for users
- [ ] Update installation instructions
- [ ] Add migration notes if needed

---

## Known Issues & Considerations

### 1. markdown2dash Compatibility
- Check if `markdown2dash` is compatible with latest Dash/DMC versions
- May need updates to custom directives (kwargs.py, source.py, toc.py)

### 2. Custom CSS
- Verify all Mantine CSS classes still work with v8
- May need to update class selectors that changed

### 3. Docker
- Python 3.11.8 in Dockerfile is good
- Ensure all dependencies install correctly in container
- May need to update pip/npm in Dockerfile

### 4. NotificationContainer Migration
This is the most significant breaking change. The new API:
- Single `NotificationContainer` component (replaces NotificationProvider)
- Direct access to Mantine's Notification API in clientside callbacks
- See DMC docs for full migration guide

---

## Component Prop Changes Reference

### AppShell
- No major breaking changes for basic usage
- Verify `header`, `navbar`, `aside` config still works

### Table
- Now uses compound components: `TableTr`, `TableTd`, etc.
- New props: `borderColor`, `withRowBorders`, `stripedColor`, `highlightOnHoverColor`
- `withBorder` → `withTableBorder`
- Remove `fontSize` prop, use `fz` style prop

### Progress
- Now supports compound components pattern
- `ProgressRoot`, `ProgressSection`, `ProgressLabel`

### Button
- `compact` → `size='compact-xx'`
- `leftIcon`/`rightIcon` → `leftSection`/`rightSection`
- Remove `uppercase`, use `tt` style prop
- `loaderPosition` removed (always centered)

### Group
- `position` → `justify`
- `spacing` → `gap`

### SimpleGrid
- Now uses object format for breakpoints
- `cols={"base": 1, "sm": 2, "lg": 5}`

### Image
- `width`/`height` → `w`/`h` style props
- `caption` prop removed
- Use `fallbackSrc` for placeholder

---

## Files Requiring Changes

### Critical
1. `/requirements.txt` - Update dependencies
2. `/package.json` - Update Mantine packages
3. `/components/appshell.py` - NotificationProvider → NotificationContainer
4. `/run.py` - run_server() → run() (optional but recommended)

### Review
5. `/lib/directives/*.py` - Verify compatibility
6. `/pages/markdown.py` - Check markdown2dash compatibility
7. `/assets/main.css` - Update any deprecated selectors

### Testing
8. All files in `/docs/` - Verify examples still work
9. `/Dockerfile` - Ensure builds successfully
10. `/docker-compose.yml` - Test deployment

---

## Post-Migration Verification

### Functionality Checks
- [ ] App starts without errors
- [ ] All pages load correctly
- [ ] Theme switching works (light/dark)
- [ ] Search functionality works
- [ ] Mobile menu (drawer) works
- [ ] Code highlighting displays correctly
- [ ] Interactive examples work
- [ ] Table of contents renders
- [ ] Component props tables render
- [ ] All markdown directives work

### Visual Checks
- [ ] Layout looks correct (AppShell structure)
- [ ] Colors and theming consistent
- [ ] Typography correct
- [ ] Spacing and padding correct
- [ ] Responsive design works on mobile
- [ ] Icons render correctly

### Performance
- [ ] App loads quickly
- [ ] No console errors
- [ ] Smooth theme transitions
- [ ] Callbacks respond quickly

---

## Resources

### Documentation
- [Dash 3.0 Migration Guide](https://dash.plotly.com/migration)
- [DMC Migration Guide](https://www.dash-mantine-components.com/migration)
- [Mantine 8.0 Changelog](https://mantine.dev/changelog/8-0-0/)
- [dmc-docs GitHub](https://github.com/snehilvj/dmc-docs)

### Key Links
- [DMC Documentation](https://www.dash-mantine-components.com/)
- [Dash Documentation](https://dash.plotly.com/)
- [Mantine Documentation](https://mantine.dev/)

---

## Notes for Future Development

1. **Stay Aligned with dmc-docs**: This project follows the dmc-docs framework. When updating, check their repository for latest patterns and practices.

2. **Mantine Stability**: Per Mantine's author, v8+ should have fewer breaking changes going forward. Future updates should be smoother.

3. **React Version**: Dash 3.0 defaults to React 18.3.1. The explicit version setting in run.py may no longer be needed but doesn't hurt.

4. **Docker Deployment**: Keep Dockerfile dependencies in sync with requirements.txt. Consider using a requirements-lock file for production.

5. **Custom Directives**: The custom markdown directives (kwargs, source, toc) are a key differentiator. Ensure they remain compatible with updates.

---

## Migration Timeline Estimate

- **Phase 1** (Dependencies): 30 minutes
- **Phase 2** (Code Updates): 1-2 hours
- **Phase 3** (Testing): 2-3 hours
- **Phase 4** (Documentation): 1 hour

**Total**: ~4-6 hours for full migration and testing

---

## Success Criteria

Migration is complete when:
1. ✅ All tests pass
2. ✅ App runs on latest Dash 3.x and DMC 2.4.0
3. ✅ No deprecation warnings in console
4. ✅ All functionality works as before
5. ✅ Docker deployment succeeds
6. ✅ Documentation updated

---

*Last Updated: 2025-11-09*
*Claude Code Migration Analysis*
# Migration Notes - Dash Documentation Boilerplate

## Quick Reference: What Changed

### Critical Breaking Changes

#### 1. NotificationProvider → NotificationContainer
**Location:** `components/appshell.py:51`

```python
# Before (DMC < 2.0)
dmc.NotificationProvider()

# After (DMC >= 2.0)
dmc.NotificationContainer()
```

**Why:** DMC 2.0+ uses a new notification system aligned with Mantine's upstream implementation.

**Testing:** Ensure any notification callbacks still work after this change.

---

#### 2. Deprecated Package Imports Removed
**Location:** `requirements.txt:11-13`

```txt
# REMOVE these lines - they no longer exist in Dash 3.0
dash-html-components>=2.0.0
dash_table>=5.0.0
dash-core-components>=2.0.0
```

**Why:** These are stub packages that were kept for backwards compatibility in Dash 2.0 but removed in Dash 3.0. All components are now in the main `dash` package.

**Code Impact:** Your code already uses the correct imports (`from dash import html, dcc, dash_table`), so no code changes needed - just requirements.txt.

---

#### 3. Mantine Version Mismatch
**Location:** `package.json`

```json
// Before (Mantine 7)
"@mantine/core": "7.14.1",
"@mantine/carousel": "7.14.1",
// ... etc

// After (Mantine 8)
"@mantine/core": "8.3.6",
"@mantine/carousel": "8.3.6",
// ... etc
```

**Why:** DMC 2.4.0 is built on Mantine 8.3.6. Using Mantine 7.14.1 can cause compatibility issues.

**Impact:** May affect styling and component behavior. Test thoroughly after update.

---

### Optional/Recommended Changes

#### 4. app.run_server() → app.run()
**Location:** `run.py:38`

```python
# Old (deprecated but still works)
app.run_server(debug=False, host='0.0.0.0', port='8552')

# New (recommended)
app.run(debug=False, host='0.0.0.0', port='8552')
```

**Why:** `run_server()` is deprecated in Dash 3.0. `run()` is the new standard.

**Impact:** Low - old method still works but may be removed in future versions.

---

#### 5. React Version Setting
**Location:** `run.py:8`

```python
# May no longer be needed (Dash 3.0 defaults to React 18.3.1)
_dash_renderer._set_react_version("18.2.0")
```

**Why:** Dash 3.0 defaults to React 18.3.1, so explicit version setting is optional.

**Recommendation:** Keep it for now to maintain exact version (18.2.0 vs 18.3.1), or remove to use Dash's default.

---

## Component-Specific Changes

### AppShell
**Status:** ✅ No breaking changes for your usage

The AppShell configuration you're using is compatible with DMC 2.x:
```python
dmc.AppShell(
    header={"height": 70},
    navbar={"width": 300, "breakpoint": "lg", "collapsed": {"mobile": True}},
    aside={"width": 300, "breakpoint": "xl", "collapsed": {"desktop": False, "mobile": True}},
)
```

---

### Table
**Status:** ⚠️ Monitor (if used)

You're using default props in theme config:
```python
"Table": {
    "defaultProps": {
        "highlightOnHover": True,
        "withTableBorder": True,  # ✅ Correct (was withBorder in v7)
        "verticalSpacing": "sm",
        "horizontalSpacing": "md",
    }
}
```

This is correct for DMC 2.x. If you have any tables in docs, verify they still work.

---

### CodeHighlight
**Status:** ✅ Should work

You're using `dmc.CodeHighlightTabs` in `lib/directives/source.py`. This component is compatible with DMC 2.x.

**Note:** DMC 2.x includes only top 10 languages by default. If you need additional languages, may need to request them.

---

### Select Component
**Status:** ✅ Looks good

Your search component in `header.py` uses modern props:
```python
dmc.Select(
    searchable=True,
    clearable=True,
    leftSection=DashIconify(...),
    comboboxProps={"zIndex": 2000},
)
```

All compatible with DMC 2.x.

---

## CSS Changes Needed

### Menu Selectors (if any)
**Location:** Check `assets/main.css` and `assets/m2d.css`

```css
/* ❌ Old (no longer works) */
.menu-item[data-hovered] {
  background-color: red;
}

/* ✅ New */
.menu-item:hover,
.menu-item:focus {
  background-color: red;
}
```

**Status:** Quick search shows no `data-hovered` selectors in your CSS. ✅

---

## Testing Strategy

### 1. Dependency Update Testing
```bash
# 1. Update requirements.txt (remove deprecated lines, update versions)
# 2. Update package.json (Mantine 8.3.6)
# 3. Install
pip install -r requirements.txt --upgrade
npm install
# 4. Try running
python run.py
```

### 2. Functionality Testing Checklist
- [ ] App starts without errors
- [ ] Home page loads
- [ ] Example doc page loads (`/pip/example`)
- [ ] Search works (Select component in header)
- [ ] Theme toggle works (light/dark mode)
- [ ] Mobile menu works (hamburger button)
- [ ] Code highlighting renders
- [ ] Table of contents renders
- [ ] Component props tables render (kwargs directive)

### 3. Visual Testing Checklist
- [ ] AppShell layout correct
- [ ] Header looks right
- [ ] Navbar/sidebar looks right
- [ ] Content spacing/padding correct
- [ ] Dark mode colors correct
- [ ] Mobile responsive design works
- [ ] Icons render

### 4. Interactive Testing
- [ ] Click links - navigation works
- [ ] Search and select component - navigates correctly
- [ ] Theme toggle - switches smoothly
- [ ] Mobile drawer - opens/closes
- [ ] Any callbacks in examples work

---

## Rollback Plan

If migration fails, you can rollback:

```bash
# 1. Revert requirements.txt and package.json
git checkout requirements.txt package.json

# 2. Reinstall old versions
pip install -r requirements.txt
npm install

# 3. Revert code changes
git checkout components/appshell.py run.py
```

---

## Known Gotchas

### 1. markdown2dash Compatibility
The `markdown2dash` package may or may not be compatible with latest DMC. Monitor for:
- Errors in directive rendering
- Missing components
- Styling issues

**Mitigation:** Check markdown2dash GitHub for updates, or fork if needed.

### 2. Frontmatter Parsing
You use `python-frontmatter` to parse markdown metadata. Ensure it still works with updated dependencies.

### 3. Docker Build
After updating dependencies, rebuild Docker image to catch any issues:
```bash
docker build -t dash-docs-boilerplate .
```

If build fails, likely missing system dependencies or incompatible versions.

### 4. Notification API
If you add notification functionality later, the API has changed significantly in DMC 2.x. Refer to DMC docs for new API.

---

## Post-Migration TODO

1. **Update README.md**
   - Update installation instructions with new versions
   - Note minimum Python version (3.11+)
   - Update any screenshots if UI changed

2. **Update .gitignore**
   - Ensure all cache/build dirs ignored
   - Add any new build artifacts

3. **Consider Adding**
   - `requirements-lock.txt` for reproducible builds
   - `package-lock.json` committed to repo
   - GitHub Actions for CI/CD testing

4. **Documentation**
   - Add migration notes for users
   - Document any new features from DMC 2.x
   - Update contributing guide if needed

---

## Questions to Consider

1. **Do you use notifications anywhere?**
   - If yes, you'll need to learn the new NotificationContainer API
   - If no, the change is simple (just rename component)

2. **Do you have any custom Carousel usage?**
   - If yes, check for `draggable` or `speed` props (removed)
   - Update to use `emblaOptions` instead

3. **Do you use DatePicker or DateTimePicker?**
   - Verify prop names haven't changed
   - Test date selection still works

4. **Any custom CSS targeting Mantine classes?**
   - Mantine 8 may have different internal class names
   - Test and update as needed

---

## Useful Commands

```bash
# Check installed versions
pip list | grep -E "(dash|mantine|plotly)"
npm list --depth=0 | grep mantine

# Find deprecated imports in code
grep -r "import dash_html_components" .
grep -r "import dash_core_components" .
grep -r "import dash_table" .

# Find potential issues in code
grep -r "NotificationProvider" .
grep -r "data-hovered" assets/
grep -r "run_server" .

# Test build
python -c "import dash; import dash_mantine_components; print('OK')"

# Run with verbose output
python run.py 2>&1 | tee migration.log
```

---

## Success Indicators

You'll know migration is successful when:

1. ✅ No errors on `pip install -r requirements.txt`
2. ✅ No errors on `npm install`
3. ✅ No import errors when running app
4. ✅ No console warnings about deprecated features
5. ✅ App starts and loads without errors
6. ✅ All interactive features work
7. ✅ Visual appearance is correct
8. ✅ Docker build succeeds
9. ✅ Tests pass (if any)

---

## Getting Help

If you encounter issues:

1. Check DMC migration guide: https://www.dash-mantine-components.com/migration
2. Check Dash migration guide: https://dash.plotly.com/migration
3. Review dmc-docs for reference implementation
4. Search DMC GitHub issues
5. Post in Dash Community forum

---

*Prepared for migration from DMC 0.14.7 → 2.4.0 and Dash 2.5.0 → 3.2.0*
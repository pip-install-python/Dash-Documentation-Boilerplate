# Code Changes Summary - Dash 3.x & DMC 2.4.0 Migration

This document provides a quick reference for all code changes needed during migration.

---

## Files That Need Changes

### 🔴 CRITICAL CHANGES (Required)

#### 1. `requirements.txt`
**What:** Remove deprecated package lines, update version constraints

**Changes:**
```diff
  flask>=1.0.4
+ flask>=3.0.0
  importlib-metadata
  nest-asyncio
  pandas>=1.2.3
  plotly>=5.0.0
  requests
  retrying
  setuptools
  typing-extensions>=4.1.1

- dash-html-components>=2.0.0
- dash_table>=5.0.0
- dash-core-components>=2.0.0

- dash>=2.5.0
+ dash>=3.0.0
  dash-iconify>=0.1.0
  requests>=2.27.1
  python-frontmatter>=1.0.0
- dash-mantine-components>=0.14.7
+ dash-mantine-components>=2.4.0
  pydantic>=2.3.0
  gunicorn>=21.2.0
  markdown2dash
```

**Why:** Dash 3.0 removed stub packages; DMC 2.4.0 is latest version

**File location:** `/requirements.txt`

---

#### 2. `package.json`
**What:** Update all Mantine packages from 7.14.1 to 8.3.6

**Changes:**
```diff
  "dependencies": {
-   "@mantine/carousel": "7.14.1",
+   "@mantine/carousel": "8.3.6",
-   "@mantine/charts": "7.14.1",
+   "@mantine/charts": "8.3.6",
-   "@mantine/code-highlight": "7.14.1",
+   "@mantine/code-highlight": "8.3.6",
-   "@mantine/core": "7.14.1",
+   "@mantine/core": "8.3.6",
-   "@mantine/dates": "7.14.1",
+   "@mantine/dates": "8.3.6",
-   "@mantine/hooks": "7.14.1",
+   "@mantine/hooks": "8.3.6",
-   "@mantine/notifications": "7.14.1",
+   "@mantine/notifications": "8.3.6",
-   "@mantine/nprogress": "7.14.1",
+   "@mantine/nprogress": "8.3.6",
-   "@mantine/spotlight": "7.14.1",
+   "@mantine/spotlight": "8.3.6",
    "dayjs": "^1.11.10",
    "embla-carousel-auto-scroll": "^8.4.0",
    "embla-carousel-autoplay": "^8.4.0",
    "embla-carousel-react": "^8.4.0",
    "is-absolute-url": "^4.0.1",
    "jsonpath": "^1.1.1",
    "recharts": "^2.13.3"
  }
```

**Why:** DMC 2.4.0 is built on Mantine 8.3.6; version mismatch causes issues

**File location:** `/package.json`

---

#### 3. `components/appshell.py`
**What:** Update NotificationProvider to NotificationContainer

**Changes:**
```diff
  children=[
      dcc.Location(id="url", refresh="callback-nav"),
      dcc.Store(id="color-scheme-storage", storage_type="local"),
-     dmc.NotificationProvider(),
+     dmc.NotificationContainer(),
      dmc.AppShell(
          [
              create_header(data),
```

**Why:** NotificationProvider deprecated in DMC 2.0+

**File location:** `/components/appshell.py` (line 51)

**Impact:** If you use notifications anywhere, the API has changed. See DMC docs for new API.

---

### 🟡 RECOMMENDED CHANGES (Optional but advised)

#### 4. `run.py`
**What:** Update app.run_server() to app.run()

**Changes:**
```diff
  if __name__ == "__main__":
-     app.run_server(debug=False, host='0.0.0.0', port='8552')
+     app.run(debug=False, host='0.0.0.0', port='8552')
```

**Why:** `run_server()` deprecated in Dash 3.0

**File location:** `/run.py` (line 38)

**Impact:** Low - old method still works but may be removed in future

---

#### 5. `run.py` (React version)
**What:** Consider removing explicit React version setting

**Changes:**
```diff
  from dash import Dash, _dash_renderer
  import json
  from flask import jsonify
  from components.appshell import create_appshell
  import dash_mantine_components as dmc

- _dash_renderer._set_react_version("18.2.0")
+ # No longer needed - Dash 3.0 defaults to React 18.3.1
+ # Keep if you specifically need 18.2.0 instead of 18.3.1
```

**Why:** Dash 3.0 defaults to React 18.3.1

**File location:** `/run.py` (line 8)

**Decision:** Keep it if you want exact version control, or remove to use Dash's default

---

### ✅ NO CHANGES NEEDED

The following files are already compatible with Dash 3.x and DMC 2.4.0:

#### `components/header.py`
- ✅ Uses modern DMC component props
- ✅ `visibleFrom`/`hiddenFrom` correct
- ✅ Select component props compatible
- ✅ ActionIcon usage correct
- ✅ Clientside callbacks properly structured

#### `components/navbar.py`
- ✅ AppShellNavbar usage correct
- ✅ Drawer props compatible
- ✅ Anchor components OK
- ✅ ScrollArea works fine

#### `lib/constants.py`
- ✅ Just constants, no changes needed

#### `lib/directives/kwargs.py`
- ⚠️ Should work, but test component introspection
- Uses `importlib` and `inspect` - should be compatible

#### `lib/directives/source.py`
- ✅ CodeHighlightTabs usage correct
- ✅ File reading and icon display should work

#### `lib/directives/toc.py`
- ✅ AppShellAside usage correct
- ✅ Rendering logic should work

#### `pages/home.py`
- ✅ Container usage correct
- ✅ Markdown rendering compatible

#### `pages/markdown.py`
- ⚠️ Should work, verify markdown2dash compatibility
- ✅ Uses correct imports
- ✅ Page registration API unchanged

#### `assets/main.css`
- ✅ No `data-hovered` selectors found
- ✅ Mantine class overrides should still work
- ⚠️ Monitor for any Mantine 8 class name changes

#### `assets/m2d.css`
- ✅ Custom markdown styling
- ✅ Should work unchanged

#### `templates/index.html`
- ✅ Standard Dash template
- ✅ No changes needed

#### `Dockerfile`
- ✅ Python 3.11.8 is good
- ✅ Build process should work
- ⚠️ Will pick up new requirements.txt and package.json

#### `docker-compose.yml`
- ✅ Configuration looks good
- ✅ No changes needed

---

## Complete File-by-File Summary

| File | Change Type | Difficulty | Priority | Estimated Time |
|------|-------------|-----------|----------|----------------|
| `requirements.txt` | Update | Easy | 🔴 Critical | 5 min |
| `package.json` | Update | Easy | 🔴 Critical | 5 min |
| `components/appshell.py` | Code change | Easy | 🔴 Critical | 2 min |
| `run.py` | Code change | Easy | 🟡 Recommended | 1 min |
| `components/header.py` | None | - | ✅ OK | - |
| `components/navbar.py` | None | - | ✅ OK | - |
| `lib/constants.py` | None | - | ✅ OK | - |
| `lib/directives/kwargs.py` | Test only | - | ⚠️ Monitor | 5 min |
| `lib/directives/source.py` | Test only | - | ⚠️ Monitor | 2 min |
| `lib/directives/toc.py` | Test only | - | ⚠️ Monitor | 2 min |
| `pages/home.py` | None | - | ✅ OK | - |
| `pages/markdown.py` | Test only | - | ⚠️ Monitor | 5 min |
| `assets/main.css` | Verify only | - | ⚠️ Monitor | 5 min |
| `assets/m2d.css` | None | - | ✅ OK | - |
| `templates/index.html` | None | - | ✅ OK | - |
| `Dockerfile` | None | - | ✅ OK | - |
| `docker-compose.yml` | None | - | ✅ OK | - |

**Total Code Changes:** 3-5 files (depending on optional changes)
**Total Time for Changes:** ~15-20 minutes
**Total Time for Testing:** 2-3 hours

---

## Step-by-Step Implementation Order

Follow this order for smoothest migration:

### Step 1: Backup
```bash
git add -A
git commit -m "Pre-migration backup"
git tag pre-migration-backup
git checkout -b migration/dash3-dmc2.4
```

### Step 2: Update Dependencies (10 min)
1. Update `requirements.txt` (5 min)
2. Update `package.json` (5 min)
3. Install: `pip install -r requirements.txt --upgrade && npm install`

### Step 3: Update Code (5 min)
1. Update `components/appshell.py` - NotificationProvider → NotificationContainer (2 min)
2. Update `run.py` - run_server() → run() (1 min)
3. (Optional) Remove React version line in `run.py` (1 min)

### Step 4: Test (2-3 hours)
1. Start app: `python run.py`
2. Test all functionality (see MIGRATION_CHECKLIST.md)
3. Test Docker build and run

### Step 5: Commit
```bash
git add -A
git commit -m "Migrate to Dash 3.x and DMC 2.4.0"
git tag v0.2.0
```

---

## Quick Command Reference

```bash
# Backup
git tag pre-migration-backup

# Create migration branch
git checkout -b migration/dash3-dmc2.4

# Install updated dependencies
pip install -r requirements.txt --upgrade
npm install

# Test installation
python -c "import dash; import dash_mantine_components as dmc; print(f'Dash: {dash.__version__}, DMC: {dmc.__version__}')"

# Check installed versions
pip list | grep -E "(dash|mantine|plotly)"
npm list --depth=0 | grep mantine

# Run app
python run.py

# Test Docker
docker build -t dash-docs-boilerplate .
docker run -p 8550:8550 dash-docs-boilerplate

# Rollback if needed
git checkout pre-migration-backup
pip install -r requirements.txt
npm install
```

---

## Common Issues & Solutions

### Issue 1: "No module named 'dash_html_components'"
**Cause:** Old import in code somewhere
**Solution:** Search and replace:
```bash
grep -r "import dash_html_components" .
# Replace with: from dash import html
```

### Issue 2: "NotificationProvider not found"
**Cause:** Forgot to change to NotificationContainer
**Solution:** Update `components/appshell.py` line 51

### Issue 3: Mantine version mismatch warnings
**Cause:** package.json not updated
**Solution:** Update all @mantine packages to 8.3.6, then `npm install`

### Issue 4: Styles look different
**Cause:** Mantine 8 has some style changes
**Solution:** Review CSS, update if needed

### Issue 5: Docker build fails
**Cause:** New dependencies incompatible
**Solution:** Check Dockerfile pip/npm versions, update if needed

---

## Verification Commands

After making changes, run these to verify:

```bash
# 1. Check Python imports work
python -c "from dash import html, dcc, dash_table; import dash_mantine_components as dmc; print('Imports OK')"

# 2. Check versions
python -c "import dash; import dash_mantine_components as dmc; print(f'Dash: {dash.__version__}, DMC: {dmc.__version__}')"

# 3. Start app and check for errors
python run.py
# Look for any errors in terminal

# 4. Check for deprecation warnings
python run.py 2>&1 | grep -i "deprecat"

# 5. Verify Docker build
docker build -t dash-docs-boilerplate . && echo "Build OK"
```

---

## What Success Looks Like

When migration is successful, you should see:

```bash
$ python -c "import dash; import dash_mantine_components as dmc; print(f'Dash: {dash.__version__}, DMC: {dmc.__version__}')"
Dash: 3.2.0, DMC: 2.4.0

$ python run.py
Dash is running on http://0.0.0.0:8552/

 * Serving Flask app 'run'
 * Debug mode: off
```

And in browser:
- ✅ No console errors
- ✅ App loads correctly
- ✅ Theme switching works
- ✅ Navigation works
- ✅ All features functional

---

*This summary provides quick reference for all code changes needed during migration.*
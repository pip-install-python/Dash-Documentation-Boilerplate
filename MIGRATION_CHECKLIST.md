# Migration Checklist - Step-by-Step Guide

Use this checklist to track your migration progress. Check off items as you complete them.

---

## Pre-Migration Preparation

- [ ] **Backup current working state**
  ```bash
  git add -A
  git commit -m "Pre-migration backup - DMC 0.14.7, Dash 2.5.0"
  git tag pre-migration-backup
  ```

- [ ] **Create migration branch**
  ```bash
  git checkout -b migration/dash3-dmc2.4
  ```

- [ ] **Review claude.md and MIGRATION_NOTES.md**
  - Read through both documents
  - Understand breaking changes
  - Note any custom code that might be affected

- [ ] **Verify current app works**
  ```bash
  python run.py
  # Visit http://localhost:8552
  # Test basic functionality
  ```

- [ ] **Document current behavior**
  - Take screenshots of key pages
  - Note any existing bugs or issues
  - List all features to test after migration

---

## Phase 1: Update Dependencies (Est. 30 min)

### 1.1 Update requirements.txt
- [ ] **Backup original file**
  ```bash
  cp requirements.txt requirements-OLD.txt
  ```

- [ ] **Remove deprecated lines**
  - [ ] Delete line: `dash-html-components>=2.0.0`
  - [ ] Delete line: `dash_table>=5.0.0`
  - [ ] Delete line: `dash-core-components>=2.0.0`

- [ ] **Update version constraints**
  - [ ] Change `dash>=2.5.0` to `dash>=3.0.0`
  - [ ] Change `dash-mantine-components>=0.14.7` to `dash-mantine-components>=2.4.0`
  - [ ] Update `flask>=1.0.4` to `flask>=3.0.0` (recommended)

- [ ] **Verify final requirements.txt**
  - Reference `requirements-NEW.txt` for comparison
  - Ensure no deprecated packages remain

### 1.2 Update package.json
- [ ] **Backup original file**
  ```bash
  cp package.json package-OLD.json
  ```

- [ ] **Update Mantine packages to 8.3.6**
  - [ ] `@mantine/carousel`: `7.14.1` → `8.3.6`
  - [ ] `@mantine/charts`: `7.14.1` → `8.3.6`
  - [ ] `@mantine/code-highlight`: `7.14.1` → `8.3.6`
  - [ ] `@mantine/core`: `7.14.1` → `8.3.6`
  - [ ] `@mantine/dates`: `7.14.1` → `8.3.6`
  - [ ] `@mantine/hooks`: `7.14.1` → `8.3.6`
  - [ ] `@mantine/notifications`: `7.14.1` → `8.3.6`
  - [ ] `@mantine/nprogress`: `7.14.1` → `8.3.6`
  - [ ] `@mantine/spotlight`: `7.14.1` → `8.3.6`

- [ ] **Update version number (optional)**
  - [ ] Change `"version": "0.1.0"` to `"version": "0.2.0"`

- [ ] **Verify final package.json**
  - Reference `package-NEW.json` for comparison
  - Ensure all Mantine packages are 8.3.6

### 1.3 Install Updated Dependencies
- [ ] **Install Python dependencies**
  ```bash
  pip install -r requirements.txt --upgrade
  ```
  - [ ] No errors during installation
  - [ ] Note any warnings

- [ ] **Install Node dependencies**
  ```bash
  npm install
  ```
  - [ ] No errors during installation
  - [ ] Note any warnings

- [ ] **Verify installed versions**
  ```bash
  pip list | grep -E "(dash|mantine|plotly)"
  npm list --depth=0 | grep mantine
  ```
  - [ ] dash >= 3.0.0
  - [ ] dash-mantine-components >= 2.4.0
  - [ ] All @mantine packages = 8.3.6

---

## Phase 2: Update Code (Est. 1-2 hours)

### 2.1 Update run.py
- [ ] **Backup original file**
  ```bash
  cp run.py run-OLD.py
  ```

- [ ] **Update app.run_server() → app.run()**
  - [ ] Change line 38: `app.run_server(...)` → `app.run(...)`
  - [ ] Keep same parameters: `debug=False, host='0.0.0.0', port='8552'`

- [ ] **Review React version setting (optional)**
  - [ ] Consider removing line 8 (Dash 3.0 defaults to React 18.3.1)
  - [ ] Or keep it to maintain exact version (18.2.0)
  - Decision: ⬜ Keep ⬜ Remove

### 2.2 Update components/appshell.py (CRITICAL)
- [ ] **Backup original file**
  ```bash
  cp components/appshell.py components/appshell-OLD.py
  ```

- [ ] **Update NotificationProvider → NotificationContainer**
  - [ ] Change line 51: `dmc.NotificationProvider()` → `dmc.NotificationContainer()`

- [ ] **Verify MantineProvider config**
  - [ ] Theme config looks correct
  - [ ] primaryColor is set
  - [ ] Component default props are valid

- [ ] **Verify AppShell config**
  - [ ] `header={"height": 70}` - valid
  - [ ] `navbar` config - valid
  - [ ] `aside` config - valid

- [ ] **Check clientside callbacks**
  - [ ] Color scheme toggle callback
  - [ ] Both callbacks have proper syntax

### 2.3 Review Other Components
- [ ] **components/header.py**
  - [ ] Check for any deprecated props
  - [ ] Verify Select component props
  - [ ] ActionIcon usage looks good
  - Status: ⬜ No changes needed ⬜ Changes made

- [ ] **components/navbar.py**
  - [ ] AppShellNavbar usage correct
  - [ ] Drawer props valid
  - [ ] Anchor components OK
  - Status: ⬜ No changes needed ⬜ Changes made

### 2.4 Review Lib/Directives
- [ ] **lib/directives/kwargs.py**
  - [ ] Test component introspection still works
  - Status: ⬜ No changes needed ⬜ Changes made

- [ ] **lib/directives/source.py**
  - [ ] CodeHighlightTabs usage correct
  - [ ] File reading works
  - Status: ⬜ No changes needed ⬜ Changes made

- [ ] **lib/directives/toc.py**
  - [ ] AppShellAside usage correct
  - [ ] Rendering works
  - Status: ⬜ No changes needed ⬜ Changes made

### 2.5 Review Pages
- [ ] **pages/markdown.py**
  - [ ] markdown2dash import works
  - [ ] Page registration works
  - [ ] Title rendering OK
  - Status: ⬜ No changes needed ⬜ Changes made

- [ ] **pages/home.py**
  - [ ] Container usage correct
  - [ ] Markdown rendering works
  - Status: ⬜ No changes needed ⬜ Changes made

### 2.6 Review CSS (if needed)
- [ ] **Check assets/main.css**
  - [ ] Search for `data-hovered` - should find none
  - [ ] Verify Mantine class overrides still valid
  - [ ] Check any custom selectors
  - Status: ⬜ No changes needed ⬜ Changes made

- [ ] **Check assets/m2d.css**
  - [ ] Markdown styling classes
  - [ ] No deprecated selectors
  - Status: ⬜ No changes needed ⬜ Changes made

---

## Phase 3: Testing (Est. 2-3 hours)

### 3.1 Basic Functionality Tests
- [ ] **App starts successfully**
  ```bash
  python run.py
  ```
  - [ ] No import errors
  - [ ] No startup errors
  - [ ] Server runs on port 8552

- [ ] **Home page loads**
  - [ ] Visit http://localhost:8552/
  - [ ] Page renders without errors
  - [ ] No console errors in browser
  - [ ] Images load correctly

- [ ] **Example documentation page loads**
  - [ ] Visit http://localhost:8552/pip/example
  - [ ] Page renders correctly
  - [ ] Markdown content displays
  - [ ] No console errors

### 3.2 Component Functionality Tests
- [ ] **Header components**
  - [ ] Logo displays and links to home
  - [ ] Search (Select component) works
    - [ ] Can open dropdown
    - [ ] Can search for pages
    - [ ] Selecting navigates to page
  - [ ] GitHub link works
  - [ ] Theme toggle button visible

- [ ] **Theme switching**
  - [ ] Click theme toggle
  - [ ] Switches from light to dark
  - [ ] Click again, switches back
  - [ ] Colors change appropriately
  - [ ] No visual glitches
  - [ ] Theme persists on reload

- [ ] **Navigation**
  - [ ] Sidebar (navbar) displays
  - [ ] Links are clickable
  - [ ] Navigation works correctly
  - [ ] Active page highlighted (if implemented)

- [ ] **Mobile responsive**
  - [ ] Resize browser to mobile width
  - [ ] Hamburger menu appears
  - [ ] Click hamburger - drawer opens
  - [ ] Drawer displays navigation
  - [ ] Drawer can close
  - [ ] All mobile navigation works

### 3.3 Documentation Features Tests
- [ ] **Table of contents**
  - [ ] TOC appears on right side (if on wide screen)
  - [ ] Links are generated correctly
  - [ ] Clicking TOC link scrolls to section
  - [ ] Smooth scrolling works

- [ ] **Code highlighting**
  - [ ] Code blocks display with syntax highlighting
  - [ ] Multiple languages work (Python, CSS, etc.)
  - [ ] Code is readable in both themes
  - [ ] Copy button works (if implemented)

- [ ] **Interactive examples**
  - [ ] Example components render
  - [ ] Callbacks work
  - [ ] Interactivity functions (buttons, graphs, etc.)
  - [ ] No errors in examples

- [ ] **Component props tables (kwargs directive)**
  - [ ] Props tables render
  - [ ] Columns display correctly
  - [ ] Content is readable
  - [ ] Tables are styled correctly

### 3.4 Visual/Style Tests
- [ ] **Layout**
  - [ ] AppShell structure correct
  - [ ] Header height correct (70px)
  - [ ] Sidebar width correct (300px)
  - [ ] Content area spacing good

- [ ] **Typography**
  - [ ] Font family correct (Inter)
  - [ ] Heading sizes appropriate
  - [ ] Text is readable
  - [ ] Line heights good

- [ ] **Colors**
  - [ ] Primary color (teal) applies
  - [ ] Light mode colors correct
  - [ ] Dark mode colors correct
  - [ ] Links are visible
  - [ ] Contrast is good

- [ ] **Spacing**
  - [ ] Padding between sections
  - [ ] Margin on elements
  - [ ] No overlapping content
  - [ ] Content not cramped

### 3.5 Performance Tests
- [ ] **Load times**
  - [ ] Initial page load < 3 seconds
  - [ ] Navigation between pages is fast
  - [ ] No lag when switching themes

- [ ] **Console errors**
  - [ ] Open browser dev tools
  - [ ] Check console - no errors
  - [ ] Check network tab - all assets load
  - [ ] No 404s or failed requests

- [ ] **Deprecation warnings**
  - [ ] Check terminal output
  - [ ] No deprecation warnings about Dash components
  - [ ] No warnings about DMC components
  - [ ] No warnings about React version

---

## Phase 4: Docker Testing (Est. 1 hour)

### 4.1 Update Docker Configuration (if needed)
- [ ] **Review Dockerfile**
  - [ ] Python version (3.11.8) is good
  - [ ] pip install steps correct
  - [ ] Port (8550) is correct
  - Status: ⬜ No changes needed ⬜ Changes made

- [ ] **Review docker-compose.yml**
  - [ ] Version and config look good
  - Status: ⬜ No changes needed ⬜ Changes made

### 4.2 Build and Test Docker Image
- [ ] **Build Docker image**
  ```bash
  docker build -t dash-docs-boilerplate .
  ```
  - [ ] Build completes successfully
  - [ ] No build errors
  - [ ] All dependencies install

- [ ] **Run Docker container**
  ```bash
  docker run -p 8550:8550 dash-docs-boilerplate
  ```
  - [ ] Container starts
  - [ ] App runs in container
  - [ ] No runtime errors

- [ ] **Test app in container**
  - [ ] Visit http://localhost:8550/
  - [ ] Home page loads
  - [ ] Navigation works
  - [ ] All features functional
  - [ ] Stop container: Ctrl+C

- [ ] **Test with docker-compose**
  ```bash
  docker-compose up
  ```
  - [ ] Service starts
  - [ ] App accessible
  - [ ] Stop: `docker-compose down`

---

## Phase 5: Documentation & Cleanup (Est. 1 hour)

### 5.1 Update Documentation
- [ ] **Update README.md**
  - [ ] Update dependency versions mentioned
  - [ ] Update installation instructions if needed
  - [ ] Note Python 3.11+ requirement
  - [ ] Add migration notes section

- [ ] **Create/Update CHANGELOG.md**
  - [ ] Document version update
  - [ ] List breaking changes
  - [ ] List new features (if any)
  - [ ] Credit migration to Dash 3.0 & DMC 2.4.0

### 5.2 Clean Up
- [ ] **Remove backup files (optional)**
  ```bash
  rm requirements-OLD.txt
  rm package-OLD.json
  rm run-OLD.py
  rm components/appshell-OLD.py
  ```
  - Or keep them for reference

- [ ] **Remove migration files from repo (optional)**
  - [ ] Keep claude.md for future reference
  - [ ] Keep MIGRATION_NOTES.md for reference
  - [ ] Add to .gitignore if desired

### 5.3 Git Commit
- [ ] **Stage all changes**
  ```bash
  git add -A
  ```

- [ ] **Commit with descriptive message**
  ```bash
  git commit -m "Migrate to Dash 3.x and DMC 2.4.0

  - Updated dependencies: Dash 2.5→3.2, DMC 0.14.7→2.4.0
  - Updated Mantine packages from 7.14.1 to 8.3.6
  - Removed deprecated package imports
  - Updated NotificationProvider to NotificationContainer
  - Updated app.run_server() to app.run()
  - All tests passing
  - Docker deployment verified"
  ```

- [ ] **Tag release (optional)**
  ```bash
  git tag v0.2.0
  ```

---

## Phase 6: Post-Migration

### 6.1 Verify Everything Works
- [ ] **Final smoke test**
  - [ ] Start fresh: `python run.py`
  - [ ] Test all major features
  - [ ] Check both light and dark themes
  - [ ] Test on mobile/responsive
  - [ ] Check Docker still works

### 6.2 Monitor for Issues
- [ ] **Watch for edge cases**
  - [ ] Use app for a day
  - [ ] Try different browsers
  - [ ] Test with different content
  - [ ] Note any issues found

### 6.3 Update Dependencies Regularly
- [ ] **Set reminder to check for updates**
  - [ ] Monthly: Check for DMC updates
  - [ ] Monthly: Check for Dash updates
  - [ ] Quarterly: Update all dependencies

---

## Rollback Plan (If Needed)

If migration fails and you need to rollback:

- [ ] **Checkout pre-migration state**
  ```bash
  git checkout pre-migration-backup
  ```

- [ ] **Reinstall old dependencies**
  ```bash
  pip install -r requirements.txt
  npm install
  ```

- [ ] **Verify old version works**
  ```bash
  python run.py
  ```

- [ ] **Document what went wrong**
  - Make notes for future migration attempt
  - Search for solutions to issues encountered

---

## Success Criteria

Migration is successful when ALL of these are true:

- ✅ No import or startup errors
- ✅ All pages load without errors
- ✅ All navigation works
- ✅ Theme switching works
- ✅ Search functionality works
- ✅ Mobile responsive design works
- ✅ All markdown directives work
- ✅ Code highlighting works
- ✅ Interactive examples work
- ✅ Docker deployment works
- ✅ No deprecation warnings
- ✅ No console errors

---

## Notes & Issues Encountered

Use this space to document any issues you encounter during migration:

### Issues Found
1.

### Solutions Applied
1.

### Open Questions
1.

---

## Estimated Time Investment

- **Phase 1** (Dependencies): ☐ Started: _____ ☐ Completed: _____ (Est: 30 min)
- **Phase 2** (Code Updates): ☐ Started: _____ ☐ Completed: _____ (Est: 1-2 hours)
- **Phase 3** (Testing): ☐ Started: _____ ☐ Completed: _____ (Est: 2-3 hours)
- **Phase 4** (Docker): ☐ Started: _____ ☐ Completed: _____ (Est: 1 hour)
- **Phase 5** (Documentation): ☐ Started: _____ ☐ Completed: _____ (Est: 1 hour)

**Total Estimated Time:** 4-6 hours
**Actual Time Spent:** _____ hours

---

**Migration Started:** _______________
**Migration Completed:** _______________
**Migration Status:** ⬜ In Progress ⬜ Completed ✅ ⬜ Rolled Back ⬜ Paused

---

*Use this checklist to track your migration step-by-step. Good luck!*
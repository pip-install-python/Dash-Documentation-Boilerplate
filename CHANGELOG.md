# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-11-10

### Added
- **LLM Copy Button Directive** (`.. llms_copy::`)
  - New custom directive that adds a "Copy for llm 📋" button to documentation pages
  - Copies the page's `/llms.txt` URL to clipboard for easy AI assistant sharing
  - Users can paste the URL into ChatGPT, Claude, or other AI assistants for context-aware help
  - Features:
    - Automatic URL construction based on current page path
    - Visual feedback with "✓ Copied! ✓" confirmation
    - Fallback clipboard method for non-HTTPS contexts (HTTP development servers)
    - Works across all modern browsers
    - Tooltip: "Copy llms.txt URL for AI assistants"
  - Implementation:
    - Python directive: `lib/directives/llms_copy.py`
    - JavaScript handler: `assets/llms_copy.js`
    - Uses both modern Clipboard API and legacy `execCommand` fallback
    - Mutation observer for Dash-rendered content detection
  - Documentation updated in Custom Directives guide
  - Added to all 5 example documentation pages

## [0.3.0] - 2025-11-09

### Added - Documentation System
- **Comprehensive Getting Started Guide** (385+ lines)
  - Detailed directive options documentation (`:code: false`, `:defaultExpanded`, `:withExpandedButton`)
  - Interactive examples with best practices
  - File structure examples and patterns
- **Custom Directives Guide** (476 lines)
  - Complete documentation for all 4 directives (toc, exec, source, kwargs)
  - 3 live Python examples (button, counter, form validation)
- **Data Visualization Guide** (465+ lines)
  - 5 chart type examples with full implementations
  - Plotly template integration guide
  - Real-time updates and dashboard patterns
- **Interactive Components Guide** (569 lines)
  - 6 callback pattern examples
  - State management, pattern matching, chained callbacks
  - Loading states demonstration
- **AI/LLM Integration Guide** (577 lines)
  - Complete dash-improve-my-llms documentation
  - SEO optimization strategies
  - Bot management and privacy controls

### Added - Theme System
- **DMC Figure Templates Integration**
  - All Plotly charts now use `dmc.add_figure_templates()`
  - Theme-aware callbacks for 6 chart examples
  - Charts dynamically update with light/dark theme toggle
  - Proper background rendering in both themes
- **Code Block Theming**
  - Theme-aware CSS for markdown code blocks
  - Proper syntax highlighting in light and dark modes
  - Inline code and code block styling
- **Comprehensive Theme Configuration**
  - Professional typography hierarchy (h1-h6)
  - Systematic 4px-based spacing scale
  - 5-level shadow system
  - Consistent border radius system
  - Global component defaults via theme.components
  - Softer black (#1a1b1e) for better contrast

### Added - UI/UX Enhancements
- **Navigation Improvements**
  - Custom page ordering (Getting Started → Custom Directives → AI/LLM → Interactive → Visualization)
  - Better visual hierarchy
  - Organized documentation sections
- **Typography System**
  - Inter font family across application
  - Optimized line heights (md: 1.55 for body text)
  - Proper font sizes (16px base)
  - Font smoothing and text rendering optimization
- **Layout Refinements**
  - Better responsive breakpoints (md for navbar)
  - Improved spacing consistency
  - Enhanced mobile experience
  - Better heading spacing (1.5em top, 0.5em bottom)

### Added - Production Features
- **SEO-Ready HTML Template**
  - Comprehensive meta tags with developer guidance
  - Open Graph and Twitter Card configuration
  - Structured data (Schema.org) for Organization and SoftwareApplication
  - Analytics integration (Google Analytics ready to enable)
  - Favicon configuration with multiple formats
  - Performance optimization (preconnect hints)
  - Search engine verification placeholders
  - Enhanced noscript fallback with styled content
  - 297 lines of documentation and configuration

### Improved
- **15 Working Python Examples**
  - Button interactions, counters, form validation
  - 5 chart types (bar, line, scatter, realtime, dashboard)
  - Callback patterns and state management
  - All examples theme-aware and fully functional
- **Directive System**
  - Fixed kwargs directive to parse component specifications (e.g., `dmc.Button`)
  - Better error handling and fallbacks
  - Support for directive options
- **Code Quality**
  - Fixed JSON serialization error (removed lambda from theme styles)
  - Better import statements
  - Comprehensive inline comments
  - Fixed DMC 2.4.0 compatibility issues

### Changed
- **Better Performance**
  - Optimized theme switching
  - Smooth transitions
  - Better font loading
- **Documentation Organization**
  - Clear learning path
  - Progressive complexity
  - Better code examples

### Fixed
- Import errors in example files (missing dmc, State imports)
- DMC 2.4.0 compatibility (removed unsupported `type` prop from TextInput)
- JSON serialization error in theme configuration
- Heading ID generation with code blocks in markdown
- Theme persistence and switching
- Code block rendering in dark mode

## [0.2.0] - 2025-11-09

### Changed
- **BREAKING**: Migrated from Dash 2.5.0+ to Dash 3.2.0
- **BREAKING**: Migrated from dash-mantine-components 0.14.7 to 2.4.0
- **BREAKING**: Updated all Mantine packages from 7.14.1 to 8.3.6
- Updated Flask from 1.0.4+ to 3.1.2
- Updated Plotly from 5.0.0+ to 6.4.0
- Updated `app.run_server()` to `app.run()` (Dash 3.x standard)

### Removed
- **BREAKING**: Removed deprecated package imports:
  - `dash-html-components` (now part of main `dash` package)
  - `dash-core-components` (now part of main `dash` package)
  - `dash_table` (now part of main `dash` package)

### Fixed
- Replaced deprecated `NotificationProvider` with `NotificationContainer`
- Fixed Mantine version mismatch between package.json and DMC version
- Added node_modules to .gitignore

### Added
- Added package-lock.json for reproducible npm builds
- Comprehensive migration documentation (8 detailed guides)
- Project analysis and assessment documentation
- Persistent theme preference storage using localStorage
- Browser color scheme preference detection on first visit
- Smooth theme transitions without page flash
- AI/LLM & SEO Integration (dash-improve-my-llms v0.3.0)
  - Automatic llms.txt, page.json, architecture.txt generation
  - SEO-optimized sitemap.xml with intelligent priority
  - Bot management (blocks AI training, allows AI search)
  - Structured data for better search indexing
  - Privacy controls for sensitive pages

### Improved
- Better dependency management with cleaner requirements.txt
- Improved code organization with inline comments
- Enhanced theme management system
- Better performance with latest Dash and DMC versions

## [0.1.0] - 2024-11-30

### Added
- Initial release of Dash Documentation Boilerplate
- Markdown-driven documentation system
- Support for light and dark themes
- Responsive design for mobile and desktop
- Docker deployment support
- Interactive code examples with syntax highlighting
- Custom markdown directives:
  - `toc` - Table of contents generation
  - `exec` - Executable Python code blocks
  - `source` - Source code display with syntax highlighting
  - `kwargs` - Component props documentation
- AppShell layout with header, navbar, and responsive drawer
- Search functionality for navigation
- Theme toggle with icon indicators
- Integration with dash-mantine-components (DMC)
- Integration with python-frontmatter for metadata
- Custom CSS styling system
- Docker and docker-compose configuration

### Documentation
- README with getting started guide
- Project structure documentation
- Example documentation pages

---

## Version History Summary

| Version | Date | Dash | DMC | Mantine | Python | Features |
|---------|------|------|-----|---------|--------|----------|
| 0.3.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Comprehensive docs, theme system, SEO |
| 0.2.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Migration to Dash 3.x, DMC 2.4.0, AI/LLM |
| 0.1.0 | 2024-11-30 | 2.5.0+ | 0.14.7 | 7.14.1 | 3.11+ | Initial release |

---

## Migration Guides

### Migrating to 0.3.0 from 0.2.0

Minor updates, mostly additive. Key changes:
1. Documentation content significantly expanded
2. Chart examples now use DMC figure templates
3. Enhanced SEO features in index.html
4. Better theme integration across all components

### Migrating to 0.2.0 from 0.1.0

Major breaking changes. See migration documentation:

- **Quick Start**: `MIGRATION_README.md`
- **Detailed Guide**: `claude.md`
- **Step-by-Step**: `MIGRATION_CHECKLIST.md`
- **Code Changes**: `CODE_CHANGES_SUMMARY.md`

Key changes to be aware of:
1. Update all imports from `dash_html_components` to `from dash import html`
2. Update all imports from `dash_core_components` to `from dash import dcc`
3. Replace `dmc.NotificationProvider()` with `dmc.NotificationContainer()`
4. Update custom components to use DMC 2.4.0 API
5. Check CSS for any Mantine 8 specific changes

---

## Support

- **Issues**: [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/discussions)
- **Dash Community**: [Plotly Community Forum](https://community.plotly.com/)

---

[unreleased]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/releases/tag/v0.1.0

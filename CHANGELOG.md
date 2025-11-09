# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Persistent theme preference storage using localStorage
- Browser color scheme preference detection on first visit
- Smooth theme transitions without page flash

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

| Version | Date | Dash | DMC | Mantine | Status |
|---------|------|------|-----|---------|--------|
| 0.2.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | Current |
| 0.1.0 | 2024-11-30 | 2.5.0+ | 0.14.7 | 7.14.1 | Legacy |

---

## Migration Guides

### Migrating to 0.2.0 from 0.1.0

If you have customized this boilerplate, see the migration documentation:

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

[unreleased]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/releases/tag/v0.1.0

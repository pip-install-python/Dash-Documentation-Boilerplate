# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2025-12-13

### Added
- **Custom Documentation-Aware TOON Generator** (`lib/toon_generator.py`)
  - Custom TOON route that processes raw markdown from `NAME_CONTENT_MAP`
  - Achieves **54.7% token reduction** vs llms.txt while preserving all content
  - Full directive awareness (exec, source, kwargs, toc, llms_copy)
  - Features:
    - Section extraction with hierarchical structure (h2-h6)
    - Directive parsing with option extraction
    - Source file embedding with smart code compression
    - Table and list preservation in compact format
    - Exec component detection with callback markers
    - Deduplication of code examples and directives
  - Smart code compression (`compress_code()`) that:
    - Preserves imports, function/class definitions
    - Keeps callback decorators and Input/Output patterns
    - Truncates long files with line count indicator
  - TOON v3.2 format with optimized output:
    - Compact section format: `[level] title`
    - Grouped directives by type
    - Inline table format with pipe separators
    - Key lists extraction for substantial bullet points

### Changed
- **Custom `/<page>/llms.toon` route** in `run.py`
  - Overrides default dash-improve-my-llms TOON for markdown pages
  - Uses raw markdown from NAME_CONTENT_MAP instead of rendered components
  - Processes source directives to embed actual file content

### Fixed
- **TOON content gap issue** - Previous TOON was only capturing 15-20% of documentation content
  - Root cause: dash-improve-my-llms extracts from rendered Dash components, losing directive context
  - Solution: Custom route processes raw markdown with full directive awareness
  - Previous TOON was 185% the size of llms.txt (27,669 chars vs 14,943 chars)
  - New TOON is 45.3% the size of llms.txt (6,965 chars vs 15,369 chars)

### Technical Details
- New module: `lib/toon_generator.py` (698 lines)
  - `generate_documentation_toon()` - Main entry point
  - `build_documentation_toon()` - TOON string builder
  - `extract_sections()` - Hierarchical section parser
  - `extract_directives()` - Directive extractor with options
  - `process_source_directive()` - File content reader
  - `process_exec_directive()` - Component metadata extractor
  - `compress_code()` - Smart code compression
  - `compress_section_content()` - Content summarization
  - `extract_tables()` / `extract_lists()` - Structure extractors

---

## [0.6.0] - 2025-12-13

### Added
- **Enhanced TOON Format v3.1** - Lossless semantic compression with 40-50% token reduction
  - Application context with related pages and multi-page awareness
  - Page purpose explanations with human-readable descriptions
  - Component breakdown with type distribution
  - Human-readable callback descriptions
  - Synthesized page summaries
  - Link categorization (internal vs external)

### Changed
- **Upgraded dash-improve-my-llms from v1.0.0 to v1.1.0**
  - Lossless semantic compression preserves all meaningful content
  - New content extraction: `extract_markdown_content()`, `parse_markdown_content()`
  - Smart compression: `compress_code_example()`, `compress_section_content()`
  - New helper functions: `_generate_page_summary()`, `_format_callback_description()`

### New TOONConfig Options
- `preserve_code_examples=True` - Include code snippets from markdown
- `preserve_headings=True` - Keep section structure
- `preserve_markdown=True` - Extract dcc.Markdown content
- `max_code_lines=30` - Max lines per code example
- `max_sections=20` - Max sections to include
- `max_content_items=100` - Increased from 20

### Documentation
- **Updated AI/LLM Integration Guide** with v1.1.0 TOON enhancements
  - Added design principle: lossless semantic compression
  - Updated token efficiency comparison table
  - Added 6 content gap examples (context, purpose, components, callbacks, summary, navigation)
  - Updated TOONConfig with new v1.1.0 options

### Improved
- Better content preservation in TOON format
- Optimal information density vs token reduction balance
- Enhanced developer experience with richer TOON output

---

## [0.5.0] - 2025-12-13

### Added
- **TOON Format Support** - Token-Oriented Object Notation for 50-60% fewer tokens
  - New `/llms.toon` endpoint for token-optimized LLM documentation
  - New `/architecture.toon` endpoint for token-optimized architecture
  - New `/<page>/llms.toon` per-page TOON format endpoints
  - TOON provides tabular arrays and explicit length markers for LLM validation
  - Ideal for API calls, large apps, and cost-conscious deployments

### Changed
- **Upgraded dash-improve-my-llms from v0.3.0 to v1.0.0**
  - Production-ready release with comprehensive test coverage (88 tests, 98% coverage)
  - New API exports: `TOONConfig`, `toon_encode`, `generate_llms_toon`, `generate_architecture_toon`
  - Zero-change migration: existing code works without modifications

### Documentation
- **Updated AI/LLM Integration Guide** with comprehensive TOON format documentation
  - Added TOON format section with benefits comparison table
  - Added example comparison (markdown vs TOON token usage)
  - Added TOONConfig configuration examples
  - Added programmatic TOON generation examples
  - Updated available routes table with new TOON endpoints
  - Updated key functions reference with new TOON imports

### Improved
- Better AI/LLM documentation organization
- Enhanced developer experience with new format options
- Cost optimization through token-efficient TOON format

---

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
| 0.6.0 | 2025-12-13 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Enhanced TOON v3.1, dash-improve-my-llms v1.1.0 |
| 0.5.0 | 2025-12-13 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | TOON format, dash-improve-my-llms v1.0.0 |
| 0.4.0 | 2025-11-10 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | LLM Copy Button directive |
| 0.3.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Comprehensive docs, theme system, SEO |
| 0.2.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Migration to Dash 3.x, DMC 2.4.0, AI/LLM |
| 0.1.0 | 2024-11-30 | 2.5.0+ | 0.14.7 | 7.14.1 | 3.11+ | Initial release |

---

## Migration Guides

### Migrating to 0.6.0 from 0.5.0

**Zero changes required!** The upgrade is fully backwards compatible.

Key changes:
1. Update `dash-improve-my-llms` in requirements.txt to `>=1.1.0`
2. TOON output now includes richer, lossless semantic content automatically

Optional new TOONConfig options:
```python
from dash_improve_my_llms import TOONConfig

app._toon_config = TOONConfig(
    # New in v1.1.0:
    preserve_code_examples=True,   # Include code snippets
    preserve_headings=True,        # Keep section structure
    preserve_markdown=True,        # Extract dcc.Markdown content
    max_code_lines=30,             # Max lines per code example
    max_sections=20,               # Max sections to include
    max_content_items=100,         # Increased from 20
)
```

### Migrating to 0.5.0 from 0.4.0

**Zero changes required!** The upgrade is fully backwards compatible.

Key changes:
1. Update `dash-improve-my-llms` in requirements.txt to `>=1.0.0`
2. New TOON endpoints are automatically available:
   - `/llms.toon` - Token-optimized LLM docs
   - `/architecture.toon` - Token-optimized architecture
   - `/<page>/llms.toon` - Per-page TOON format

Optional new features:
```python
# Configure TOON output (optional)
from dash_improve_my_llms import TOONConfig

app._toon_config = TOONConfig(
    indent=2,
    delimiter=",",
    include_metadata=True
)

# Programmatic TOON encoding (optional)
from dash_improve_my_llms import toon_encode
toon_string = toon_encode({"key": "value"})
```

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

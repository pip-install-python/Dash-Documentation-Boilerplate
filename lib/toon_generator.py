"""
Custom TOON generator for markdown-driven documentation.

This module generates documentation-aware TOON format from raw markdown
that contains custom directives (exec, source, kwargs, toc, llms_copy).

The key insight is that dash-improve-my-llms extracts from rendered Dash
components, but loses the directive context. This module works with the
raw markdown from NAME_CONTENT_MAP to preserve full documentation value.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class DirectiveType(Enum):
    """Types of custom markdown directives."""
    EXEC = "exec"
    SOURCE = "source"
    KWARGS = "kwargs"
    TOC = "toc"
    LLMS_COPY = "llms_copy"


@dataclass
class Section:
    """Represents a markdown section with heading and content."""
    level: int
    title: str
    content: str
    directives: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CodeExample:
    """Represents a code example from source directive or code block."""
    language: str
    code: str
    source_file: Optional[str] = None
    directive_type: Optional[str] = None
    description: Optional[str] = None


@dataclass
class DirectiveInfo:
    """Parsed directive information."""
    type: DirectiveType
    target: str
    options: Dict[str, Any] = field(default_factory=dict)
    line_number: int = 0


@dataclass
class TableInfo:
    """Represents a markdown table."""
    headers: List[str]
    rows: List[List[str]]
    title: Optional[str] = None


@dataclass
class ListInfo:
    """Represents a markdown list."""
    list_type: str  # 'ordered' or 'unordered'
    items: List[str]


# Language extension mapping
LANG_MAP = {
    'py': 'python', 'pyi': 'python',
    'js': 'javascript', 'jsx': 'jsx',
    'ts': 'typescript', 'tsx': 'tsx',
    'css': 'css', 'scss': 'scss', 'sass': 'sass', 'less': 'less',
    'html': 'html', 'htm': 'html', 'xml': 'xml',
    'json': 'json', 'yaml': 'yaml', 'yml': 'yaml',
    'md': 'markdown', 'rst': 'rst', 'txt': 'text',
    'sh': 'bash', 'bash': 'bash', 'zsh': 'bash',
    'sql': 'sql', 'r': 'r', 'toml': 'toml',
}


def extract_sections(markdown: str) -> List[Section]:
    """
    Extract hierarchical sections from markdown content.

    Handles:
    - ## Level 2 headings through ###### Level 6
    - Content between headings
    - Directives within sections
    """
    lines = markdown.split('\n')
    sections = []
    current_section = None
    content_lines = []

    heading_pattern = re.compile(r'^(#{2,6})\s+(.+)$')
    directive_pattern = re.compile(r'^\.\. (\w+)::(.*)$')

    for i, line in enumerate(lines):
        heading_match = heading_pattern.match(line)
        if heading_match:
            # Save previous section
            if current_section:
                current_section.content = '\n'.join(content_lines).strip()
                sections.append(current_section)

            # Start new section
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            # Remove any markdown formatting from title (like `code`)
            title = re.sub(r'`([^`]+)`', r'\1', title)
            current_section = Section(
                level=level,
                title=title,
                content='',
                directives=[]
            )
            content_lines = []
        else:
            content_lines.append(line)

            # Check for directives in this line
            directive_match = directive_pattern.match(line)
            if directive_match and current_section:
                current_section.directives.append({
                    'type': directive_match.group(1),
                    'target': directive_match.group(2).strip()
                })

    # Don't forget last section
    if current_section:
        current_section.content = '\n'.join(content_lines).strip()
        sections.append(current_section)

    return sections


def extract_directives(markdown: str) -> List[DirectiveInfo]:
    """Extract all directive references from markdown."""
    directives = []

    # Pattern matches: .. directive_name::target
    pattern = re.compile(r'^\.\. (\w+)::(.*)$', re.MULTILINE)

    for i, match in enumerate(pattern.finditer(markdown)):
        directive_name = match.group(1).lower()
        target = match.group(2).strip()

        try:
            dtype = DirectiveType(directive_name)
        except ValueError:
            # Unknown directive, skip
            continue

        # Extract options (lines starting with :option: after directive)
        options = {}
        start_pos = match.end()
        option_pattern = re.compile(r'^\s+:(\w+):\s*(.*)$', re.MULTILINE)
        remaining = markdown[start_pos:start_pos + 200]  # Look ahead 200 chars

        for opt_match in option_pattern.finditer(remaining):
            opt_name = opt_match.group(1)
            opt_value = opt_match.group(2).strip()
            # Convert string values to appropriate types
            if opt_value.lower() in ('true', 'false'):
                opt_value = opt_value.lower() == 'true'
            options[opt_name] = opt_value

        directives.append(DirectiveInfo(
            type=dtype,
            target=target,
            options=options,
            line_number=markdown[:match.start()].count('\n') + 1
        ))

    return directives


def process_source_directive(target: str) -> Optional[CodeExample]:
    """
    Process source directive - read actual file content.

    Args:
        target: File path like "docs/directives/button_example.py"

    Returns:
        CodeExample with file content, or None if file not found
    """
    # Handle comma-separated files (take first one)
    if ',' in target:
        target = target.split(',')[0].strip()

    file_path = Path(target)
    if not file_path.exists():
        return None

    try:
        content = file_path.read_text()
        ext = file_path.suffix.lstrip('.')
        language = LANG_MAP.get(ext, ext if ext else 'text')

        return CodeExample(
            language=language,
            code=content,
            source_file=target,
            directive_type="source"
        )
    except Exception:
        return None


def process_exec_directive(target: str) -> Dict[str, Any]:
    """
    Process exec directive - extract component metadata.

    Args:
        target: Module path like "docs.directives.button_example"

    Returns:
        Dict with module info and component metadata
    """
    # Convert module path to file path
    file_path = target.replace('.', '/') + '.py'
    path = Path(file_path)

    info = {
        'module': target,
        'file': file_path,
        'exists': path.exists(),
        'has_callback': False,
        'description': None
    }

    if path.exists():
        try:
            content = path.read_text()
            # Check for callback decorator
            info['has_callback'] = '@callback' in content or 'callback(' in content
            # Try to extract docstring or first comment
            docstring_match = re.search(r'^"""(.+?)"""', content, re.DOTALL)
            if docstring_match:
                info['description'] = docstring_match.group(1).strip().split('\n')[0]
        except Exception:
            pass

    return info


def compress_code(code: str, max_lines: int = 30, preserve_structure: bool = True) -> str:
    """
    Compress code while preserving understanding of structure.

    Args:
        code: Full code content
        max_lines: Maximum lines to include
        preserve_structure: If True, try to keep imports, class/function definitions

    Returns:
        Compressed code string
    """
    lines = code.split('\n')

    if len(lines) <= max_lines:
        return code

    if not preserve_structure:
        return '\n'.join(lines[:max_lines]) + f'\n# ... ({len(lines) - max_lines} more lines)'

    # Smart compression: keep imports, definitions, and key code
    result_lines = []
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track docstrings
        if '"""' in stripped or "'''" in stripped:
            if not in_docstring:
                in_docstring = True
                docstring_char = '"""' if '"""' in stripped else "'''"
                # Check if single-line docstring
                if stripped.count(docstring_char) >= 2:
                    in_docstring = False
            else:
                if docstring_char in stripped:
                    in_docstring = False
            continue

        if in_docstring:
            continue

        # Always keep these
        if (stripped.startswith('import ') or
            stripped.startswith('from ') or
            stripped.startswith('def ') or
            stripped.startswith('class ') or
            stripped.startswith('@') or
            stripped.startswith('component =') or
            'Output(' in stripped or
            'Input(' in stripped):
            result_lines.append(line)
        elif len(result_lines) < max_lines:
            result_lines.append(line)

        if len(result_lines) >= max_lines:
            break

    if len(lines) > len(result_lines):
        result_lines.append(f'# ... ({len(lines) - len(result_lines)} more lines)')

    return '\n'.join(result_lines)


def extract_markdown_code_blocks(markdown: str) -> List[CodeExample]:
    """Extract fenced code blocks from markdown."""
    pattern = re.compile(r'```(\w+)?\n(.*?)```', re.DOTALL)

    examples = []
    for match in pattern.finditer(markdown):
        lang = match.group(1) or 'text'
        code = match.group(2).strip()

        # Skip very short code blocks (likely inline examples)
        if len(code) < 20:
            continue

        examples.append(CodeExample(
            language=lang,
            code=code,
            directive_type='markdown_block'
        ))

    return examples


def extract_tables(markdown: str) -> List[TableInfo]:
    """Extract markdown tables with headers and rows."""
    tables = []

    # Pattern for markdown tables
    # Header row | col1 | col2 |
    # Separator  |------|------|
    # Data rows  | val1 | val2 |
    table_pattern = re.compile(
        r'(?:^|\n)\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)+)',
        re.MULTILINE
    )

    for match in table_pattern.finditer(markdown):
        header_row = match.group(1)
        body = match.group(2)

        # Parse headers
        headers = [h.strip() for h in header_row.split('|') if h.strip()]

        # Parse rows
        rows = []
        for row_line in body.strip().split('\n'):
            cells = [c.strip() for c in row_line.split('|') if c.strip()]
            if cells:
                rows.append(cells)

        if headers and rows:
            tables.append(TableInfo(headers=headers, rows=rows))

    return tables


def extract_lists(markdown: str) -> List[ListInfo]:
    """Extract bullet and numbered lists."""
    lists = []

    # Find bullet lists (-, *, +)
    bullet_pattern = re.compile(r'(?:^|\n)((?:[ ]*[-*+] .+\n?)+)', re.MULTILINE)
    for match in bullet_pattern.finditer(markdown):
        block = match.group(1).strip()
        items = []
        for line in block.split('\n'):
            line = line.strip()
            if line and line[0] in '-*+':
                items.append(line[1:].strip())
        if items:
            lists.append(ListInfo(list_type='unordered', items=items))

    # Find numbered lists
    numbered_pattern = re.compile(r'(?:^|\n)((?:[ ]*\d+\. .+\n?)+)', re.MULTILINE)
    for match in numbered_pattern.finditer(markdown):
        block = match.group(1).strip()
        items = []
        for line in block.split('\n'):
            line = line.strip()
            num_match = re.match(r'^\d+\.\s*(.+)$', line)
            if num_match:
                items.append(num_match.group(1))
        if items:
            lists.append(ListInfo(list_type='ordered', items=items))

    return lists


def compress_section_content(content: str, max_chars: int = 500) -> str:
    """
    Compress section content while preserving key information.

    Removes:
    - Directive lines (.. directive::)
    - Empty lines
    - Excessive whitespace

    Preserves:
    - First sentences of paragraphs
    - Key terminology
    """
    # Remove directive lines
    content = re.sub(r'^\.\. \w+::.+$', '', content, flags=re.MULTILINE)
    # Remove directive options
    content = re.sub(r'^\s+:\w+:.+$', '', content, flags=re.MULTILINE)
    # Collapse multiple newlines
    content = re.sub(r'\n{2,}', '\n', content)
    # Collapse whitespace
    content = re.sub(r'[ \t]+', ' ', content)
    # Strip
    content = content.strip()

    if len(content) <= max_chars:
        return content

    # Truncate at sentence boundary if possible
    truncated = content[:max_chars]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')

    cut_point = max(last_period, last_newline)
    if cut_point > max_chars // 2:
        return content[:cut_point + 1].strip()

    return truncated.strip() + '...'


def escape_toon_value(value: str) -> str:
    """Escape special characters in TOON values."""
    if not value:
        return '""'
    # If contains special chars, quote it
    if any(c in value for c in [',', ':', '\n', '"', "'"]):
        # Use double quotes and escape internal quotes
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


def generate_documentation_toon(
    page_path: str,
    page_name: str,
    page_description: str,
    raw_markdown: str,
    page_registry,
    base_url: str = ""
) -> str:
    """
    Generate documentation-optimized TOON from raw markdown.

    This is the main entry point - called from run.py route handler.

    Args:
        page_path: Page URL path (e.g., "/examples/directives")
        page_name: Page display name (e.g., "Custom Directives")
        page_description: Page description from frontmatter
        raw_markdown: Raw markdown content with directives
        page_registry: Dash page registry for context
        base_url: Application base URL

    Returns:
        TOON-formatted string
    """
    # Extract all content
    sections = extract_sections(raw_markdown)
    directives = extract_directives(raw_markdown)
    tables = extract_tables(raw_markdown)
    lists = extract_lists(raw_markdown)

    # Process source directives to get actual code - DEDUPLICATE by file path
    code_examples = []
    seen_files = set()
    for directive in directives:
        if directive.type == DirectiveType.SOURCE:
            # Handle comma-separated files
            target = directive.target.split(',')[0].strip() if ',' in directive.target else directive.target
            if target not in seen_files:
                example = process_source_directive(directive.target)
                if example:
                    code_examples.append(example)
                    seen_files.add(target)

    # Skip inline markdown code blocks (they add too much noise)
    # markdown_code_blocks = extract_markdown_code_blocks(raw_markdown)
    # Only add unique, substantial markdown code blocks not already from source
    # code_examples.extend(markdown_code_blocks)

    # Get exec directive info - DEDUPLICATE by module
    exec_info = []
    seen_modules = set()
    for directive in directives:
        if directive.type == DirectiveType.EXEC:
            if directive.target not in seen_modules:
                info = process_exec_directive(directive.target)
                exec_info.append(info)
                seen_modules.add(directive.target)

    # Build TOON output
    return build_documentation_toon(
        page_path=page_path,
        page_name=page_name,
        page_description=page_description,
        sections=sections,
        directives=directives,
        code_examples=code_examples,
        exec_info=exec_info,
        tables=tables,
        lists=lists,
        page_registry=page_registry,
        base_url=base_url
    )


def build_documentation_toon(
    page_path: str,
    page_name: str,
    page_description: str,
    sections: List[Section],
    directives: List[DirectiveInfo],
    code_examples: List[CodeExample],
    exec_info: List[Dict[str, Any]],
    tables: List[TableInfo],
    lists: List[ListInfo],
    page_registry,
    base_url: str
) -> str:
    """Build the final TOON string output - optimized for token efficiency."""
    lines = []

    # ========== META SECTION (compact) ==========
    lines.append("meta:")
    lines.append(f"  path: {page_path}")
    lines.append(f"  name: {page_name}")
    if page_description:
        lines.append(f"  desc: {escape_toon_value(page_description)}")
    lines.append("  type: documentation")
    lines.append("  format: toon/3.2")
    lines.append("")

    # ========== CONTEXT SECTION (compact) ==========
    registry_list = list(page_registry) if hasattr(page_registry, '__iter__') else []
    total_pages = len(registry_list)

    # Related pages (exclude current) - compact format
    related = []
    for page in registry_list:
        p_path = page.get('path', '') if isinstance(page, dict) else getattr(page, 'path', '')
        p_name = page.get('name', '') if isinstance(page, dict) else getattr(page, 'name', '')
        if p_path and p_path != page_path and p_name:
            related.append((p_name, p_path))

    lines.append(f"context: {total_pages}-page Dash docs site")
    if related:
        lines.append(f"relatedPages[{min(len(related), 5)}]:")
        for name, path in related[:5]:
            lines.append(f"  {escape_toon_value(name)}: {path}")
    lines.append("")

    # ========== SECTIONS (compressed - only key sections with content) ==========
    # Filter to only sections with meaningful content
    meaningful_sections = [s for s in sections if s.content.strip() or s.directives]
    # Further limit to avoid bloat
    display_sections = meaningful_sections[:20]  # Max 20 sections

    if display_sections:
        lines.append(f"sections[{len(display_sections)}]:")
        for i, section in enumerate(display_sections, 1):
            # Compact section format
            title_clean = section.title.replace('"', "'")
            lines.append(f"  {i}. [{section.level}] {title_clean}")

            # Only add content if substantial (> 50 chars after compression)
            compressed = compress_section_content(section.content, max_chars=300)
            if compressed and len(compressed) > 50:
                # Single line if short, otherwise indented
                if len(compressed) <= 100 and '\n' not in compressed:
                    lines.append(f"     > {compressed}")
                else:
                    for content_line in compressed.split('\n')[:3]:  # Max 3 lines
                        if content_line.strip():
                            lines.append(f"     {content_line.strip()}")

        lines.append("")

    # ========== DIRECTIVES (deduplicated, compact) ==========
    # Deduplicate directives by type+target
    seen_directives = set()
    unique_directives = []
    for d in directives:
        key = (d.type.value, d.target)
        if key not in seen_directives:
            unique_directives.append(d)
            seen_directives.add(key)

    if unique_directives:
        # Group by type for compact display
        by_type = {}
        for d in unique_directives:
            by_type.setdefault(d.type.value, []).append(d.target)

        lines.append(f"directives:")
        for dtype, targets in by_type.items():
            unique_targets = list(dict.fromkeys(targets))  # Preserve order, remove dups
            if len(unique_targets) <= 3:
                targets_str = ', '.join(t if t else '(none)' for t in unique_targets)
                lines.append(f"  {dtype}: [{targets_str}]")
            else:
                lines.append(f"  {dtype}[{len(unique_targets)}]: {unique_targets[0]}, {unique_targets[1]}, ...")
        lines.append("")

    # ========== EXEC COMPONENTS (compact) ==========
    if exec_info:
        lines.append(f"execComponents[{len(exec_info)}]:")
        for info in exec_info:
            callback_marker = " [callback]" if info.get('has_callback') else ""
            lines.append(f"  - {info['module']}{callback_marker}")
        lines.append("")

    # ========== CODE EXAMPLES (compressed but complete) ==========
    if code_examples:
        lines.append(f"codeExamples[{len(code_examples)}]:")
        for i, ex in enumerate(code_examples, 1):
            lines.append(f"  {i}:")
            lines.append(f"    file: {ex.source_file or 'inline'}")
            lines.append(f"    lang: {ex.language}")

            # Compress code - keep structure understanding
            compressed_code = compress_code(ex.code, max_lines=20, preserve_structure=True)
            code_lines = compressed_code.split('\n')
            lines.append("    code: |")
            for code_line in code_lines:
                lines.append(f"      {code_line}")

        lines.append("")

    # ========== TABLES (fully preserved, compact format) ==========
    if tables:
        lines.append(f"tables[{len(tables)}]:")
        for i, table in enumerate(tables, 1):
            # Compact header format
            headers_str = '|'.join(table.headers)
            lines.append(f"  {i}. [{headers_str}]")
            # Compact row format - one line per row
            for row in table.rows[:15]:  # Limit rows
                row_str = '|'.join(cell[:50] for cell in row)  # Truncate long cells
                lines.append(f"     {row_str}")
        lines.append("")

    # ========== KEY LISTS (only substantial ones) ==========
    substantial_lists = [l for l in lists if len(l.items) > 2][:5]  # Max 5 lists
    if substantial_lists:
        lines.append(f"keyLists[{len(substantial_lists)}]:")
        for lst in substantial_lists:
            items_preview = [item[:60] + '...' if len(item) > 60 else item for item in lst.items[:5]]
            lines.append(f"  - {lst.list_type}: {', '.join(items_preview)}")
        lines.append("")

    # ========== SUMMARY ==========
    summary_parts = [f"{page_name}:"]

    if display_sections:
        summary_parts.append(f"{len(display_sections)} sections")

    if code_examples:
        summary_parts.append(f"{len(code_examples)} code examples")

    if tables:
        summary_parts.append(f"{len(tables)} tables")

    if unique_directives:
        directive_types = sorted(set(d.type.value for d in unique_directives))
        summary_parts.append(f"uses {', '.join(directive_types)}")

    if exec_info:
        callback_count = sum(1 for e in exec_info if e.get('has_callback'))
        if callback_count:
            summary_parts.append(f"{callback_count} interactive components")

    lines.append(f"summary: {' | '.join(summary_parts)}")

    return '\n'.join(lines)

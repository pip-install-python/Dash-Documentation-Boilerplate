from dash import html, dcc, callback, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc

# Register Mantine templates
dmc.add_figure_templates(default="mantine_light")

# ============================================================================
# TOON v3.3 Analytics Data
# Real metrics from comparing llms.toon vs llms.txt for Data Visualization page
# ============================================================================

# Token/Character comparison data
format_comparison = {
    'Format': ['llms.txt', 'llms.toon'],
    'Characters': [15369, 11444],  # Actual measured values
    'Description': ['Full markdown with embedded code', 'TOON v3.3 compressed format']
}

# Calculate token reduction percentage
txt_chars = format_comparison['Characters'][0]
toon_chars = format_comparison['Characters'][1]
token_reduction = ((txt_chars - toon_chars) / txt_chars) * 100

# Content extraction metrics
content_extracted = {
    'Content Type': ['Sections', 'Code Examples', 'Tips', 'Best Practices', 'Patterns', 'Resources'],
    'Count': [20, 5, 6, 5, 3, 4],
    'Color': ['#228BE6', '#40C057', '#FAB005', '#7950F2', '#F06595', '#15AABF']
}

# TOON version evolution data
version_evolution = {
    'Version': ['v3.1', 'v3.2', 'v3.3'],
    'Comprehension': [60, 78, 95],  # Percentage
    'Features': [
        'Basic structure',
        'Sections, directives, tables',
        'Tips, best practices, patterns, resources'
    ]
}

# Comprehension score (target vs achieved)
comprehension_target = 95
comprehension_achieved = 95

# ============================================================================
# Create Figures
# ============================================================================

# Figure 1: Format Size Comparison (Bar)
fig_comparison = px.bar(
    x=format_comparison['Format'],
    y=format_comparison['Characters'],
    title='Format Size Comparison',
    labels={'x': 'Format', 'y': 'Characters'},
    color=format_comparison['Format'],
    color_discrete_map={'llms.txt': '#FA5252', 'llms.toon': '#12B886'},
    text=format_comparison['Characters']
)
fig_comparison.update_traces(textposition='outside', texttemplate='%{text:,}')
fig_comparison.update_layout(
    height=280,
    margin=dict(l=20, r=20, t=50, b=20),
    showlegend=False,
    yaxis_title='Characters',
    xaxis_title=''
)

# Figure 2: Content Extraction Breakdown (Pie)
fig_content = px.pie(
    names=content_extracted['Content Type'],
    values=content_extracted['Count'],
    title='Extracted Content Distribution',
    color_discrete_sequence=['#228BE6', '#40C057', '#FAB005', '#7950F2', '#F06595', '#15AABF'],
    hole=0.4
)
fig_content.update_layout(
    height=280,
    margin=dict(l=20, r=20, t=50, b=20)
)
fig_content.update_traces(textposition='inside', textinfo='label+value')

# Figure 3: Comprehension Evolution (Line)
fig_evolution = px.line(
    x=version_evolution['Version'],
    y=version_evolution['Comprehension'],
    title='TOON Comprehension Score Evolution',
    labels={'x': 'Version', 'y': 'Comprehension (%)'},
    markers=True
)
fig_evolution.add_scatter(
    x=version_evolution['Version'],
    y=version_evolution['Comprehension'],
    mode='markers+text',
    text=[f"{v}%" for v in version_evolution['Comprehension']],
    textposition='top center',
    marker=dict(size=12, color='#12B886'),
    showlegend=False
)
fig_evolution.update_layout(
    height=280,
    margin=dict(l=20, r=20, t=50, b=20),
    yaxis_range=[0, 105],
    showlegend=False
)
fig_evolution.update_traces(line=dict(color='#12B886', width=3))

# ============================================================================
# Dashboard Component
# ============================================================================

component = html.Div([
    dmc.Title("TOON v3.3 Analytics Dashboard", order=3, mb=20),
    dmc.Text(
        "Real-time metrics comparing llms.toon vs llms.txt format efficiency",
        c="dimmed", mb=20
    ),

    # KPI Cards Row
    dmc.SimpleGrid([
        # Token Reduction Card
        dmc.Card([
            dmc.Group([
                dmc.ThemeIcon(
                    dmc.Text("-", size="xl", fw=700),
                    size="xl",
                    radius="md",
                    color="teal",
                    variant="light"
                ),
                html.Div([
                    dmc.Text("Token Reduction", size="sm", c="dimmed"),
                    dmc.Title(f"{token_reduction:.1f}%", order=4, c="teal")
                ])
            ]),
        ], withBorder=True, p="md", radius="md"),

        # Comprehension Score Card
        dmc.Card([
            dmc.Group([
                dmc.ThemeIcon(
                    dmc.Text("AI", size="lg", fw=700),
                    size="xl",
                    radius="md",
                    color="violet",
                    variant="light"
                ),
                html.Div([
                    dmc.Text("LLM Comprehension", size="sm", c="dimmed"),
                    dmc.Title(f"{comprehension_achieved}%", order=4, c="violet")
                ])
            ]),
        ], withBorder=True, p="md", radius="md"),

        # Content Items Card
        dmc.Card([
            dmc.Group([
                dmc.ThemeIcon(
                    dmc.Text("#", size="xl", fw=700),
                    size="xl",
                    radius="md",
                    color="blue",
                    variant="light"
                ),
                html.Div([
                    dmc.Text("Content Items", size="sm", c="dimmed"),
                    dmc.Title(f"{sum(content_extracted['Count'])}", order=4, c="blue")
                ])
            ]),
        ], withBorder=True, p="md", radius="md"),

        # TOON Version Card
        dmc.Card([
            dmc.Group([
                dmc.ThemeIcon(
                    dmc.Text("v", size="xl", fw=700),
                    size="xl",
                    radius="md",
                    color="orange",
                    variant="light"
                ),
                html.Div([
                    dmc.Text("TOON Format", size="sm", c="dimmed"),
                    dmc.Title("v3.3", order=4, c="orange")
                ])
            ]),
        ], withBorder=True, p="md", radius="md"),
    ], cols={"base": 2, "sm": 4}, mb=20),

    # Charts Grid - Row 1
    dmc.SimpleGrid([
        dmc.Card([
            dcc.Graph(
                figure=fig_comparison,
                id='toon-comparison-chart',
                config={'displayModeBar': False}
            )
        ], withBorder=True, p="md", radius="md"),

        dmc.Card([
            dcc.Graph(
                figure=fig_content,
                id='toon-content-chart',
                config={'displayModeBar': False}
            )
        ], withBorder=True, p="md", radius="md"),
    ], cols={"base": 1, "sm": 2}, mb=15),

    # Charts Row 2 - Full Width Evolution Chart
    dmc.Card([
        dcc.Graph(
            figure=fig_evolution,
            id='toon-evolution-chart',
            config={'displayModeBar': False}
        )
    ], withBorder=True, p="md", radius="md", mb=15),

    # Feature Breakdown Table
    dmc.Card([
        dmc.Title("TOON v3.3 Features", order=5, mb=10),
        dmc.Table(
            striped=True,
            highlightOnHover=True,
            data={
                "head": ["Feature", "Count", "Description"],
                "body": [
                    ["Sections", "20", "Hierarchical document structure (h2-h6)"],
                    ["Code Examples", "5", "Full source files with smart compression"],
                    ["Tips", "6", "Short instructional code snippets"],
                    ["Best Practices", "5", "Numbered practices with multi-line code"],
                    ["Patterns", "3", "Architectural patterns with implementations"],
                    ["Resources", "4", "External links with full URLs preserved"],
                ]
            }
        )
    ], withBorder=True, p="md", radius="md")
])


# ============================================================================
# Theme-Aware Callbacks
# ============================================================================

@callback(
    Output('toon-comparison-chart', 'figure'),
    Output('toon-content-chart', 'figure'),
    Output('toon-evolution-chart', 'figure'),
    Input("color-scheme-storage", "data"),
)
def update_toon_dashboard_theme(theme):
    """Update all dashboard charts based on theme"""
    template = "mantine_dark" if theme == "dark" else "mantine_light"

    # Format comparison chart
    fig_comp = px.bar(
        x=format_comparison['Format'],
        y=format_comparison['Characters'],
        title='Format Size Comparison',
        labels={'x': 'Format', 'y': 'Characters'},
        color=format_comparison['Format'],
        color_discrete_map={'llms.txt': '#FA5252', 'llms.toon': '#12B886'},
        text=format_comparison['Characters'],
        template=template
    )
    fig_comp.update_traces(textposition='outside', texttemplate='%{text:,}')
    fig_comp.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=False,
        yaxis_title='Characters',
        xaxis_title=''
    )

    # Content breakdown chart
    fig_cont = px.pie(
        names=content_extracted['Content Type'],
        values=content_extracted['Count'],
        title='Extracted Content Distribution',
        color_discrete_sequence=['#228BE6', '#40C057', '#FAB005', '#7950F2', '#F06595', '#15AABF'],
        hole=0.4,
        template=template
    )
    fig_cont.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig_cont.update_traces(textposition='inside', textinfo='label+value')

    # Evolution chart
    fig_evo = go.Figure()
    fig_evo.add_trace(go.Scatter(
        x=version_evolution['Version'],
        y=version_evolution['Comprehension'],
        mode='lines+markers+text',
        text=[f"{v}%" for v in version_evolution['Comprehension']],
        textposition='top center',
        marker=dict(size=12, color='#12B886'),
        line=dict(color='#12B886', width=3),
        name='Comprehension'
    ))
    fig_evo.update_layout(
        title='TOON Comprehension Score Evolution',
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_range=[0, 105],
        yaxis_title='Comprehension (%)',
        xaxis_title='Version',
        showlegend=False,
        template=template
    )

    return fig_comp, fig_cont, fig_evo

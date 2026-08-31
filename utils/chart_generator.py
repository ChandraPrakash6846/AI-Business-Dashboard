import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import traceback

DEFAULT_TEMPLATE = 'plotly_dark'
COLOR_PALETTE = px.colors.qualitative.Set2

def apply_chart_styling(fig):
    """Apply consistent dark theme styling to any plotly figure."""
    try:
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e0e0ff'),
            margin=dict(l=40, r=40, t=60, b=40),
            legend=dict(bgcolor='rgba(0,0,0,0)')
        )
        return fig
    except Exception as e:
        print(f"Error styling chart: {e}")
        return fig

def create_bar_chart(df, x, y, color=None, title='', orientation='v'):
    """Create interactive bar chart using plotly express."""
    try:
        kwargs = {}
        if color and color in df.columns:
            kwargs['color'] = color
            
        if orientation == 'h':
            # Swap x and y internally for horizontal
            fig = px.bar(df, x=y, y=x, title=title, orientation='h',
                         template=DEFAULT_TEMPLATE, color_discrete_sequence=COLOR_PALETTE, **kwargs)
        else:
            fig = px.bar(df, x=x, y=y, title=title, orientation='v',
                         template=DEFAULT_TEMPLATE, color_discrete_sequence=COLOR_PALETTE, **kwargs)
        return apply_chart_styling(fig)
    except Exception as e:
        print(f"Error creating bar chart: {e}")
        return go.Figure()

def create_line_chart(df, x, y, color=None, title='', markers=True):
    """Create interactive line chart."""
    try:
        kwargs = {}
        if color and color in df.columns:
            kwargs['color'] = color
            
        fig = px.line(df, x=x, y=y, title=title, markers=markers,
                      template=DEFAULT_TEMPLATE, color_discrete_sequence=COLOR_PALETTE, **kwargs)
        return apply_chart_styling(fig)
    except Exception as e:
        print(f"Error creating line chart: {e}")
        return go.Figure()

def create_pie_chart(df, names, values, title='', hole=0.4):
    """Create donut/pie chart."""
    try:
        fig = px.pie(df, names=names, values=values, title=title, hole=hole,
                     template=DEFAULT_TEMPLATE, color_discrete_sequence=COLOR_PALETTE)
        return apply_chart_styling(fig)
    except Exception as e:
        print(f"Error creating pie chart: {e}")
        return go.Figure()

def create_scatter_chart(df, x, y, color=None, size=None, title='', trendline=None):
    """Create scatter plot."""
    try:
        kwargs = {}
        if color and color in df.columns: kwargs['color'] = color
        if size and size in df.columns: kwargs['size'] = size
        if trendline: kwargs['trendline'] = trendline
            
        fig = px.scatter(df, x=x, y=y, title=title, 
                         template=DEFAULT_TEMPLATE, color_discrete_sequence=COLOR_PALETTE, **kwargs)
        return apply_chart_styling(fig)
    except Exception as e:
        print(f"Error creating scatter chart: {e}")
        return go.Figure()

def create_histogram(df, x, nbins=30, color=None, title=''):
    """Create histogram."""
    try:
        kwargs = {}
        if color and color in df.columns: kwargs['color'] = color
            
        fig = px.histogram(df, x=x, nbins=nbins, title=title,
                           template=DEFAULT_TEMPLATE, color_discrete_sequence=COLOR_PALETTE, **kwargs)
        return apply_chart_styling(fig)
    except Exception as e:
        print(f"Error creating histogram: {e}")
        return go.Figure()

def create_heatmap(data, title='Correlation Heatmap'):
    """Create heatmap from correlation matrix (DataFrame)."""
    try:
        if not isinstance(data, pd.DataFrame):
            data = pd.DataFrame(data)
            
        # Format text for annotations
        text = np.round(data.values, 2).astype(str)
            
        fig = go.Figure(data=go.Heatmap(
            z=data.values,
            x=data.columns,
            y=data.index,
            colorscale='RdBu_r',
            text=text,
            texttemplate="%{text}",
            hoverinfo='z'
        ))
        fig.update_layout(title=title, template=DEFAULT_TEMPLATE)
        return apply_chart_styling(fig)
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        return go.Figure()

def create_box_plot(df, x=None, y=None, color=None, title=''):
    """Create box plot for distribution analysis."""
    try:
        kwargs = {}
        if color and color in df.columns: kwargs['color'] = color
        if x and x in df.columns: kwargs['x'] = x
        if y and y in df.columns: kwargs['y'] = y
            
        fig = px.box(df, title=title, template=DEFAULT_TEMPLATE, 
                     color_discrete_sequence=COLOR_PALETTE, **kwargs)
        return apply_chart_styling(fig)
    except Exception as e:
        print(f"Error creating box plot: {e}")
        return go.Figure()

def create_area_chart(df, x, y, color=None, title=''):
    """Create area chart."""
    try:
        kwargs = {}
        if color and color in df.columns: kwargs['color'] = color
            
        fig = px.area(df, x=x, y=y, title=title,
                      template=DEFAULT_TEMPLATE, color_discrete_sequence=COLOR_PALETTE, **kwargs)
        return apply_chart_styling(fig)
    except Exception as e:
        print(f"Error creating area chart: {e}")
        return go.Figure()

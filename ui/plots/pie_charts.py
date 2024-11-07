import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .utils import category_colors
from dash import dcc

def pie_chart_plots(transactions_df, date_range):
    # Pie charts by category for selected date range
    pie_chart_df = transactions_df.copy()

    # # Filter out non-expense transactions (values > 0)
    # pie_chart_df = pie_chart_df[pie_chart_df['value'] <= 0]
    #
    # # Invert transaction values to make them positive
    # pie_chart_df['value'] = pie_chart_df['value'].abs()
    pie_chart_df['value'] = -pie_chart_df['value']

    # Add year, month, and week columns for flexible grouping
    pie_chart_df['year'] = pie_chart_df['bookingDate'].dt.year
    pie_chart_df['month'] = pie_chart_df['bookingDate'].dt.month
    pie_chart_df['week'] = pie_chart_df['bookingDate'].dt.isocalendar().week

    # Determine grouping level and generate pie charts
    cols = 3
    if date_range.days > 365:
        # Yearly distribution
        category_totals = pie_chart_df.groupby(['year', 'category'])['value'].sum().reset_index()
        category_totals.drop(category_totals[category_totals['value'] < 0].index, inplace=True)
        unique_years = category_totals['year'].unique()
        rows = (len(unique_years) + cols - 1) // cols  # Calculate required rows

        # Create subplot figure with shared legend
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[f"{year}" for year in unique_years],
            specs=[[{'type': 'pie'} for _ in range(cols)] for _ in range(rows)]
        )

        # Add a pie chart for each year
        for i, year in enumerate(unique_years):
            year_data = category_totals[category_totals['year'] == year]
            row = i // cols + 1
            col = i % cols + 1
            fig.add_trace(
                go.Pie(
                    labels=year_data['category'],
                    values=year_data['value'],
                    marker=dict(colors=[category_colors.get(cat, 'gray') for cat in year_data['category']]),
                    textinfo='percent+label'
                ),
                row=row, col=col
            )

        # Update layout for shared legend and scaling
        fig.update_layout(
            title="Category Distribution Over Time",
            showlegend=True,
            legend=dict(title="Category", orientation="v", x=1.2, y=1.0, xanchor="right", yanchor="top"),
            height=400 * rows,
            # width=np.inf,
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )

        # Adjust chart sizes to fit on the screen
        fig.update_traces(hole=.4, textposition='inside')

        # Display the figure in Dash
        pie_charts = dcc.Graph(id='category-pie-charts-years', figure=fig, style={'width': '100%'})

    elif date_range.days > 30:
        # Monthly distribution
        category_totals = pie_chart_df.groupby(['year', 'month', 'category'])['value'].sum().reset_index()
        category_totals.drop(category_totals[category_totals['value'] < 0].index, inplace=True)
        unique_months = category_totals[['year', 'month']].drop_duplicates()
        rows = (len(unique_months) + cols - 1) // cols
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[f"{month_data['month']:02}.{month_data['year']}" for _, month_data in
                            unique_months.iterrows()],
            specs=[[{'type': 'pie'} for _ in range(cols)] for _ in range(rows)]
        )

        for i, (year, month) in enumerate(unique_months.itertuples(index=False)):
            month_data = category_totals[(category_totals['year'] == year) & (category_totals['month'] == month)]
            row = i // cols + 1
            col = i % cols + 1
            fig.add_trace(
                go.Pie(
                    labels=month_data['category'],
                    values=month_data['value'],
                    marker=dict(colors=[category_colors.get(cat, 'gray') for cat in month_data['category']]),
                    textinfo='percent+label'
                ),
                row=row, col=col
            )

        fig.update_layout(
            title="Category Distribution by Month",
            showlegend=True,
            legend=dict(title="Category", orientation="v", x=1.2, y=1.0, xanchor="right", yanchor="top"),
            height=400 * rows,
            # width=np.inf,
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )
        fig.update_traces(hole=.4, textposition='inside')
        pie_charts = dcc.Graph(id='category-pie-charts-months', figure=fig, style={'width': '100%'})

    else:
        # Weekly distribution
        category_totals = pie_chart_df.groupby(['year', 'week', 'category'])['value'].sum().reset_index()
        category_totals.drop(category_totals[category_totals['value'] < 0].index, inplace=True)
        unique_weeks = category_totals[['year', 'week']].drop_duplicates()
        rows = (len(unique_weeks) + cols - 1) // cols
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[f"Week {week_data['week']} - {week_data['year']}" for _, week_data in
                            unique_weeks.iterrows()],
            specs=[[{'type': 'pie'} for _ in range(cols)] for _ in range(rows)]
        )

        for i, (year, week) in enumerate(unique_weeks.itertuples(index=False)):
            week_data = category_totals[(category_totals['year'] == year) & (category_totals['week'] == week)]
            row = i // cols + 1
            col = i % cols + 1
            fig.add_trace(
                go.Pie(
                    labels=week_data['category'],
                    values=week_data['value'],
                    marker=dict(colors=[category_colors.get(cat, 'gray') for cat in week_data['category']]),
                    textinfo='percent+label'
                ),
                row=row, col=col
            )

        fig.update_layout(
            title="Category Distribution by Week",
            showlegend=True,
            legend=dict(title="Category", orientation="v", x=1.2, y=1.0, xanchor="right", yanchor="top"),
            height=400 * rows,
            # width=np.inf,
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )

        fig.update_traces(hole=.4, textposition='inside')

        pie_charts = dcc.Graph(id='category-pie-charts-days', figure=fig, style={'width': '100%'})

    return pie_charts
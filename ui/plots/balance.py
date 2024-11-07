import plotly.express as px
from .utils import category_colors

def balance_plot(transactions_df):
    # sum up expenses per day
    daily_transactions_df = transactions_df.groupby('bookingDate', as_index=False).agg({'value': 'sum'})

    # Compute cumulative balance
    daily_transactions_df['balance'] = daily_transactions_df['value'].cumsum()

    # Adjust the final balance to match the target balance
    final_balance_target = transactions_df['currentBalance'].iloc[-1]
    final_cumsum_value = daily_transactions_df['balance'].iloc[-1]
    adjustment = final_balance_target - final_cumsum_value
    daily_transactions_df['balance'] += adjustment

    # Plot cumulative balance over time with one data point per day
    balance_fig = px.line(
        daily_transactions_df,
        x="bookingDate",
        y="balance",
        title="Balance Over Time",
        labels={'value': 'Balance', 'bookingDate': 'Date'},
        line_shape='hv'
    )

    return balance_fig


def category_balance_plot(transactions_df, start_date, end_date):
    # compute expenses by category
    expenses_df = transactions_df.copy()

    # Invert transaction values
    expenses_df['value'] = -expenses_df['value']

    # Sort transactions by ascending bookingDate
    expenses_df = expenses_df.sort_values(by='bookingDate')

    # Drop Income category
    expenses_df = expenses_df[expenses_df['category'] != 'Income']

    # sum up expenses per day
    daily_category_expenses_df = expenses_df.groupby(['bookingDate', 'category'], as_index=False).agg(
        {'value': 'sum'})

    # Compute cumulative balance per category
    daily_category_expenses_df['cumulative_balance'] = daily_category_expenses_df.groupby('category')[
        'value'].cumsum()

    # append start and end date data
    for category in daily_category_expenses_df['category'].unique():

        if end_date not in daily_category_expenses_df[daily_category_expenses_df['category'] == category][
            'bookingDate'].values:
            recent_balance = daily_category_expenses_df[daily_category_expenses_df['category'] == category].values[
                -1, 3]
            daily_category_expenses_df.loc[daily_category_expenses_df.shape[0] + 1] = [end_date, category, 0,
                                                                                       recent_balance]
        if start_date not in daily_category_expenses_df[daily_category_expenses_df['category'] == category][
            'bookingDate'].values:
            daily_category_expenses_df.loc[daily_category_expenses_df.shape[0] + 1] = [start_date, category, 0, 0]

    daily_category_expenses_df.sort_values(by='bookingDate', inplace=True)

    # Balance over time by category plot
    category_balance_fig = px.line(
        daily_category_expenses_df,
        x="bookingDate",
        y="cumulative_balance",
        color="category",
        title="Expenses Over Time by Category",
        labels={'value': 'Balance', 'bookingDate': 'Date'},
        line_shape='hv',
        color_discrete_map=category_colors
    )

    return category_balance_fig
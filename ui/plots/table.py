from dash import dash_table

def transaction_table(transactions_df):
    # Display transactions table
    table_df = transactions_df.copy()
    table_df.sort_values(by='bookingDate', ascending=False, inplace=True)
    table_df['bookingDate'] = table_df['bookingDate'].dt.strftime('%d.%m.%Y')
    table_df['value'] = table_df['value'].apply(lambda x: f'{x:.2f}')

    column_order = ['bookingDate', 'creditorName', 'description', 'value', 'currencyCode', 'deptorName', 'category']
    columns = [{"name": i, "id": i} for i in column_order if i in table_df.columns]

    transactions_table = dash_table.DataTable(
        id='table',
        columns=columns,
        data=table_df.to_dict('records'),
        style_table={'overflowX': 'auto', 'width': '100%'},
        style_header=dict(backgroundColor="#1f77b4", color="#ffffff"),
        style_data=dict(backgroundColor="#ffffff", whiteSpace='normal', height='auto'),
        style_cell=dict(textAlign='left', minWidth='100px', width='auto', maxWidth='250px', overflow='hidden'),
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(220, 220, 220)',
            }
        ],
        page_size=10,
    ),

    return transactions_table

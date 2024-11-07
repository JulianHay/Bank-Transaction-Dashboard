import dash
from dash import Dash, dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime, timedelta
from api.client import DKBapi
from .plots.balance import balance_plot, category_balance_plot
from .plots.pie_charts import pie_chart_plots
from .plots.table import transaction_table

# Initialize DKBapi instance
api = DKBapi()


# Dash app setup
app = Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"  # Font Awesome
])



# Login Modal
login_modal = dbc.Modal(
    [
        dbc.ModalHeader("DKB Login"),
        dbc.ModalBody(
            [
                # Username and Password Inputs
                dbc.Input(id="username", placeholder="Enter username", type="text", className="mb-2"),
                dbc.Input(id="password", placeholder="Enter password", type="password", className="mb-2"),
                dbc.Button("Login", id="login-button", color="primary", n_clicks=0)
            ],
            style={'height': '160px'}
        ),
    ],
    id="login-modal",
    is_open=False,  # Initially closed
    centered=True,  # Center the modal in the screen
    backdrop='static',
    backdrop_class_name="bg-white opacity-100",
)

# Loading Spinner for MFA
mfa_spinner = dbc.Modal(
    [
        dbc.ModalHeader("Please confirm the login via your phone"),
        dbc.ModalBody([
            dbc.Spinner(
                color="primary"
            ),
            html.Div(children="Waiting for MFA verification..."),
        ],
            style={'height': '160px', 'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'flex-direction': 'column', 'gap': '10px'}
        ),
    ],
    id="mfa-modal",
    is_open=False,  # Initially closed
    centered=True,  # Center the modal in the screen
    backdrop='static',
    backdrop_class_name="bg-white opacity-100",
)

alert = dbc.Alert(
    html.Div(id="alert-message"),  # Dynamic content for alert message
    id="alert",
    color="danger",
    dismissable=True,
    is_open=False,
    style={
        "position": "fixed",
        "top": "10%",  # Adjust to position it above the modal
        "left": "50%",
        "transform": "translateX(-50%)",
        "width": "300px",
        "zIndex": 9999,  # Ensure it appears above the modal
    }
)

# App Layout
app.layout = html.Div([
    html.H1("Bank Transaction Dashboard", style={'font-weight': 'bold'}),

    html.Div([

        # Transaction visualizations
        html.Div([
            html.P("Select Date Range:",
                   style={'font-weight': 'bold', 'font-size': '18px','margin-left': '5px', 'margin-bottom': '0px'}),
            dcc.DatePickerRange(
                id='date-picker',
                start_date=datetime.now().replace(year=datetime.now().year - 1),
                end_date=datetime.now(),
                display_format='DD.MM.YYYY',
            ),
            dcc.RadioItems(
                    id='date-range-selector',
                    options=[
                        {'label': 'Current Month', 'value': 'current_month'},
                        {'label': 'Current Year', 'value': 'current_year'},
                        {'label': 'Last 30 Days', 'value': 'last_30_days'},
                        {'label': 'Last 7 Days', 'value': 'last_7_days'},
                    ],
                    value='custom',
                    inline=True,
                    style={'display': 'flex','flex-wrap': 'wrap','gap':'10px', 'width': '285px'},
                    inputStyle={'margin-right': '5px'},
                    labelStyle={'width': '125px'}
                ),
        ]),

        html.Div(id='balance'),

        # Update data button
        dbc.Button(
            html.Span([
                html.I(className="fa-solid fa-arrow-rotate-right"),
                " Update Data"
            ]),
            id="update-data",
            n_clicks=0
        ),
    ],style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center',
             'margin': '20px', 'width': '90%'}),

    html.Div([
        dcc.Graph(id='balance-over-time', style={ 'width': '50%'}),
        dcc.Graph(id='balance-over-time-by-category', style={ 'width': '50%'}),
        ],
        style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between',
               'align-items': 'center', 'margin': '20px', 'width': '90%'}
    ),

    html.Div(id='category-pie-charts', style={'display': 'flex', 'flex-wrap': 'wrap', 'width': '90%'}),

    html.H3("Transactions", style={'margin': '20px', 'width': '90%'}),
    html.Div(id='transaction-table', style={'margin': '20px', 'width': '90%'}),

    # Modals
    html.Div(id="no-data-modal", style={'display': 'none'}),
    login_modal,
    mfa_spinner,
    alert,

    dcc.Store(id="mfa-status", data="none"),
    dcc.Interval(id="mfa-check-interval", interval=5000, n_intervals=0, disabled=True),
    dcc.Interval(id="mfa-modal-close-interval", interval=1000, max_intervals=1, disabled=True),
],
    style={'padding': '20px', 'display': 'flex', 'flex-direction': 'column', 'align-items': 'center'}
)


@app.callback(
    [Output("login-modal", "is_open"),
     Output("mfa-modal", "is_open"),
     Output("mfa-check-interval", "disabled"),
     Output("alert", "is_open"),
     Output("alert-message", "children"),
     ],
    [Input("update-data", "n_clicks"),
     Input("login-button", "n_clicks"),
     Input("mfa-modal-close-interval", "n_intervals"),
     ],
    [State("username", "value"),
     State("password", "value"),
     State("mfa-status", "data")],
    prevent_initial_call=True
)
def handle_login_and_mfa(n_update, n_login, n_intervals, username, password, mfa_status):
    ctx = dash.callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Open login modal on Update Data click
    if triggered_id == "update-data" and n_update > 0:
        return True, False, True, False, ""

    # Handle login on Login button click
    if triggered_id == "login-button" and n_login > 0:
        response = api.login(username=username, password=password)
        if response['message'] == 'Login successful':
            # Show MFA modal, set mfa_status to pending, enable interval
            return False, True, False, False, ""
        else:
            # Show alert if login failed
            return True, False, True, True, "Login failed. Please try again."

    if triggered_id == "mfa-modal-close-interval":
        if mfa_status == "verified":
            return False, False, True, False, ""
        else:
            return False, False, True, True, "MFA verification failed. Please try again."

    return False, False, False, ""

# Callback to check MFA status and fetch transaction data
@app.callback(
    [Output("mfa-status", "data"),
     Output("mfa-modal-close-interval", "disabled"),],
    [Input("mfa-check-interval", "n_intervals")],
    prevent_initial_call=True
)
def check_mfa_status(n_intervals):
    print('2 Factor Authentication .' + int(n_intervals % 3) * '.', end="\r")
    status = api.check_mfa_status()

    if status == 'processed':
        # On success, fetch data, disable interval
        account_id = api.get_account_id()
        api.get_transactions(account_id)
        return "verified", False
    else:
        if n_intervals * 5 > 120:
            return "failed", True
        else:
            return "pending", True

# Callback to update plots
@app.callback(
    [Output("balance-over-time", "figure"),
    Output("balance-over-time-by-category", "figure"),
    Output("category-pie-charts", "children"),
    Output("transaction-table", "children"),
    Output("balance", "children"),
    Output("date-range-selector", "value"),
    Output('date-picker', 'start_date'),
    Output('date-picker', 'end_date'),
    Output("no-data-modal", "style")],
    [Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
    Input("mfa-status", "data"),
    Input("date-range-selector", "value")],
)
def update_plots(start_date, end_date, mfa_status, selected_range):

    transactions_df = pd.read_excel('DKB_transactions_Girokonto.xlsx')

    if transactions_df.empty:
        # Return empty figures
        return {}, {}, "", "", "No data available. Please update.", "custom", start_date, end_date, {'display': 'block', 'width': '100%', 'height': '100%','position':'absolute', 'top': '230px', 'left': '0', 'background-color':'#fff'}
    elif mfa_status == "pending":
        return {}, {}, "", "", "", "custom", start_date, end_date, {'display': 'block', 'width': '100%', 'height': '100%','position':'absolute', 'top': '230px', 'left': '0', 'background-color':'#fff'}
    else:
        ctx = dash.callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

        today = datetime.now().date()

        # Default values to use if triggered by the RadioItems
        start_date_expected, end_date = start_date, end_date

        # Case 1: Update date picker based on radio selection
        if triggered_id == 'date-range-selector':
            if selected_range == 'current_month':
                start_date = today.replace(day=1)
                end_date = (start_date + pd.DateOffset(months=1) - timedelta(days=1)).date()
            elif selected_range == 'current_year':
                start_date = today.replace(month=1, day=1)
                end_date = today.replace(month=12, day=31)
            elif selected_range == 'last_30_days':
                start_date = today - timedelta(days=30)
                end_date = today
            elif selected_range == 'last_7_days':
                start_date = today - timedelta(days=7)
                end_date = today
            final_selected_range = selected_range

        # Case 2: Update radio to "custom" if dates are manually changed
        elif triggered_id == 'date-picker-range':
            final_selected_range = 'custom'
        else:
            final_selected_range = 'custom'

        # Convert 'bookingDate' column to datetime format
        transactions_df['bookingDate'] = pd.to_datetime(transactions_df['bookingDate'], format='%Y-%m-%d')
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # filter by date
        transactions_df = transactions_df[transactions_df['bookingDate'] >= start_date]
        transactions_df = transactions_df[transactions_df['bookingDate'] <= end_date]

        # sort by date
        transactions_df.sort_values(by='bookingDate',inplace=True)

        # Calculate the date range to determine granularity
        date_range = end_date - start_date

        balance_fig = balance_plot(transactions_df)

        category_balance_fig = category_balance_plot(transactions_df, start_date, end_date)

        pie_charts = pie_chart_plots(transactions_df,date_range)


        transactions_table = transaction_table(transactions_df)


        current_balance_info= html.Div([
            html.Span(f'Current Balance: {transactions_df["currentBalance"].iloc[-1]:.2f} {transactions_df["currencyCode"].iloc[-1]}',
                      style={'font-weight': 'bold', 'font-size': '24px', 'margin-top': '20px'}),
            html.Span(f'Last updated: {transactions_df["bookingDate"].iloc[-1].strftime("%d.%m.%Y")}'),
        ], style={'display': 'flex', 'flex-direction': 'column', 'justify-content': 'center', 'align-items': 'center'}
        )

        return balance_fig, category_balance_fig, pie_charts, transactions_table, current_balance_info, final_selected_range, start_date, end_date, {'display':'none'}

def run_dash():
    app.run(debug=False, port=8051)


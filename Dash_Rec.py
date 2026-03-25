import pandas as pd 
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv")
year_list = [i for i in range(1980, 2013)]

app.layout = html.Div(children=[
    html.H1('Automobile Sales Statistics Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
    
    html.Div([
        html.Div([
            html.H2('Select Report:', style={'margin-right': '2em'}),
            dcc.Dropdown(id='dropdown-statistics', 
                         options=[
                             {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                             {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
                         ],
                         placeholder='Select a report type',
                         value=None,
                         style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'})
        ]),
        html.Div([
            html.H2('Select year:', style={'margin-right': '2em'}),
            dcc.Dropdown(id='select-year', 
                         options=[{'label': i, 'value': i} for i in year_list],
                         placeholder='Select-year',
                         value=None,
                         style={'width': '80%', 'padding': '3px', 'fontSize': '20px', 'textAlignLast': 'center'})
        ])
    ]),

    # The Output Container - Removed 'flex' from here so it stacks vertically
    html.Div(id='output-container', className='chart-grid', style={'padding': '20px'})
])

@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    if selected_statistics == 'Yearly Statistics':
        return False
    return True

@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), 
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    if selected_statistics == 'Recession Period Statistics':
        df_R = df[df['Recession'] == 1]

        # Plot 1: Use df_R to see fluctuation over all recession years
        R_yr = df_R.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_plt1 = dcc.Graph(figure=px.line(R_yr, x='Year', y='Automobile_Sales', title='Sales Fluctuation (Recession)'))

        R_veh = df_R.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_plt2 = dcc.Graph(figure=px.bar(R_veh, x='Vehicle_Type', y='Automobile_Sales', title='Avg Vehicles Sold by Type'))

        R_exp = df_R.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_plt3 = dcc.Graph(figure=px.pie(R_exp, values='Advertising_Expenditure', names='Vehicle_Type', title="Ad Expenditure Share"))

        R_unemp = df_R.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_plt4 = dcc.Graph(figure=px.bar(R_unemp, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type', title='Unemployment vs Sales'))

        return [
            html.Div(children=[R_plt1, R_plt2], style={'display': 'flex'}),
            html.Div(children=[R_plt3, R_plt4], style={'display': 'flex'})
        ]

    elif selected_statistics == 'Yearly Statistics' and input_year:
        df_yr = df[df['Year'] == int(input_year)]

        # FIXED PLOT 1: Use the FULL dataframe (df) to show the whole trend, not just one year
        yr_trend = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
        yr_plt1 = dcc.Graph(figure=px.line(yr_trend, x='Year', y='Automobile_Sales', title='Automobile Sales Trend (1980-2013)'))

        # FIXED PLOT 2: Sort Months chronologically
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        yr_ms = df_yr.groupby('Month')['Automobile_Sales'].sum().reset_index()
        
        # Sort yr_ms by the month_order
        yr_ms['Month'] = pd.Categorical(yr_ms['Month'], categories=month_order, ordered=True)
        yr_ms = yr_ms.sort_values('Month')

        yr_plt2 = dcc.Graph(figure=px.line(yr_ms, x='Month', y='Automobile_Sales', title='Monthly Sales in {}'.format(input_year)))

        yr_v = df_yr.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        yr_plt3 = dcc.Graph(figure=px.bar(yr_v, x='Vehicle_Type', y='Automobile_Sales', title='Avg Sold by Type in {}'.format(input_year)))

        yr_exp = df_yr.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        yr_plt4 = dcc.Graph(figure=px.pie(yr_exp, values='Advertising_Expenditure', names='Vehicle_Type', title='Ad Expenditure in {}'.format(input_year)))

        return [
            # Two rows of charts
            html.Div(children=[yr_plt1, yr_plt2], style={'display': 'flex'}),
            html.Div(children=[yr_plt3, yr_plt4], style={'display': 'flex'})
        ]
    
    return []

if __name__ == '__main__':
    app.run()
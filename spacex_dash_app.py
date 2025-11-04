# Import required libraries
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} 
    for s in sorted(spacex_df['Launch Site'].dropna().unique())
]



# Create a dash application
app = Dash(__name__)

# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # successes per site
        agg = (spacex_df.groupby('Launch Site', as_index=False)['class']
               .sum()
               .rename(columns={'class': 'successes'}))
        fig = px.pie(
            agg, values='successes', names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # filter to the chosen site, then count class outcomes
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = (df_site.groupby('class').size()
                    .reindex([1, 0], fill_value=0)
                    .rename(index={1: 'Success', 0: 'Failure'})
                    .rename_axis('Outcome').reset_index(name='count'))
        fig = px.pie(
            counts, values='count', names='Outcome',
            title=f'{entered_site}: Success vs Failure',
            color='Outcome',
            color_discrete_map={'Success': 'green', 'Failure': 'red'}
        )

    fig.update_traces(textinfo='percent+label')
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return fig

slider_marks = {v: f"{v:,}" for v in range(0, 10001, 2000)}

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")])
def get_pie_chart(entered_site, payload_range):
    low, high = payload_range
    # base filter: payload in selected range
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    # site filter if not ALL
    if entered_site != 'ALL':
        df = df[df['Launch Site'] == entered_site]

    # make y categorical so 0/1 are readable
    df = df.copy()
    df['Outcome'] = df['class'].map({1: 'Success', 0: 'Failure'})

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='Outcome',                          # shows Success/Failure bands
        color='Booster Version Category',
        hover_data=['Launch Site', 'class', 'Payload Mass (kg)'],
        title=('Correlation between Payload and Success — All Sites'
               if entered_site == 'ALL' else
               f'Correlation between Payload and Success — {entered_site}')
    )
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend_title_text='Booster')
    # optional: put markers on a single row (numeric y)
    # fig.update_traces(marker=dict(size=9, opacity=0.8))

    return fig

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=site_options,
                                    value='ALL',                      # default
                                    placeholder='Select a Launch Site',
                                    searchable=True,
                                    clearable=False
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks=slider_marks,
                                    value=[min_payload, max_payload],
                                    tooltip={"placement":"bottom", "always_visible": True}),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output


# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# Create a comprehensive dataset of FIFA World Cup finals
def create_world_cup_dataset():
    data = [
        {"Year": 1930, "Winner": "Uruguay", "Runner-up": "Argentina", "Host": "Uruguay"},
        {"Year": 1934, "Winner": "Italy", "Runner-up": "Czechoslovakia", "Host": "Italy"},
        {"Year": 1938, "Winner": "Italy", "Runner-up": "Hungary", "Host": "France"},
        {"Year": 1950, "Winner": "Uruguay", "Runner-up": "Brazil", "Host": "Brazil"},
        {"Year": 1954, "Winner": "West Germany", "Runner-up": "Hungary", "Host": "Switzerland"},
        {"Year": 1958, "Winner": "Brazil", "Runner-up": "Sweden", "Host": "Sweden"},
        {"Year": 1962, "Winner": "Brazil", "Runner-up": "Czechoslovakia", "Host": "Chile"},
        {"Year": 1966, "Winner": "England", "Runner-up": "West Germany", "Host": "England"},
        {"Year": 1970, "Winner": "Brazil", "Runner-up": "Italy", "Host": "Mexico"},
        {"Year": 1974, "Winner": "West Germany", "Runner-up": "Netherlands", "Host": "West Germany"},
        {"Year": 1978, "Winner": "Argentina", "Runner-up": "Netherlands", "Host": "Argentina"},
        {"Year": 1982, "Winner": "Italy", "Runner-up": "West Germany", "Host": "Spain"},
        {"Year": 1986, "Winner": "Argentina", "Runner-up": "West Germany", "Host": "Mexico"},
        {"Year": 1990, "Winner": "West Germany", "Runner-up": "Argentina", "Host": "Italy"},
        {"Year": 1994, "Winner": "Brazil", "Runner-up": "Italy", "Host": "United States"},
        {"Year": 1998, "Winner": "France", "Runner-up": "Brazil", "Host": "France"},
        {"Year": 2002, "Winner": "Brazil", "Runner-up": "Germany", "Host": "South Korea/Japan"},
        {"Year": 2006, "Winner": "Italy", "Runner-up": "France", "Host": "Germany"},
        {"Year": 2010, "Winner": "Spain", "Runner-up": "Netherlands", "Host": "South Africa"},
        {"Year": 2014, "Winner": "Germany", "Runner-up": "Argentina", "Host": "Brazil"},
        {"Year": 2018, "Winner": "France", "Runner-up": "Croatia", "Host": "Russia"},
        {"Year": 2022, "Winner": "Argentina", "Runner-up": "France", "Host": "Qatar"}
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Normalize country names (merge West Germany and Germany)
    df['Winner'] = df['Winner'].replace('West Germany', 'Germany')
    df['Runner-up'] = df['Runner-up'].replace('West Germany', 'Germany')
    
    return df

# Prepare data for visualization
world_cup_df = create_world_cup_dataset()

# Calculate number of wins for each country
wins_by_country = world_cup_df['Winner'].value_counts().reset_index()
wins_by_country.columns = ['Country', 'Wins']
print(wins_by_country)

# Prepare country codes for Choropleth map
country_codes = {
    'Brazil': 'BRA', 'Germany': 'DEU', 'Italy': 'ITA', 'Argentina': 'ARG', 
    'France': 'FRA', 'Uruguay': 'URY', 'England': 'GBR', 'Spain': 'ESP', 
    'Netherlands': 'NLD', 'Croatia': 'HRV', 'Hungary': 'HUN', 'Sweden': 'SWE',
    'Czechoslovakia': 'CZE'
}

# Add country code to wins dataframe
wins_by_country['Country Code'] = wins_by_country['Country'].map(country_codes)

# Create Dash app
app = dash.Dash(__name__)
server = app.server

# Layout of the dashboard
app.layout = html.Div([
    html.H1("FIFA World Cup Winners Dashboard", style={'textAlign': 'center'}),
    
    # Choropleth Map
    dcc.Graph(id='world-cup-map'),
    
    # Dropdowns and Interactive Components
    html.Div([
        # Country Selection Dropdown
        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in world_cup_df['Winner'].unique()],
                value=None,
                placeholder="Select a Country"
            )
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
        
        # Year Selection Dropdown
        html.Div([
            html.Label("Select Year:"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in world_cup_df['Year'].unique()],
                value=None,
                placeholder="Select a Year"
            )
        ], style={'width': '30%', 'display': 'inline-block', 'margin': '10px'}),
    ], style={'textAlign': 'center'}),
    
    # Output Displays
    html.Div([
        # Country Wins Display
        html.Div(id='country-wins-output', style={'margin': '20px', 'textAlign': 'center', 'font-size': '18px', 'font-weight': 'bold'}),
        
        # Year Details Display
        html.Div(id='year-details-output', style={'margin': '20px', 'textAlign': 'center', 'font-size': '18px', 'font-weight': 'bold'})
    ])
])

# Callback for Choropleth Map
@app.callback(
    Output('world-cup-map', 'figure'),
    [Input('country-dropdown', 'value')]
)
def update_choropleth(selected_country):
    # Create enhanced choropleth map
    fig = go.Figure()
    
    # Base layer - Light colored world map
    fig.add_trace(go.Choropleth(
        locations=wins_by_country['Country Code'],
        z=wins_by_country['Wins'],
        text=wins_by_country['Country'],
        colorscale='Blues',
        autocolorscale=False,
        marker_line_color='white',
        marker_line_width=0.5,
        colorbar_title='World Cup Wins',
        locationmode='ISO-3',
        showlegend=False,
        hoverinfo='text+z',
        hovertext=['<b>' + country + '</b><br>Wins: ' + str(wins) 
                  for country, wins in zip(wins_by_country['Country'], wins_by_country['Wins'])],
    ))
    
    # Add markers for winners with explicit sizes based on win count
    fig.add_trace(go.Scattergeo(
        locationmode='ISO-3',
        locations=wins_by_country['Country Code'],
        text=wins_by_country['Country'],
        mode='markers+text',
        marker=dict(
            size=wins_by_country['Wins'] * 10,  # Size scaled by number of wins
            color='gold',
            line=dict(width=1, color='black'),
            sizemode='diameter',
            sizemin=5
        ),
        textposition='middle center',
        textfont=dict(size=10, color='black'),
        hoverinfo='text',
        hovertext=['<b>' + country + '</b><br>Wins: ' + str(wins) 
                  for country, wins in zip(wins_by_country['Country'], wins_by_country['Wins'])],
        name='World Cup Winners'
    ))
    
    # If a country is selected, add an additional highlight
    if selected_country and selected_country in country_codes:
        selected_data = wins_by_country[wins_by_country['Country'] == selected_country]
        if not selected_data.empty:
            fig.add_trace(go.Scattergeo(
                locationmode='ISO-3',
                locations=[selected_data['Country Code'].values[0]],
                text=[selected_country],
                mode='markers',
                marker=dict(
                    size=selected_data['Wins'].values[0] * 15,  # Even larger for selection
                    color='red',
                    symbol='star',
                    line=dict(width=2, color='black')
                ),
                hoverinfo='text',
                hovertext=['<b>' + selected_country + '</b><br>Wins: ' + str(selected_data['Wins'].values[0])],
                name='Selected Country'
            ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'FIFA World Cup Winners (1930-2022)',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        geo=dict(
            showframe=True,
            showcoastlines=True,
            projection_type='natural earth',
            showcountries=True,
            countrycolor='lightgray',
            landcolor='whitesmoke',
            oceancolor='aliceblue'
        ),
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        legend=dict(
            x=0.01,
            y=0.99,
            traceorder="normal",
            font=dict(family="sans-serif", size=12),
            bgcolor="rgba(255, 255, 255, 0.5)",
        )
    )
    
    return fig

# Callback for Country Wins
@app.callback(
    Output('country-wins-output', 'children'),
    [Input('country-dropdown', 'value')]
)
def display_country_wins(selected_country):
    if selected_country:
        wins = wins_by_country[wins_by_country['Country'] == selected_country]['Wins'].values[0]
        years = world_cup_df[world_cup_df['Winner'] == selected_country]['Year'].tolist()
        years_str = ', '.join(str(year) for year in sorted(years))
        return html.Div([
            html.H3(f"{selected_country} has won the World Cup {wins} time{'s' if wins > 1 else ''}."),
            html.P(f"Championship years: {years_str}", style={'fontSize': '16px'})
        ])
    return ""

# Callback for Year Details
@app.callback(
    Output('year-details-output', 'children'),
    [Input('year-dropdown', 'value')]
)
def display_year_details(selected_year):
    if selected_year:
        year_data = world_cup_df[world_cup_df['Year'] == selected_year].iloc[0]
        return html.Div([
            html.H3(f"World Cup {selected_year}"),
            html.P(f"Winner: {year_data['Winner']}", style={'fontSize': '16px', 'color': 'darkgreen'}),
            html.P(f"Runner-up: {year_data['Runner-up']}", style={'fontSize': '16px', 'color': 'darkblue'}),
            html.P(f"Host: {year_data['Host']}", style={'fontSize': '16px'})
        ])
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)
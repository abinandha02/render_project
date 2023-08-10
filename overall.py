import dash
import json
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests

#for yearly analysis
df = pd.read_csv(r'https://raw.githubusercontent.com/abinandha02/render_project/main/crimes_against_women_2001-2014-checkpoint.csv', index_col=0)
year_df = df.groupby('Year').sum()
features_1 = year_df.columns

#data cleaning for statewise
state_df = pd.read_csv(r'https://raw.githubusercontent.com/abinandha02/render_project/main/crimes_against_women_2001-2014-checkpoint.csv')
state_df.drop(columns="Unnamed: 0", inplace=True)
state_df["STATE/UT"] = state_df.apply(lambda row: row['STATE/UT'].lower(), axis=1)
state_df['STATE/UT'].replace(
    {'a & n islands': 'A & N Islands', 'a&n islands': 'A & N Islands', 'd & n haveli': 'd & n haveli',
     'd&n haveli': 'd & n haveli', 'delhi ut': 'NCT of Delhi', 'delhi': 'NCT of Delhi'}, inplace=True, regex=True)
state_df['STATE/UT'] = state_df['STATE/UT'].str.title()

#for json and its id's

url = "https://raw.githubusercontent.com/abinandha02/render_project/7a09418ddc45f0aa3d54f3e9305494bf2c831536/states_india.geojson"
response = requests.get(url)
if response.status_code == 200:
    india_states = response.json()
    # Now you can work with the 'india_states' GeoJSON data
else:
    print("Failed to retrieve GeoJSON file from GitHub")
state_id_map = {}
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map[feature["properties"]["st_nm"]] = feature["id"]

#grouped state_wise
grouped_df1 = state_df.groupby('STATE/UT', as_index=False).sum(numeric_only=True)
state_id_map = {key: state_id_map[key] for key in sorted(state_id_map)}
grouped_df1['Total Crimes'] = grouped_df1['Rape'] + grouped_df1['Kidnapping and Abduction'] + grouped_df1['Dowry Deaths'] + \
                           grouped_df1['Assault on women with intent to outrage her modesty'] + grouped_df1[
                               'Insult to modesty of Women'] + grouped_df1['Cruelty by Husband or his Relatives'] + \
                           grouped_df1['Importation of Girls']

keys = []
values = []
for key, value in state_id_map.items():
    keys.append(key)
    values.append(value)
grouped_df1['state'] = keys
grouped_df1['id'] = values
features_2=grouped_df1.columns[2:10]

#creating dummy record for telangana
dummy_records = []
for year in range(2001, 2014):
    dummy_record = {
        'STATE/UT': 'Telangana',
        'Year': year,
        'Rape': 0,
        'Kidnapping and Abduction': 0,
        'Dowry Deaths': 0,
        'Assault on women with intent to outrage her modesty': 0,
        'Insult to modesty of Women': 0,
        'Cruelty by Husband or his Relatives': 0,
        'Importation of Girls': 0
    }
    dummy_records.append(dummy_record)
dummy_df = pd.DataFrame(dummy_records)

#grouped  state and year
state_df=state_df.append(dummy_df,ignore_index=True)
new=state_df.groupby(['STATE/UT','Year']).sum()
new.reset_index(inplace=True)
features_3 = new.columns[2:-1]

app = dash.Dash()
server=app.server

# CSS borders
plot_style = {'width': '100%', 'height': '60vh', 'border': '0px solid #d4d4d4', 'padding': '10px'}
#LAYOUT
app.layout = html.Div(style={'backgroundColor': '#f2f2f2'},  # Set the background color here
    children=[
    html.H3('CRIMES AGAINST WOMEN IN A SPECIFIC YEAR', style={'textAlign': 'center', 'marginBottom': '20px'}),


    html.Div([
        html.H4('Select a crime category', style={'marginBottom': '20px', 'marginLeft': '20px'}),
        dcc.Dropdown(
            id='crime-dropdown',
            options=[{'label': i.title(), 'value': i} for i in features_2],
            value='Rape',
            style={'width': '100%', 'marginBottom': '20px'}
        ),
        dcc.Graph(id='feature-graphic', style=plot_style)
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.H4('Select a year', style={'marginBottom': '20px', 'marginLeft': '20px'}),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(i), 'value': i} for i in year_df.index],
            value=2001,
            style={'width': '100%', 'marginBottom': '20px'}
        ),
        dcc.Graph(id='pie-graphic', style=plot_style)
    ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'}),

    #for state
        html.Div([
            html.H3("CRIME AGAINST WOMEN STATE WISE", style={'textAlign': 'center', 'marginBottom': '20px', 'marginTop': '40px'}),
            html.H4('Select a crime category', style={'marginBottom': '20px', 'marginLeft': '20px'}),
    dcc.Dropdown(
            id='state-crime-dropdown',
            options=[{'label': i.title(), 'value': i} for i in features_2],
            value='Total Crimes',
            style={'width': '60%', 'marginBottom': '10px'}
        ),
    dcc.Graph(
        id='choropleth-map',
        config={'scrollZoom': False},
        style={'height': '90vh'}
    ),
]),
    html.Div([
    html.H3('CRIMES AGAINST WOMEN IN STATE AND YEAR', style={'textAlign': 'center','marginBottom': '20px'}),
    html.H4('Select a crime category',style={'marginBottom':'20px', 'marginLeft': '20px'}),# Center-aligned heading with margin at the bottom
    dcc.Dropdown(
        id='yaxis',
        options=[{'label': i.title(), 'value': i} for i in features_3],
        value='Rape',
        style={'width': '58%', 'marginLeft': '20px', 'marginBottom': '20px'}  # Adjust the width and add left margin with margin at the bottom
    ),
    dcc.Graph(id='heatmap-graphic', style={'width': '70%', 'height': '70vh', 'marginLeft': 'auto', 'marginRight': 'auto', 'marginBottom': '20px'})  # Center-align the plot using margins with margin at the bottom
])
])

#scatter decarator
@app.callback(
    Output('feature-graphic', 'figure'),
    [Input('crime-dropdown', 'value')])
def update_graph(yaxis_name):
    return {
        'data': [go.Scatter(
            x=year_df.index,
            y=year_df[yaxis_name],
            mode='lines+markers',
            marker={
                'size': 8,
                'opacity': 0.7,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': go.Layout(
            title='Crime Trends Over The Years',
            xaxis={'title': 'Year'},
            yaxis={'title': yaxis_name.title()},
            margin={'l': 60, 'b': 60, 't':80, 'r': 10},
            hovermode='closest'
        )
    }

#pie decator
@app.callback(
    Output('pie-graphic', 'figure'),
    [Input('year-dropdown', 'value')])
def update_pie(yaxis_name):
    return {
        'data': [go.Pie(
            labels=year_df.columns,
            values=year_df.loc[yaxis_name]
        )]
    }

#map decarator
@app.callback(
    dash.dependencies.Output('choropleth-map', 'figure'),
    dash.dependencies.Input('state-crime-dropdown', 'value')
)
def update_choropleth_map(selectedcrime):
    # Create choropleth map
    choropleth_map = go.Figure(data=go.Choropleth(
        locations=grouped_df1['id'],
        z=grouped_df1[selectedcrime],
        locationmode='geojson-id',
        geojson=india_states,
        colorscale='Viridis',
        colorbar_title=selectedcrime,
        hovertext=grouped_df1['state'],
        hoverinfo='z+text'
    ))

    choropleth_map.update_geos(fitbounds="locations", visible=False)
    choropleth_map.update_layout(title="Crime analysis over States")

    return choropleth_map
#heatmap decarator
@app.callback(
    Output('heatmap-graphic', 'figure'),
    [Input('yaxis', 'value')])
def update_graph(yaxis_name):
    return {
        'data': [go.Heatmap(
            x=new['STATE/UT'],
            y=new['Year'],
            z=new[yaxis_name],
            colorscale='Viridis'  # Change the colorscale to Viridis for better visibility
        )],
        'layout': go.Layout(
            title=f'Crimes Against Women: {yaxis_name} by State and Year'  # Update the title to reflect the selected crime category
        )
    }


if __name__ == '__main__':
    app.run_server()

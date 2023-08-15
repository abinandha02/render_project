import dash
import json
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

# for yearly analysis
df = pd.read_csv(
    r'https://raw.githubusercontent.com/abinandha02/render_project/main/crimes_against_women_2001-2014-checkpoint.csv',
    index_col=0)
year_df = df.groupby('Year').sum()
year_df['Total Crimes'] = year_df['Rape'] + year_df['Kidnapping and Abduction'] + year_df[
    'Dowry Deaths'] + year_df['Assault on women with intent to outrage her modesty'] + year_df[
                                  'Insult to modesty of Women'] + year_df['Cruelty by Husband or his Relatives'] + \
                              year_df['Importation of Girls']
features_1 = year_df.columns

# data cleaning for statewise
state_df = pd.read_csv(
    r'https://raw.githubusercontent.com/abinandha02/render_project/main/crimes_against_women_2001-2014-checkpoint.csv')
state_df.drop(columns="Unnamed: 0", inplace=True)
state_df["STATE/UT"] = state_df.apply(lambda row: row['STATE/UT'].lower(), axis=1)
state_df['STATE/UT'].replace(
    {'a & n islands': 'A & N Islands', 'a&n islands': 'A & N Islands', 'd & n haveli': 'd & n haveli',
     'd&n haveli': 'd & n haveli', 'delhi ut': 'NCT of Delhi', 'delhi': 'NCT of Delhi'}, inplace=True, regex=True)
state_df['STATE/UT'] = state_df['STATE/UT'].str.title()

# grouped state_wise
grouped_df1 = state_df.groupby('STATE/UT', as_index=False).sum(numeric_only=True)
grouped_df1['Total Crimes'] = grouped_df1['Rape'] + grouped_df1['Kidnapping and Abduction'] + grouped_df1[
    'Dowry Deaths'] + \
                              grouped_df1['Assault on women with intent to outrage her modesty'] + grouped_df1[
                                  'Insult to modesty of Women'] + grouped_df1['Cruelty by Husband or his Relatives'] + \
                              grouped_df1['Importation of Girls']

features_2 = grouped_df1.columns[2:10]

# creating dummy record for telangana
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

# grouped  state and year
state_df = state_df.append(dummy_df, ignore_index=True)
new = state_df.groupby(['STATE/UT', 'Year']).sum()
new.reset_index(inplace=True)
features_3 = new.columns[2:-1]

app = dash.Dash()
server = app.server

# CSS borders
plot_style = {'width': '100%', 'height': '60vh', 'border': '0px solid #d4d4d4', 'padding': '10px'}
# LAYOUT
app.layout = html.Div(style={'backgroundColor': '#f2f2f2'}, 
                      children=[
                          html.H3('CRIMES AGAINST WOMEN IN A SPECIFIC YEAR',
                                  style={'textAlign': 'center', 'marginBottom': '20px'}),

                          html.Div([
                              html.H4('Select a crime category', style={'marginBottom': '20px', 'marginLeft': '20px'}),
                              dcc.Dropdown(
                                  id='crime-dropdown',
                                  options=[{'label': i.title(), 'value': i} for i in features_1],
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

                          # for state
                          html.Div([
                              html.H3('CRIMES AGAINST WOMEN IN STATE AND YEAR',
                                      style={'textAlign': 'center', 'marginBottom': '20px'}),
                              html.H4('Select a crime category', style={'marginBottom': '20px', 'marginLeft': '20px'}),
                              
                              dcc.Dropdown(
                                  id='yaxis',
                                  options=[{'label': i.title(), 'value': i} for i in features_3],
                                  value='Rape',
                                  style={'width': '58%', 'marginLeft': '20px', 'marginBottom': '20px'}
                               
                              ),
                              dcc.Graph(id='heatmap-graphic',
                                        style={'width': '70%', 'height': '80vh', 'marginLeft': 'auto',
                                               'marginRight': 'auto', 'marginBottom': '30px'})
                             
                          ]),  # for violin plot
                          html.Div([
                              dcc.Graph(
                                  id='violin-graphic',
                                  style={
                                      **plot_style,
                                      'width': '70%',
                                      'height': '70vh',
                                      'marginLeft': 'auto',
                                      'marginRight': 'auto',
                                      'marginBottom': '20px'
                                  }
                              )
                          ])

                      ])


# scatter decarator
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
            margin={'l': 60, 'b': 60, 't': 80, 'r': 10},
            hovermode='closest'
        )
    }


# pie decator
@app.callback(
    Output('pie-graphic', 'figure'),
    [Input('year-dropdown', 'value')])
def update_pie(yaxis_name):
    return {
        'data': [go.Pie(
            labels=year_df.columns[:-1],
            values=year_df.loc[yaxis_name]
        )]
    }


# heatmap decarator
@app.callback(
    Output('heatmap-graphic', 'figure'),
    [Input('yaxis', 'value')])
def update_choro(yaxis_name):
    return {
        'data': [go.Heatmap(
            x=new['STATE/UT'],
            y=new['Year'],
            z=new[yaxis_name],
            colorscale='Viridis'  
        )],
        'layout': go.Layout(
            title=f'Crimes Against Women: {yaxis_name} by State and Year',
            xaxis={'title': 'State/UT'},
            yaxis={'title': 'Year'},
            margin={'l': 60, 'b': 150, 't': 80, 'r': 10},
        )
    }

#violin plot
@app.callback(
    Output('violin-graphic', 'figure'),
    [Input('violin-graphic', 'children')]
)
def update_violin_plot(selected_crime):
    violin_data = []

    for crime in features_3:
        violin_data.append(go.Violin(
            y=year_df[crime],
            box_visible=True,
            line_color='blue',
            name=crime
        ))

    layout = go.Layout(title='Crime Distribution by Category',
                       yaxis_title='Number of Crimes',
                       margin={'l': 60, 'b': 60, 't': 80, 'r': 10})

    violin_fig = go.Figure(data=violin_data, layout=layout)
    return violin_fig


if __name__ == '__main__':
    app.run_server(port=8060)

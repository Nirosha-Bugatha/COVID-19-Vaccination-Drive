import plotly.express as px
import plotly.graph_objects as go
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc


#Application initialization
app = dash.Dash(__name__, external_stylesheets=["https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/flatly/bootstrap.min.css"],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = app.server

px.set_mapbox_access_token(open("./Plots/.mapbox_token").read())
#Create dataframes to read data from csv files
df_sun = pd.read_csv('./Data/final_data_2.csv')
df_origin=pd.read_csv('./Data/origin_country.csv')
df_tot = pd.read_csv('./Data/final_total_vacc_lat.csv')
df_income=pd.read_csv('./Data/income.csv')
df= pd.read_csv("./Data/grouped.csv")
#country options
country_ops= [dict(label=x,value=x) for x in df_sun['country'].unique()]
vaccine_ops=[dict(label=x,value=x) for x in df_sun['vaccines'].unique()]
all_vac = [option["value"] for option in vaccine_ops]


colors={'Moderna': 'rgb(231,41,138)',
           'Sputnik V':'#8B4513',#'#750D86',
           'Pfizer/BioNTech':'#800080',#'#862A16',
           'Oxford/AstraZeneca':'rgb(52, 235, 150)',#'rgb(15,133,84)',
           'Sinopharm/Beijing':'rgb(230,131,16)',
           'Sinovac':'rgb(136,204,238)',
           'Sinopharm/Wuhan':'#1616A7',
           'Covaxin':'#999900',#'rgb(102, 197, 204)',
           'EpiVacCorona':'#FFFF66',#'rgb(246, 207, 113)',
           'Johnson&Johnson':'#FFA07A'}
colors_country={
    "Developed": "rgb(79,79,79)",
    "Developing": "rgb(127,127,127)",
    "Underdeveloped": "rgb(229,229,229)"
}

df_merge=pd.merge(df_origin,df_sun[['country','vaccines']],on='vaccines', how='left')
df_income_vac=pd.merge(df_origin,df_tot[['country','vaccines','IncomeGroup']],on='vaccines', how='left')
df_income_merge=pd.merge(df_income,df_tot[['country','IncomeGroup','vaccines']],on='IncomeGroup',how='left')

#Application Layout in bootstrap
app.layout=dbc.Container([
  dbc.Row([
  # dbc.Nav(dbc.NavLink("Code",active=True, href="#"),pills=True,className="btn btn-link"),
   html.Div([html.A(html.Button("Project Report", id="report-button",style={'background-color': '#555555','color': 'white','margin':'5px'}),href="https://github.com/Nirosha-Bugatha/COVID-19-Vaccination-Drive/tree/main/Project%20Report")]),
   html.Div([html.A(html.Button("GitHub", id="learn-more-button",style={'background-color': '#555555','color': 'white','margin':'5px'}),href="https://github.com/Nirosha-Bugatha/COVID-19-Vaccination-Drive",)],id="button"),
     dbc.Col(html.H1("COVID-19 Vaccination Drive",
                    className='text-center mb-4',style={'font-family':'Helvetica','font-weight': 'bold'}),
            width=12),

   ]),
      dbc.Row(dbc.Col(className="btn btn-dark")),
      dbc.Row([html.Br()]),
      # dbc.Row(dbc.Col(html.Button('Clear Filters', id='reset', n_clicks=0,className="btn btn-dark"))),
      dbc.Row([
      dbc.Col([html.H5("Vaccines and their Origin Country",className='text-center',style={'font-weight': 'bold'}),
      dcc.Graph(id="bar_origin",figure={})],width=4),
      dbc.Col([html.H5("Income group of Countries",className='text-center',style={'font-weight': 'bold'}),
      dcc.Graph(id="income_group",figure={})],width=3),
      dbc.Col([html.H5("Vaccines Distribution drill down world wide",className='text-center',style={'font-weight': 'bold'}),
                dcc.Graph(id="sun_burst_chart",figure={})],width=4)],justify="around"),
     dbc.Row([html.Br()]),
     dbc.Row([
     dbc.Col([html.H5("Vaccines Distribution and Categeorization of Countries",className='text-center',style={'font-weight': 'bold'}),
     dcc.Graph(id="maps",figure={})],width=6),
     dbc.Col([html.H5("Relative comparision of Covid confirmed cases and people vaccinated with population of each country",className='text-center',style={'font-weight': 'bold'}),
     dcc.Graph(id="bubble_chart",figure={})],width=4)
     ],justify="around")
], fluid=True)

def getSizeOfNestedList(listOfElem):
    ''' Get number of elements in a nested list'''
    count = 0
    # Iterate over the list
    for elem in listOfElem:
        # Check if type of element is list
        if type(elem) == list:
            # Again call this function to get the size of this element
            count += getSizeOfNestedList(elem)
        else:
            count += 1
    return count
# Callback section: connecting the components
# ************************************************************************
#Interactions
#IncomeGroup bar_chart
@app.callback(Output("income_group","figure"),
            [Input("sun_burst_chart", "clickData"),Input('bubble_chart','clickData'),Input('maps','clickData'),Input('bar_origin','clickData'),Input('bar_origin','selectedData')])
def income_chart(clickData,bubble_click,map_click,bar_click,bar_selected):
    if clickData:
        label = clickData["points"][0]["label"] #country and vaccine names
        parent = clickData["points"][0]["parent"]
        if parent:
            df_bar_incom=df_income_merge.query('country == @label')
            df_bar_incom=df_bar_incom.drop_duplicates(subset = ["country"])
            fig_income=px.bar(df_bar_incom, y="Number of countries", x='IncomeGroup',
                                                 color="IncomeGroup",
                                                  color_discrete_map=colors_country,
                                                  text="Number of countries",
                                                  template="simple_white",height=400,width=500)
        else:
            fig_income=px.bar(df_income, y="Number of countries", x='IncomeGroup',
                                                 color="IncomeGroup",
                                                  color_discrete_map=colors_country,
                                                  text="Number of countries",
                                                   template="simple_white",height=400,width=500)
    elif bubble_click:
        country=bubble_click["points"][0]["hovertext"]
        df_bar_incom=df_income_merge.query('country == @country')
        df_bar_incom=df_bar_incom.drop_duplicates(subset = ["country"])
        fig_income=px.bar(df_bar_incom, y="Number of countries", x='IncomeGroup',
                                             color="IncomeGroup",
                                              color_discrete_map=colors_country,
                                              text="Number of countries",
                                              template="simple_white",height=400,width=500)
    elif map_click:
        map_country=map_click["points"][0]["hovertext"]
        df_bar_incom=df_income_merge.query('country == @map_country')
        df_bar_incom=df_bar_incom.drop_duplicates(subset = ["country"])
        fig_income=px.bar(df_bar_incom, y="Number of countries", x='IncomeGroup',
                                                 color="IncomeGroup",
                                                  color_discrete_map=colors_country,
                                                  text="Number of countries",
                                                  template="simple_white",height=400,width=500)
    elif bar_selected:
        values =[]
        for i in bar_selected["points"]:
            values.append(i["label"])
        df_scat=df_income_merge[df_income_merge['vaccines'].isin(values)]
        df_bar_incom=df_scat.drop_duplicates(subset = ["IncomeGroup"])
        fig_income=px.bar(df_bar_incom, y="Number of countries", x='IncomeGroup',
                                                 color="IncomeGroup",
                                                  color_discrete_map=colors_country,
                                                  text="Number of countries",
                                                  template="simple_white",height=400,width=500)
    elif bar_click:
        label = bar_click["points"][0]["label"]
        df_scat = df_income_merge.query('vaccines == @label')
        df_bar_incom=df_scat.drop_duplicates(subset = ["IncomeGroup"])
        fig_income=px.bar(df_bar_incom, y="Number of countries", x='IncomeGroup',
                                                 color="IncomeGroup",
                                                  color_discrete_map=colors_country,
                                                  text="Number of countries",
                                                  template="simple_white",height=400,width=500)
    else:
        fig_income=px.bar(df_income, y="Number of countries", x='IncomeGroup',
                                     color="IncomeGroup",
                                      color_discrete_map=colors_country,
                                      text="Number of countries",
                                      template="simple_white",height=400,width=500)
    fig_income.update_layout(clickmode='event+select')
    return fig_income

#barchart
@app.callback(Output("bar_origin", "figure"),
            [Input("sun_burst_chart", "clickData"),Input('bubble_chart','clickData'),Input('maps','clickData'),
            Input('income_group','clickData'),Input('income_group','selectedData')])
def bar_chart(clickData,bubble_click,map_click,income_click,income_selected):
    if clickData:
        label = clickData["points"][0]["label"] #country and vaccine names
        parent = clickData["points"][0]["parent"]
        if not parent:
            df_bar=df_origin.query('vaccines == @label')
            fig_bar=px.bar(df_bar, y="vaccines", x='Number of countries used',
                                     color="vaccines",
                                     orientation="h",
                                      hover_name='Number of countries used',
                                      color_discrete_map=colors,
                                      text="The country of manufacture",
                                      template="simple_white",height=400,width=700)
        else:
            df_bar_coun=df_merge.query('country == @label')
            fig_bar=px.bar(df_bar_coun, y="vaccines", x='Number of countries used',
                                         color="vaccines",
                                         orientation="h",
                                          hover_name='Number of countries used',
                                          color_discrete_map=colors,
                                          text="The country of manufacture",
                                          template="simple_white",height=400,width=700)
    elif map_click:
        map_country=map_click["points"][0]["hovertext"]
        df_map = df_merge.query('country == @map_country')
        fig_bar=px.bar(df_map, y="vaccines", x='Number of countries used',
                                                 color="vaccines",
                                                 orientation="h",
                                                  hover_name='Number of countries used',
                                                  color_discrete_map=colors,
                                                  text="The country of manufacture",
                                                  template="simple_white",height=400,width=700)
    elif bubble_click:
        country=bubble_click["points"][0]["hovertext"]
        df_bar_bubble=df_merge.query('country == @country')
        fig_bar=px.bar(df_bar_bubble, y="vaccines", x='Number of countries used',
                                     color="vaccines",
                                     orientation="h",
                                      hover_name='Number of countries used',
                                      color_discrete_map=colors,
                                      text="The country of manufacture",
                                      template="simple_white",height=400,width=700)
    elif income_click:
            label = income_click["points"][0]["label"]
            df_income=df_income_vac.query('IncomeGroup==@label')
            df_bar_incom=df_income.drop_duplicates(subset = ["vaccines"])
            fig_bar=px.bar(df_bar_incom, y="vaccines", x='Number of countries used',
                                                 color="vaccines",
                                                 orientation="h",
                                                  hover_name='Number of countries used',
                                                  color_discrete_map=colors,
                                                  text="The country of manufacture",
                                                  template="simple_white",height=400,width=700)
    elif income_selected:
        values =[]
        for i in income_selected["points"]:
            values.append(i["label"])
        df_value=df_income_vac[df_income_vac['IncomeGroup'].isin(values)]
        df_bar_incom=df_value.drop_duplicates(subset = ["vaccines"])
        fig_bar=px.bar(df_bar_incom, y="vaccines", x='Number of countries used',
                                             color="vaccines",
                                             orientation="h",
                                              hover_name='Number of countries used',
                                              color_discrete_map=colors,
                                              text="The country of manufacture",
                                              template="simple_white",height=400,width=700)
    else:
        fig_bar=px.bar(df_origin, y="vaccines", x='Number of countries used',
                         color="vaccines",
                         orientation="h",
                          hover_name='Number of countries used',
                          color_discrete_map=colors,
                          text="The country of manufacture",
                          template="simple_white",height=400,width=700)

    fig_bar.update_layout(showlegend=False,clickmode='event+select')
    return fig_bar

#Bubble chart
@app.callback(Output("bubble_chart", "figure"),
              [Input("sun_burst_chart", "clickData"),
              Input('bar_origin','clickData'),Input('maps','clickData'),Input('maps','selectedData'),Input('income_group','clickData'),
              Input('income_group','selectedData'),Input('bar_origin','selectedData')])
def bubble(clickData,bar_click,map_click,selectedData,income_click,income_selected,bar_selected):
    if clickData:
        label = clickData["points"][0]["label"] #country and vaccine names
        parent = clickData["points"][0]["parent"]
        if not parent:
                df_scat = df_sun.query('vaccines == @label')
                fig_bubble=px.scatter(df_scat, x="covid_percentage", y="Percentage",
                                    size="Percentage",
                                   color="vaccines",color_discrete_map=colors,
                                         hover_data=["country","Percentage","covid_percentage","population"],
                                         log_x=False, size_max=60,hover_name="country",
                                         labels=dict(Percentage="Relative Percentage of People Vaccinated",
                                         covid_percentage="Relative Percentage of COVID confirmed cases"),
                                         template="simple_white",height=450,width=700)
        else:
            df_scat = df_sun.query('country == @label')
            fig_bubble=px.scatter(df_scat, x="covid_percentage", y="Percentage",
                                size="Percentage",
                                   color="vaccines",color_discrete_map=colors,text='country',
                                         hover_data=["country","Percentage","covid_percentage","population"],
                                         log_x=False, size_max=60,hover_name="country",
                                         labels=dict(Percentage="Relative Percentage of People Vaccinated",
                                         covid_percentage="Relative Percentage of COVID confirmed cases"),
                                         template="simple_white",height=450,width=700)
    elif selectedData:
        values =[]
        for i in selectedData["points"]:
            values.append(i["hovertext"])
        df_value=df_sun[df_sun['country'].isin(values)]
        fig_bubble=px.scatter(df_value, x="covid_percentage", y="Percentage",
                            size="Percentage",
                            color="vaccines",color_discrete_map=colors,text='country',
                            hover_data=["country","Percentage","covid_percentage","population"],
                             log_x=False, size_max=60,hover_name="country",
                            labels=dict(Percentage="Relative Percentage of People Vaccinated",
                            covid_percentage="Relative Percentage of COVID confirmed cases"),
                            template="simple_white",height=450,width=700)
    elif income_selected:
        values =[]
        for i in income_selected["points"]:
            values.append(i["label"])
        df_income=df_tot[df_tot['IncomeGroup'].isin(values)]
        fig_bubble=px.scatter(df_income, x="covid_percentage", y="Percentage",
                            size="Percentage",
                    color="vaccines",color_discrete_map=colors,
                     hover_data=["country","Percentage","covid_percentage","population"],
                    log_x=False, size_max=60,hover_name="country",
                    labels=dict(Percentage="Relative Percentage of People Vaccinated",
                    covid_percentage="Relative Percentage of COVID confirmed cases"),
                    template="simple_white",height=450,width=700)
    elif bar_selected:
        values =[]
        for i in bar_selected["points"]:
            values.append(i["label"])
        df_scat=df_sun[df_sun['vaccines'].isin(values)]
        fig_bubble=px.scatter(df_scat, x="covid_percentage", y="Percentage",
                            size="Percentage",
                    color="vaccines",color_discrete_map=colors,
                     hover_data=["country","Percentage","covid_percentage","population"],
                     log_x=False, size_max=60,hover_name="country",
                    labels=dict(Percentage="Relative Percentage of People Vaccinated",
                    covid_percentage="Relative Percentage of COVID confirmed cases"),
                    template="simple_white",height=450,width=700)
    elif map_click:
        map_country=map_click["points"][0]["hovertext"]
        df_map = df_sun.query('country == @map_country')
        fig_bubble=px.scatter(df_map, x="covid_percentage", y="Percentage",
                            size="Percentage",
                            color="vaccines",color_discrete_map=colors,text='country',
                             hover_data=["country","Percentage","covid_percentage","population"],
                             log_x=False, size_max=60,hover_name="country",
                            labels=dict(Percentage="Relative Percentage of People Vaccinated",
                            covid_percentage="Relative Percentage of COVID confirmed cases"),
                            template="simple_white",height=450,width=700)
    elif bar_click:
        label = bar_click["points"][0]["label"]
        df_scat = df_sun.query('vaccines == @label')
        fig_bubble=px.scatter(df_scat, x="covid_percentage", y="Percentage",
                            size="Percentage",
                    color="vaccines",color_discrete_map=colors,
                     hover_data=["country","Percentage","covid_percentage","population"],
                     log_x=False, size_max=60,hover_name="country",
                    labels=dict(Percentage="Relative Percentage of People Vaccinated",
                    covid_percentage="Relative Percentage of COVID confirmed cases"),
                    template="simple_white",height=450,width=700)
    elif income_click:
        label = income_click["points"][0]["label"]
        df_income=df_tot.query('IncomeGroup==@label')
        fig_bubble=px.scatter(df_income, x="covid_percentage", y="Percentage",
                            size="Percentage",
                    color="vaccines",color_discrete_map=colors,
                     hover_data=["country","Percentage","covid_percentage","population"],
                    log_x=False, size_max=60,hover_name="country",
                    labels=dict(Percentage="Relative Percentage of People Vaccinated",
                    covid_percentage="Relative Percentage of COVID confirmed cases"),
                    template="simple_white",height=450,width=700)
    else:
        fig_bubble=px.scatter(df_sun,  x="covid_percentage", y="Percentage",
                            size="Percentage",
                   color="vaccines",color_discrete_map=colors,
                         hover_data=["country","Percentage","covid_percentage","population"],
                          log_x=False, size_max=60,hover_name="country",
                         labels=dict(Percentage="Relative Percentage of People Vaccinated",
                         covid_percentage="Relative Percentage of COVID confirmed cases"),
                         template="simple_white",height=450,width=700)
    fig_bubble.update_layout(showlegend=False,clickmode='event+select')
    return fig_bubble

#heirarchy chart
@app.callback(Output("sun_burst_chart", "figure"),
              [Input("bubble_chart", "clickData"),
              Input('bar_origin','clickData'),
              Input('maps','clickData'),Input('maps','selectedData'),Input('income_group','clickData'),Input('income_group','selectedData'),Input('bar_origin','selectedData')])
def sunburst(clickData,bar_click,map_click,selectedData,income_click,income_selected,bar_selected):
    if clickData:
        country=clickData["points"][0]["hovertext"]
        df_sun_country=df_sun.query('country == @country')
        fig=px.sunburst(df_sun_country,
        path=['vaccines','country'],
        values='people_vaccinated',
        maxdepth=-1,
        color='vaccines',
        color_discrete_map=colors,height=400,width=700)
        fig.update_traces(textinfo='label+value')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    elif selectedData:
        values =[]
        for i in selectedData["points"]:
            values.append(i["hovertext"])
        df_value=df_sun[df_sun['country'].isin(values)]
        fig=px.sunburst(df_value,
        path=['vaccines','country'],
        values='people_vaccinated',
        maxdepth=-1,
        color='vaccines',
        color_discrete_map=colors,height=400,width=700)
        fig.update_traces(textinfo='label+value')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    elif income_selected:
        values =[]
        for i in income_selected["points"]:
            values.append(i["label"])
        df_income=df_tot[df_tot['IncomeGroup'].isin(values)]
        fig=px.sunburst(df_income,
        path=['vaccines','country'],
         values='people_vaccinated',
         maxdepth=-1,
         color='vaccines',
         color_discrete_map=colors,height=400,width=700)
        fig.update_traces(textinfo='label+value')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    elif map_click:
            map_country=map_click["points"][0]["hovertext"]
            df_sun_country=df_sun.query('country == @map_country')
            fig=px.sunburst(df_sun_country,
            path=['vaccines','country'],
            values='people_vaccinated',
            maxdepth=-1,
            color='vaccines',
            color_discrete_map=colors,height=400,width=700)
            fig.update_traces(textinfo='label+value')
            fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    elif bar_click:
        bar_vac=bar_click["points"][0]["label"]
        df_sun_vacc=df_sun.query('vaccines == @bar_vac')
        fig=px.sunburst(df_sun_vacc,
        path=['vaccines','country'],
         values='people_vaccinated',
         maxdepth=-1,
         color='vaccines',
         color_discrete_map=colors,height=400,width=700)
        fig.update_traces(textinfo='label+value')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    elif bar_selected:
        values =[]
        for i in bar_selected["points"]:
            values.append(i["label"])
        df_sun_vacc=df_sun[df_sun['vaccines'].isin(values)]
        fig=px.sunburst(df_sun_vacc,
        path=['vaccines','country'],
         values='people_vaccinated',
         maxdepth=-1,
         color='vaccines',
         color_discrete_map=colors,height=400,width=700)
        fig.update_traces(textinfo='label+value')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    elif income_click:
        label = income_click["points"][0]["label"]
        df_income=df_tot.query('IncomeGroup==@label')
        fig=px.sunburst(df_income,
        path=['vaccines','country'],
         values='people_vaccinated',
         maxdepth=-1,
         color='vaccines',
         color_discrete_map=colors,height=400,width=700)
        fig.update_traces(textinfo='label+value')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    else:
        fig=px.sunburst(df_sun,
        path=['vaccines','country'],
         values='people_vaccinated',
         maxdepth=-1,
         color='vaccines',
         color_discrete_map=colors,height=400,width=700)
        fig.update_traces(textinfo='label+value')
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
    fig.update_layout(clickmode='event+select')
    # fig.update_traces(textfont_color='white')
    return fig
#Maps
@app.callback(Output("maps", "figure"),
              [Input('sun_burst_chart','clickData'),Input("bubble_chart", "clickData"),Input("bubble_chart", "selectedData"),
              Input("bar_origin", "clickData"),Input('income_group','clickData'),Input('income_group','selectedData'),Input('bar_origin','selectedData')])
def display_maps(clickData,value,value1,bar_click,income_click,income_selected,bar_selected):
    if clickData:
        label = clickData["points"][0]["label"] #country and vaccine names
        parent = clickData["points"][0]["parent"]
        if not parent:
                df_scat = df_tot.query('vaccines == @label')
                fig_map = px.choropleth(df_scat,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,
                                        locationmode = "country names"
                                        )
                fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
                fig1 =px.scatter_geo(df_scat,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                                     color_discrete_map=colors
                                     )
                fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
                fig1.update_traces(showlegend=False)
                fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                # fig_map.add_trace(fig1.data[0])
                count = getSizeOfNestedList(fig1["data"])
                if count > 0 :
                    i=0
                    while i!=count:
                        fig_map.add_trace(fig1.data[i])
                        i=i+1
                else:
                    fig_map.add_trace(fig1.data[0])

        else:
            df_scat = df_sun.query('country == @label')
            df_maps = df_tot.query('country == @label')
            fig_map = px.choropleth(df_maps,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,
                                    locationmode = "country names"
                                    )
            fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
            fig1 =px.scatter_geo(df_scat,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                                 color_discrete_map=colors
                                 )
            fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
            fig1.update_traces(showlegend=False)
            fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            # fig_map.add_trace(fig1.data[0])
            count = getSizeOfNestedList(fig1["data"])
            if count > 0 :
                i=0
                while i!=count:
                    fig_map.add_trace(fig1.data[i])
                    i=i+1
            else:
                fig_map.add_trace(fig1.data[0])

    elif value1:
        values =[]
        for i in value1["points"]:
            values.append(i["hovertext"])
        df_value=df_sun[df_sun['country'].isin(values)]
        df_maps = df_tot[df_tot['country'].isin(values)]
        fig_map = px.choropleth(df_maps,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,
                                locationmode = "country names"
                                )
        fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
        fig1 =px.scatter_geo(df_value,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                             color_discrete_map=colors
                             )
        fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
        fig1.update_traces(showlegend=False)
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # fig_map.add_trace(fig1.data[0])
        count = getSizeOfNestedList(fig1["data"])
        if count > 0 :
            i=0
            while i!=count:
                fig_map.add_trace(fig1.data[i])
                i=i+1
        else:
            fig_map.add_trace(fig1.data[0])
    elif value:
        values =[]
        for i in value["points"]:
            values.append(i["hovertext"])
        df_value=df_sun[df_sun['country'].isin(values)]
        df_maps = df_tot[df_tot['country'].isin(values)]
        fig_map = px.choropleth(df_maps,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,
                                locationmode = "country names"
                                )
        fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
        fig1 =px.scatter_geo(df_value,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                             color_discrete_map=colors
                             )
        fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
        fig1.update_traces(showlegend=False)
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # fig_map.add_trace(fig1.data[0])
        count = getSizeOfNestedList(fig1["data"])
        if count > 0 :
            i=0
            while i!=count:
                fig_map.add_trace(fig1.data[i])
                i=i+1
        else:
            fig_map.add_trace(fig1.data[0])
    elif bar_click:
        bar_vac=bar_click["points"][0]["label"]
        df_sun_vacc=df_tot.query('vaccines == @bar_vac')
        df_map2=df_sun.query('vaccines == @bar_vac')
        fig_map = px.choropleth(df_sun_vacc,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,
                                locationmode = "country names"
                                )
        fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
        fig1 =px.scatter_geo(df_map2,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                             color_discrete_map=colors
                             )
        fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
        fig1.update_traces(showlegend=False)
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # fig_map.add_trace(fig1.data[0])
        count = getSizeOfNestedList(fig1["data"])
        if count > 0 :
            i=0
            while i!=count:
                fig_map.add_trace(fig1.data[i])
                i=i+1
        else:
            fig_map.add_trace(fig1.data[0])
    elif bar_selected:
        values =[]
        for i in bar_selected["points"]:
            values.append(i["label"])
        df_sun_vacc=df_tot[df_tot['vaccines'].isin(values)]
        df_map2=df_sun[df_sun['vaccines'].isin(values)]
        fig_map = px.choropleth(df_sun_vacc,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,
                                locationmode = "country names"
                                )
        fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
        fig1 =px.scatter_geo(df_map2,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                             color_discrete_map=colors
                             )
        fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
        fig1.update_traces(showlegend=False)
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # fig_map.add_trace(fig1.data[0])
        count = getSizeOfNestedList(fig1["data"])
        if count > 0 :
            i=0
            while i!=count:
                fig_map.add_trace(fig1.data[i])
                i=i+1
        else:
            fig_map.add_trace(fig1.data[0])
    elif income_selected:
        values =[]
        for i in income_selected["points"]:
            values.append(i["label"])
        df_income=df_tot[df_tot['IncomeGroup'].isin(values)]
        fig_map = px.choropleth(df_income,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,
                                locationmode = "country names"
                                )
        fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
        fig1 =px.scatter_geo(df_income,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                             color_discrete_map=colors
                             )
        fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
        fig1.update_traces(showlegend=False)
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        count = getSizeOfNestedList(fig1["data"])
        if count > 0 :
            i=0
            while i!=count:
                fig_map.add_trace(fig1.data[i])
                i=i+1
        else:
            fig_map.add_trace(fig1.data[0])
    elif income_click:
        income_bar=income_click["points"][0]["label"]
        df_income=df_tot.query('IncomeGroup==@income_bar')
        #df_map2=df_sun.query('IncomeGroup==@income_bar')
        fig_map = px.choropleth(df_income,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,
                                locationmode = "country names"
                                )
        fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
        fig1 =px.scatter_geo(df_income,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                             color_discrete_map=colors
                             )
        fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
        fig1.update_traces(showlegend=False)
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        # fig_map.add_trace(fig1.data[0])
        count = getSizeOfNestedList(fig1["data"])
        if count > 0 :
            i=0
            while i!=count:
                fig_map.add_trace(fig1.data[i])
                i=i+1
        else:
            fig_map.add_trace(fig1.data[0])
    else:
        fig_map = px.choropleth(df_tot,locations='country',hover_name='country',color='IncomeGroup',color_discrete_map=colors_country,#colors_country,
                                locationmode = "country names"
                                )
        fig_map.update_traces(showlegend=False,selector=dict(type='scattergeo'),marker_size=9)
        fig1 =px.scatter_geo(df_tot,locations='country',hover_name='country',color='vaccines',size='Percentage',locationmode = "country names",
                            color_discrete_map=colors
                            )
        fig1.update_geos(showcountries=True, countrycolor="RebeccaPurple")
        fig1.update_traces(showlegend=False)
        fig1.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        count = getSizeOfNestedList(fig1["data"])
        if count > 0 :
            i=0
            while i!=count:
                fig_map.add_trace(fig1.data[i])
                i=i+1
        else:
            fig_map.add_trace(fig1.data[0])
    fig_map.update_layout(clickmode='event+select')
    return fig_map

if __name__ == '__main__':
    app.run_server(debug=True)

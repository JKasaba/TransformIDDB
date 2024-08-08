from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from transformID_gen import generate_urn

# MongoDB connection
uri = "mongodb+srv://kasaba:1wGjJqwEnuP7p2Fp@aces-cluster.fafjow5.mongodb.net/?retryWrites=true&w=majority&appName=Aces-Cluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['aces_ID']
collection = db['PendingRequests']


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

primaries_options = [
    {'label': 'Rec.709', 'value': 'Rec.709'},
    {'label': 'Rec.2020', 'value': 'Rec.2020'},
    {'label': 'P3', 'value': 'P3'},
    {'label': 'XYZ', 'value': 'XYZ'}
]

white_options = [
    {'label': 'D65', 'value': 'D65'},
    {'label': 'D60', 'value': 'D60'},
    {'label': 'E', 'value': 'E'}
]

eotf_options = [
    {'label': 'PQ', 'value': 'PQ'},
    {'label': 'HLG', 'value': 'HLG'},
    {'label': 'Gamma 2.2', 'value': 'Gamma 2.2'}
]

# Define the layout
app.layout = dbc.Container([
    dbc.Tabs([
        dbc.Tab(label="Create New Transform ID", tab_id="tab-1"),
        dbc.Tab(label="Search with Unique Identifier", tab_id="tab-2"),
        dbc.Tab(label="View All Data", tab_id="tab-3")
    ], id="tabs", active_tab="tab-1"),
    html.Div(id="tab-content", className="p-4")
])

# Data Entry Form layout
data_entry_layout = dbc.Form([
    dbc.Row([
        dbc.Col([
            dbc.Label("Organization"),
            dbc.Input(id='organization', type='text', placeholder='E.G. Academy', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("ACES Version"),
            dbc.Input(id='aces_version', type='text', placeholder='Enter ACES Version', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Transform Version"),
            dbc.Input(id='transform_version', type='text', placeholder='Enter Transform Version', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Limiting Primaries"),
            dcc.Dropdown(id='limiting_primaries', options=primaries_options, placeholder='Select Limiting Primaries', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Limiting White"),
            dcc.Dropdown(id='limiting_white', options=white_options, placeholder='Select Limiting White', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Limiting White (nits)"),
            dbc.Input(id='limiting_white_nits', type='number', placeholder='Enter Limiting White (nits)', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Peak Luminance (value used in tonescale function)"),
            dbc.Input(id='peak_luminance', type='number', placeholder='Enter Peak Luminance', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Linear Scale"),
            dbc.Input(id='linear_scale', type='text', placeholder='Enter Linear Scale', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Encoding Primaries"),
            dcc.Dropdown(id='encoding_primaries', options=primaries_options, placeholder='Select Encoding Primaries', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("Encoding White"),
            dcc.Dropdown(id='encoding_white', options=white_options, placeholder='Select Encoding White', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Label("EOTF"),
            dbc.Input(id='eotf', type='text', placeholder='Enter EOTF', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button('Generate URN', id='generate-urn-button', n_clicks=0, color='primary', className='me-2'),
            dbc.Button('Submit', id='submit-button', n_clicks=0, color='primary')
        ], width=12)
    ]),
    html.Div(id='output-container', className="mt-4")
])

# Search Form layout
search_layout = dbc.Form([
    dbc.Row([
        dbc.Col([
            dbc.Label("Unique ID"),
            dbc.Input(id='search_unique_id', type='text', placeholder='Enter Unique ID', className='mb-3')
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button('Search', id='search-button', n_clicks=0, color='primary')
        ], width=12)
    ]),
    html.Div(id='search-results', className="mt-4")
])

# Layout for viewing all data
view_all_layout = html.Div([
    dbc.Button('Load Data', id='load-data-button', n_clicks=0, color='primary', className='mb-3'),
    html.Div(id='all-data-container')
])

# Update tab content
@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab")]
)
def render_tab_content(active_tab):
    if active_tab == "tab-1":
        return data_entry_layout
    elif active_tab == "tab-2":
        return search_layout
    elif active_tab == "tab-3":
        return view_all_layout
    return html.P("This shouldn't ever be displayed...")


@app.callback(
    Output('urn-output', 'children'),
    [Input('generate-urn-button', 'n_clicks')],
    [State('organization', 'value'), State('aces_version', 'value'),
     State('transform_version', 'value'), State('limiting_primaries', 'value'),
     State('limiting_white', 'value'), State('limiting_white_nits', 'value'),
     State('peak_luminance', 'value'), State('linear_scale', 'value'),
     State('encoding_primaries', 'value'), State('encoding_white', 'value'),
     State('eotf', 'value')]
)
def generate_urn(n_clicks, organization, aces_version, transform_version, limiting_primaries,
                  limiting_white, limiting_white_nits, peak_luminance, linear_scale,
                  encoding_primaries, encoding_white, eotf):
    if n_clicks > 0:
        unique_id = f"{limiting_primaries}-{limiting_white}_{limiting_white_nits}nits_in_{encoding_primaries}-{encoding_white}_{eotf}".replace(" ", "_")
        urn = f"urn:ampas:aces:transformID:v2.0:Output.{organization}.{unique_id}.{aces_version}.{transform_version}"
        return f"Generated URN: {urn}"
    return ""

# Define callback to handle form submission
@app.callback(
    Output('output-container', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('organization', 'value'), State('aces_version', 'value'),
     State('transform_version', 'value'), State('limiting_primaries', 'value'),
     State('limiting_white', 'value'), State('limiting_white_nits', 'value'),
     State('peak_luminance', 'value'), State('linear_scale', 'value'),
     State('encoding_primaries', 'value'), State('encoding_white', 'value'),
     State('eotf', 'value')]
)
def update_output(n_clicks, organization, aces_version, transform_version, limiting_primaries,
                  limiting_white, limiting_white_nits, peak_luminance, linear_scale,
                  encoding_primaries, encoding_white, eotf):
    if n_clicks > 0:
        unique_id = f"{limiting_primaries}-{limiting_white}_{limiting_white_nits}nits_in_{encoding_primaries}-{encoding_white}_{eotf}".replace(" ", "_")
        urn = f"urn:ampas:aces:transformID:v2.0:Output.{organization}.{unique_id}.{aces_version}.{transform_version}"
        data = {
            "urn": urn,
            "unique_ID": unique_id,
            "organization": organization,
            "aces_version": aces_version,
            "transform_version": transform_version,
            "limiting_primaries": limiting_primaries,
            "limiting_white": limiting_white,
            "limiting_white_nits": limiting_white_nits,
            "peak_luminance": peak_luminance,
            "linear_scale": linear_scale,
            "encoding_primaries": encoding_primaries,
            "encoding_white": encoding_white,
            "eotf": eotf
        }
        try:
            collection.insert_one(data)
            return f"Data inserted successfully \n Your Unique ID is {unique_id}"
        except Exception as e:
            return f"An error occurred: {e}"

# Define callback to handle search functionality
@app.callback(
    Output('search-results', 'children'),
    [Input('search-button', 'n_clicks')],
    [State('search_unique_id', 'value')]
)
def search_data(n_clicks, search_unique_id):
    if n_clicks > 0:
        try:
            result = collection.find_one({"unique_ID": search_unique_id})
            if result:
                return html.Div([
                    html.P(f"URN: {result['urn']}"),
                    html.P(f"Organization: {result['organization']}"),
                    html.P(f"ACES Version: {result['aces_version']}"),
                    html.P(f"Transform Version: {result['transform_version']}"),
                    html.P(f"Limiting Primaries: {result['limiting_primaries']}"),
                    html.P(f"Limiting White: {result['limiting_white']}"),
                    html.P(f"Limiting White (nits): {result['limiting_white_nits']}"),
                    html.P(f"Peak Luminance: {result['peak_luminance']}"),
                    html.P(f"Linear Scale: {result['linear_scale']}"),
                    html.P(f"Encoding Primaries: {result['encoding_primaries']}"),
                    html.P(f"Encoding White: {result['encoding_white']}"),
                    html.P(f"EOTF: {result['eotf']}"),
                ])
            else:
                return "No data found for the given Unique ID."
        except Exception as e:
            return f"An error occurred: {e}"

# Define callback to load and display all data
@app.callback(
    Output('all-data-container', 'children'),
    [Input('load-data-button', 'n_clicks')]
)
def load_all_data(n_clicks):
    if n_clicks > 0:
        try:
            results = collection.find({})
            all_data = []
            for result in results:
                all_data.append(html.Div([
                    html.P(f"URN: {result['urn']}"),
                    html.P(f"Organization: {result['organization']}"),
                    html.P(f"ACES Version: {result['aces_version']}"),
                    html.P(f"Transform Version: {result['transform_version']}"),
                    html.P(f"Limiting Primaries: {result['limiting_primaries']}"),
                    html.P(f"Limiting White: {result['limiting_white']}"),
                    html.P(f"Limiting White (nits): {result['limiting_white_nits']}"),
                    html.P(f"Peak Luminance: {result['peak_luminance']}"),
                    html.P(f"Linear Scale: {result['linear_scale']}"),
                    html.P(f"Encoding Primaries: {result['encoding_primaries']}"),
                    html.P(f"Encoding White: {result['encoding_white']}"),
                    html.P(f"EOTF: {result['eotf']}"),
                    html.Hr()
                ]))
            return all_data
        except Exception as e:
            return f"An error occurred: {e}"


if __name__ == '__main__':
    app.run_server(debug=True, port = 8055)


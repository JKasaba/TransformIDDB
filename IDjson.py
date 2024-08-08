from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import json
from bson.json_util import dumps

# MongoDB connection
uri = "mongodb+srv://kasaba:1wGjJqwEnuP7p2Fp@aces-cluster.fafjow5.mongodb.net/?retryWrites=true&w=majority&appName=Aces-Cluster"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['aces_ID']
collection = db['TransformID2']

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    ),
    html.Pre(id='json-data', style={'whiteSpace': 'pre-wrap', 'wordBreak': 'break-all'})
])

# Define the callback to update the JSON data
@app.callback(
    Output('json-data', 'children'),
    [Input('interval-component', 'n_intervals')]
)
def update_json_data(n):
    # Fetch the data from MongoDB
    data = collection.find()
    json_data = dumps(data, indent=4)
    return json_data

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port= 8060)

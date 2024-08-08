from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State, ALL
from bson.json_util import dumps
import dash_bootstrap_components as dbc
from bson.objectid import ObjectId

uri = "mongodb+srv://kasaba:1wGjJqwEnuP7p2Fp@aces-cluster.fafjow5.mongodb.net/?retryWrites=true&w=majority&appName=Aces-Cluster"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['aces_ID']
collection = db['TransformID2']
pending_collection = db['PendingRequests']  # Collection for pending requests

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

# Define the layout of the app
app.layout = html.Div([
    html.H1("Admin Validation Page"),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    ),
    html.Div(id='pending-requests')
])

# Combined callback to update the pending requests and handle approval/denial
@app.callback(
    Output('pending-requests', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input({'type': 'approve-button', 'index': ALL}, 'n_clicks'),
     Input({'type': 'deny-button', 'index': ALL}, 'n_clicks')],
    [State({'type': 'approve-button', 'index': ALL}, 'id'),
     State({'type': 'deny-button', 'index': ALL}, 'id')]
)
def update_and_handle_requests(n, approve_n_clicks, deny_n_clicks, approve_ids, deny_ids):
    ctx = dash.callback_context

    # Handle approval/denial actions
    if ctx.triggered:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id != 'interval-component':
            button_type, request_id = eval(button_id)['type'], eval(button_id)['index']
            if button_type == 'approve-button':
                request = pending_collection.find_one({'_id': ObjectId(request_id)})
                if request:
                    collection.insert_one(request)
                    pending_collection.delete_one({'_id': ObjectId(request_id)})
            elif button_type == 'deny-button':
                pending_collection.delete_one({'_id': ObjectId(request_id)})

    # Fetch pending requests from MongoDB
    pending_requests = list(pending_collection.find())
    if not pending_requests:
        return html.Div("No pending requests.")

    # Create a table of pending requests with approve/deny buttons
    rows = []
    for request in pending_requests:
        request_id = str(request['_id'])
        request_data = dumps(request, indent=4)
        rows.append(html.Tr([
            html.Td(html.Pre(request_data)),
            html.Td(html.Button('Approve', id={'type': 'approve-button', 'index': request_id}, n_clicks=0)),
            html.Td(html.Button('Deny', id={'type': 'deny-button', 'index': request_id}, n_clicks=0))
        ]))

    table = html.Table([
        html.Thead(html.Tr([html.Th("Request Data"), html.Th("Approve"), html.Th("Deny")])),
        html.Tbody(rows)
    ])

    return table

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

import dash
import dash_core_components as dcc
import dash_html_components as html

#from dash import dcc
#from dash import html

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

#from dash import dash_table
import dash_table
import plotly.graph_objs as go
import dash_daq as daq
from textwrap import dedent

import pandas as pd

app = dash.Dash(__name__)
server = app.server
app.config['suppress_callback_exceptions'] = True

dfpath = "data/spc_data.csv"

df = pd.read_csv(dfpath)
params = list(df)
max_length = len(df)

suffix_row = '_row'
suffix_button_id = '_button'
suffix_sparkline_graph = '_sparkline_graph'
suffix_count = '_count'
suffix_ooc_n = '_OOC_number'
suffix_ooc_g = '_OOC_graph'
suffix_indicator = '_indicator'

theme = {
    'dark': True,
    'detail': '#2d3038',  # Background-card
    'primary': '#007439',  # Green
    'secondary': '#FFD15F',  # Accent
}


def build_banner():
    return html.Div(
        id='banner',
        className="banner",
        children=[
            html.H5('LCAero - Real-time sustainability performance'),
            html.Button(
                id='learn-more-button',
                children="LEARN MORE",
                n_clicks=0,
            ),
            html.Img(
                src="https://s3-us-west-1.amazonaws.com/plotly-tutorials/logo/new-branding/dash-logo-by-plotly-stripe-inverted.png") #updatae LOGO
        ]
    )


def build_tabs():
    return html.Div(
        id='tabs',
        className='row container scalable',
        children=[
            dcc.Tabs(
                id='app-tabs',
                value='tab3',
                className='custom-tabs',
                children=[
                    dcc.Tab(
                        id='Specs-tab',
                        label='Specification Settings',
                        value='tab1',
                        className='custom-tab',
                        selected_className='custom-tab--selected',
                        disabled_style={
                            'backgroundColor': '#2d3038',
                            'color': '#95969A',
                            'borderColor': '#23262E',
                            'display': 'flex',
                            'flex-direction': 'column',
                            'alignItems': 'center',
                            'justifyContent': 'center'
                        },
                        disabled=False
                    ),
                    dcc.Tab(
                        id='Control-chart-tab',
                        label='Control Charts Dashboard',
                        value='tab2',
                        className='custom-tab',
                        selected_className='custom-tab--selected',
                        disabled_style= {
                            'backgroundColor': '#2d3038',
                            'color': '#95969A',
                            'borderColor': '#23262E',
                            'display': 'flex',
                            'flex-direction': 'column',
                            'alignItems': 'center',
                            'justifyContent': 'center'
                        },
                        disabled=False)
                ]
            )
        ]
    )


def init_df():
    ret = {}
    for col in list(df[1:]):
        data = df[col]
        stats = data.describe()

        std = stats['std'].tolist()
        ucl = (stats['mean'] + 3 * stats['std']).tolist()
        lcl = (stats['mean'] - 3 * stats['std']).tolist()
        usl = (stats['mean'] + stats['std']).tolist()
        lsl = (stats['mean'] - stats['std']).tolist()

        ret.update({
            col: {
                'count': stats['count'].tolist(),
                'data': data,
                'mean': stats['mean'].tolist(),
                'std': std,
                'ucl': round(ucl, 3),
                'lcl': round(lcl, 3),
                'usl': round(usl, 3),
                'lsl': round(lsl, 3),
                'min': stats['min'].tolist(),
                'max': stats['max'].tolist(),
                'ooc': populate_ooc(data, ucl, lcl)
            }
        })

    return ret


def populate_ooc(data, ucl, lcl):
    ooc_count = 0
    ret = []
    for i in range(len(data)):
        if data[i] >= ucl or data[i] <= lcl:
            ooc_count += 1
            ret.append(ooc_count / (i + 1))
        else:
            ret.append(ooc_count / (i + 1))
    return ret


def build_tab_1():
    return [
        # Manually select metrics
        html.Div(
            id='set-specs-intro-container',
            className='twelve columns',
            children=html.P("Use historical control limits to establish a benchmark, or set new values.")
        ),
        html.Div(
            className='five columns',
            children=[
                html.Label(id='metric-select-title', children='Select Metrics', style={"font-weight": "bold"}),
                html.Br(),
                dcc.Dropdown(
                    id='metric-select-dropdown',
                    options=list({'label': param, 'value': param} for param in params[1:]),
                    value=params[1]
               ),
        html.Div(
            className='',
            children=[
                html.Br(),
                html.Label(id='aircraft-select', children='Select Aircraft', style={"font-weight": "bold"}),
                html.Br(),
                dcc.Dropdown(
                    id='aircraft-select-dropdown',
                    options=[
                        {'label': 'A332', 'value': 'A332'},
                        {'label': 'A333', 'value': 'A333'},
                        {'label': 'A350', 'value': 'A350'},
                        {'label': 'A380', 'value': 'A380'},
                        {'label': 'B77W', 'value': 'B77W'},
                        {'label': 'B748', 'value': 'B748'},
                        {'label': 'B788', 'value': 'B788'},
                    ],
                    value='A380',                    
                    ),
                    ]
                ),
        html.Div(id='input-path', children='A380')
                ]),

        html.Div(
            className='five columns',
            children=[
                html.Div(
                    id='value-setter-panel'),
                html.Br(),
                html.Button('Update', id='value-setter-set-btn'),
                html.Button('View current setup', id='value-setter-view-btn', n_clicks=0),
                html.Div(id='value-setter-view-output', className='output-datatable')
            ]
        )
    ]

@app.callback(
    Output('input-path', 'children'),
    Input('aircraft-select-dropdown', 'value')
)

def update_df(value):
    dfpath = "backend/model/{}.csv".format(value)
    return dfpath

df = pd.read_csv(dfpath)
params = list(df)
max_length = len(df)

state_dict = init_df()


def init_value_setter_store():
    # Initialize store data
    state_dict = init_df()
    return state_dict


ud_usl_input = daq.NumericInput(id='ud_usl_input', size=200, max=9999999, style={'width': '100%', 'height': '100%'})
ud_lsl_input = daq.NumericInput(id='ud_lsl_input', size=200, max=9999999, style={'width': '100%', 'height': '100%'})
ud_ucl_input = daq.NumericInput(id='ud_ucl_input', size=200, max=9999999, style={'width': '100%', 'height': '100%'})
ud_lcl_input = daq.NumericInput(id='ud_lcl_input', size=200, max=9999999, style={'width': '100%', 'height': '100%'})


def build_value_setter_line(line_num, label, value, col3):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className='four columns'),
            html.Label(value, className='four columns'),
            html.Div(col3, className='four columns')],
        className='row'
    )


def generate_modal():
    return html.Div(
        id='markdown',
        className="modal",
        style={'display': 'none'},
        children=(
            html.Div(
                id="markdown-container",
                className="markdown-container",
                children=[
                    html.Div(
                        className='close-container',
                        children=html.Button(
                            "Close",
                            id="markdown_close",
                            n_clicks=0,
                            className="closeButton"
                        )
                    ),
                    html.Div(
                        className='markdown-text',
                        children=dcc.Markdown(
                            children=dedent('''
                        **What is this mock app about?**

                        'dash-manufacture-spc-dashboard` is a dashboard for monitoring read-time process quality along manufacture production line. 

                        **What does this app show**

                        Click on buttons in `Parameter' column to visualize details of measurement trendlines on the bottom panel.

                        The Sparkline on top panel and Control chart on bottom panel show Shewhart process monitor using mock data. 
                        The trend is updated every other second to simulate real-time measurements. Data falling outside of six-sigma control limit are signals indicating 'Out of Control(OOC)', and will 
                        trigger alerts instantly for a detailed checkup. 
                    '''))
                    )
                ]
            )
        )
    )



app.layout = html.Div(
    children=[
        build_banner(),
        build_tabs(),
        # Main app
        html.Div(
            id='app-content',
            className='container scalable'
        ),
        html.Button('Proceed to Measurement', id='tab-trigger-btn', n_clicks=0,
                    style={'display': 'inline-block',
                           'float': 'right'}),
        dcc.Store(
            id='value-setter-store',
            data=init_value_setter_store()
        ),
        generate_modal(),
    ]
)


# ===== Callbacks to update values based on store data and dropdown selection =====
@app.callback(
    output=[
        Output('value-setter-panel', 'children'),
        Output('ud_usl_input', 'value'),
        Output('ud_lsl_input', 'value'),
        Output('ud_ucl_input', 'value'),
        Output('ud_lcl_input', 'value')],
    inputs=[Input('metric-select-dropdown', 'value')],
    state=[State('value-setter-store', 'data')]
)
def build_value_setter_panel(dd_select, state_value):
    return [
               build_value_setter_line('value-setter-panel-header', 'Specs', 'Historical Value', 'Set new value'),
               build_value_setter_line('value-setter-panel-usl', 'Upper Specification limit',
                                       state_dict[dd_select]['usl'], ud_usl_input),
               build_value_setter_line('value-setter-panel-lsl', 'Lower Specification limit',
                                       state_dict[dd_select]['lsl'], ud_lsl_input),
               build_value_setter_line('value-setter-panel-ucl', 'Upper Control limit', state_dict[dd_select]['ucl'],
                                       ud_ucl_input),
               build_value_setter_line('value-setter-panel-lcl', 'Lower Control limit', state_dict[dd_select]['lcl'],
                                       ud_lcl_input)
           ], state_value[dd_select]['usl'], state_value[dd_select]['lsl'], state_value[dd_select]['ucl'], \
           state_value[dd_select]['lcl']


# ====== Callbacks to update stored data via click =====
@app.callback(
    output=Output('value-setter-store', 'data'),
    inputs=[
        Input('value-setter-set-btn', 'n_clicks')
    ],
    state=[
        State('metric-select-dropdown', 'value'),
        State('value-setter-store', 'data'),
        State('ud_usl_input', 'value'),
        State('ud_lsl_input', 'value'),
        State('ud_ucl_input', 'value'),
        State('ud_lcl_input', 'value'),
    ]
)
def set_value_setter_store(set_btn, param, data, usl, lsl, ucl, lcl):
    if set_btn is None:
        return data
    else:
        data[param]['usl'] = usl
        data[param]['lsl'] = lsl
        data[param]['ucl'] = ucl
        data[param]['lcl'] = lcl

        # Recalculate ooc in case of param updates
        data[param]['ooc'] = populate_ooc(df[param], ucl, lcl)
        return data


@app.callback(
    output=Output('value-setter-view-output', 'children'),
    inputs=[Input('value-setter-view-btn', 'n_clicks'), Input('metric-select-dropdown', 'value'),
            Input('value-setter-store', 'data')]
)
def show_current_specs(n_clicks, dd_select, store_data):
    if n_clicks > 0:
        curr_col_data = store_data[dd_select]
        new_df_dict = {
            'Specs': ['Upper Specification Limit', 'Lower Specification Limit', 'Upper Control Limit',
                      'Lower Control Limit'],
            'Current Setup': [curr_col_data['usl'], curr_col_data['lsl'], curr_col_data['ucl'], curr_col_data['lcl']]
        }
        new_df = pd.DataFrame.from_dict(new_df_dict)
        return dash_table.DataTable(
            style_header={
                'backgroundColor': '#2d3038',
                'fontWeight': 'bold'
            },
            style_as_list_view=True,
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['Specs']
            ],
            style_cell={'backgroundColor': '#2d3038', 'color': '#95969A', 'border': '#53555B'},
            data=new_df.to_dict('rows'),
            columns=[{'id': c, 'name': c} for c in ['Specs', 'Current Setup']]
        )


def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className='row',
        children=
        [
            html.Div(
                id="card-1",
                className='four columns',
                children=[
                    html.H5("Flight #"),
                    daq.LEDDisplay(
                        value='755',
                        color=theme['secondary'],
                        size=80,
                        theme=theme
                    )
                ]
            ),

            html.Div(
                id='card-2',
                className='four columns',
                children=[
                    html.H5("Overall performance indicator"),
                    daq.Gauge(
                        id='progress-gauge',
                        value=8,
                        showCurrentValue=True,
                        size=150,
                        max=10,
                        min=0,
                        color={"gradient":True,"ranges":{"green":[0,6],"yellow":[6,8],"red":[8,10]}}
                    )
                ]
            ),

            html.Div(
                id='utility-card',
                className='four columns',
                children=[
                    daq.StopButton(id='stop-button', size=160, buttonText='start')
                ]
            )
        ]
    )


def generate_section_banner(title):
    return html.Div(
        className="section-banner",
        children=title,
    )


def build_top_panel():
    return html.Div(
        id='top-section-container',
        className='row',
        style={
            'height': '45vh'
        },
        children=[
            # Metrics summary
            html.Div(
                id='metric-summary-session',
                className='eight columns',
                style={'height': '100%'},
                children=[
                    generate_section_banner('Flight Performance Summary'),
                    generate_metric_list_header(),
                    html.Div(
                        # id='metric_div',
                        style={
                            'height': 'calc(100% - 90px)',
                            'width': '100%',
                            'overflow-x': 'hidden',
                            'overflow-y': 'scroll'
                        },
                        children=[
                            generate_metric_row_helper(1),
                            generate_metric_row_helper(2),
                            generate_metric_row_helper(3),
                            generate_metric_row_helper(4),
                            generate_metric_row_helper(5),
                            generate_metric_row_helper(6),
                            generate_metric_row_helper(7),

                        ]
                    )
                ]
            ),

            # Piechart
            html.Div(
                id='ooc-piechart-outer',
                className='four columns',
                children=[
                    generate_section_banner('% per Parameter'),
                    generate_piechart()
                ]
            )
        ]
    )


def generate_piechart():
    return dcc.Graph(
        id='piechart',
        figure={
            'data': [
                {
                    'labels': params[1:],
                    'values': [1, 1, 1, 1, 1, 1, 1],
                    'type': 'pie',
                    'marker': {'line': {'color': '#53555B', 'width': 2}},
                    'hoverinfo': 'label',
                    'textinfo': 'label'
                }],
            'layout': {
                'showlegend': True,
                'paper_bgcolor': 'rgb(45, 48, 56)',
                'plot_bgcolor': 'rgb(45, 48, 56)'
            }
        }
    )


# Build header
def generate_metric_list_header():
    return generate_metric_row(
        'metric_header',
        {
            'height': '30px',
            'margin': '10px 0px',
            'textAlign': 'center'
        },
        {
            'id': "m_header_1",
            'children': html.Div("Parameter")
        },
        {
            'id': "m_header_2",
            'children': html.Div("Count")
        },
        {
            'id': "m_header_3",
            'children': html.Div("Sparkline")
        },
        {
            'id': "m_header_4",
            'children': html.Div("OOC%")
        },
        {
            'id': "m_header_5",
            'children': html.Div("%OOC")
        },
        {
            'id': "m_header_6",
            'children': "Pass/Fail"
        })


def generate_metric_row_helper(index):
    item = params[index]

    div_id = item + suffix_row
    button_id = item + suffix_button_id
    sparkline_graph_id = item + suffix_sparkline_graph
    count_id = item + suffix_count
    ooc_percentage_id = item + suffix_ooc_n
    ooc_graph_id = item + suffix_ooc_g
    indicator_id = item + suffix_indicator

    return generate_metric_row(
        div_id, None,
        {
            'id': item,
            'children': html.Button(
                id=button_id,
                children=item,
                title="Click to visualize live-chart",
                n_clicks=0
            )
        },
        {
            'id': count_id,
            'children': '0'
        },
        {
            'id': item + '_sparkline',
            'children': dcc.Graph(
                id=sparkline_graph_id,
                style={
                    'width': '100%',
                    'height': '95%',
                },
                config={
                    'staticPlot': False,
                    'editable': False,
                    'displayModeBar': False
                },
                figure=go.Figure({
                    'data': [{'x': [], 'y': [], 'mode': 'lines+markers', 'name': item,
                              'line': {'color': 'rgb(255,209,95)'}}],
                    'layout': {
                        'uirevision': True,
                        'margin': dict(
                            l=0, r=0, t=4, b=4, pad=0
                        ),
                        'paper_bgcolor': 'rgb(45, 48, 56)',
                        'plot_bgcolor': 'rgb(45, 48, 56)'
                    }
                }))
        },
        {
            'id': ooc_percentage_id,
            'children': '0.00%'
        },
        {
            'id': ooc_graph_id + '_container',
            'children':
                daq.GraduatedBar(
                    id=ooc_graph_id,
                    color={"gradient": True, "ranges": {"green": [0, 3], "yellow": [3, 7], "red": [7, 15]}},
                    showCurrentValue=False,
                    max=15,
                    value=0
                )
        },
        {
            'id': item + '_pf',
            'children': daq.Indicator(
                id=indicator_id,
                value=True,
                color=theme['primary']
            )
        }
    )


def generate_metric_row(id, style, col1, col2, col3, col4, col5, col6):
    if style is None:
        style = {
            'height': '100px',
            'width': '100%',
        }
    return html.Div(
        id=id,
        className='row metric-row',
        style=style,
        children=[
            html.Div(
                id=col1['id'],
                style={},
                className='one column',
                children=col1['children']
            ),
            html.Div(
                id=col2['id'],
                style={'textAlign': 'center'},
                className='one column',
                children=col2['children']
            ),
            html.Div(
                id=col3['id'],
                style={
                    'height': '100%',
                },
                className='four columns',
                children=col3['children']
            ),
            html.Div(
                id=col4['id'],
                style={},
                className='one column',
                children=col4['children']
            ),
            html.Div(
                id=col5['id'],
                style={
                    'height': '100%',

                },
                className='three columns',
                children=col5['children']
            ),
            html.Div(
                id=col6['id'],
                style={
                    'display': 'flex',
                    'justifyContent': 'center'
                },
                className='one column',
                children=col6['children']
            )
        ]
    )


def build_chart_panel():
    return html.Div(
        id='control-chart-container',
        className='twelve columns',
        children=[
            generate_section_banner('Live Chart'),

            dcc.Interval(
                id='interval-component',
                interval=2 * 1000,  # in milliseconds
                n_intervals=0,
                disabled=True
            ),

            dcc.Store(
                id='control-chart-state'
            ),
            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure({
                    'data': [{'x': [], 'y': [], 'mode': 'lines+markers', 'name': params[1]}],
                    'layout': {
                        'paper_bgcolor': 'rgb(45, 48, 56)',
                        'plot_bgcolor': 'rgb(45, 48, 56)'
                    }
                }
                )
            )
        ]
    )


def generate_graph(interval, specs_dict, col):
    stats = state_dict[col]
    col_data = stats['data']
    mean = stats['mean']
    ucl = specs_dict[col]['ucl']
    lcl = specs_dict[col]['lcl']
    usl = specs_dict[col]['usl']
    lsl = specs_dict[col]['lsl']

    x_array = state_dict['Batch']['data'].tolist()
    y_array = col_data.tolist()

    total_count = 0

    if interval > max_length:
        total_count = max_length - 1
    elif interval > 0:
        total_count = interval

    ooc_trace = {'x': [],
                 'y': [],
                 'name': 'Out of Control',
                 'mode': 'markers',
                 'marker': dict(color='rgba(210, 77, 87, 0.7)', symbol="square", size=11)
                 }

    for index, data in enumerate(y_array[:total_count]):
        if data >= ucl or data <= lcl:
            ooc_trace['x'].append(index + 1)
            ooc_trace['y'].append(data)

    histo_trace = {
        'x': x_array[:total_count],
        'y': y_array[:total_count],
        'type': 'histogram',
        'orientation': 'h',
        'name': 'Distribution',
        'xaxis': 'x2',
        'yaxis': 'y2',
        'marker': {'color': 'rgb(255,209,95)'}
    }

    fig = {
        'data': [
            {
                'x': x_array[:total_count],
                'y': y_array[:total_count],
                'mode': 'lines+markers',
                'name': col,
                'line': {'color': 'rgb(255,209,95)'}
            },
            ooc_trace,
            histo_trace
        ]
    }

    len_figure = len(fig['data'][0]['x'])

    fig['layout'] = dict(
        hovermode='closest',
        uirevision=col,
        paper_bgcolor='rgb(45, 48, 56)',
        plot_bgcolor='rgb(45, 48, 56)',
        legend={'font': {'color': '#95969A'}},
        font={'color': '#95969A'},
        showlegend=True,
        xaxis={
            'zeroline': False,
            'title': 'Batch_Num',
            'showline': False,
            'domain': [0, 0.8],
            'titlefont': {'color': '#95969A'}
        },
        yaxis={
            'title': col,
            'autorange': True,
            'titlefont': {'color': '#95969A'}
        },
        annotations=[
            {'x': 0.75, 'y': lcl, 'xref': 'paper', 'yref': 'y',
             'text': 'LCL:' + str(round(lcl, 3)),
             'showarrow': False},
            {'x': 0.75, 'y': ucl, 'xref': 'paper', 'yref': 'y',
             'text': 'UCL: ' + str(round(ucl, 3)),
             'showarrow': False},
            {'x': 0.75, 'y': usl, 'xref': 'paper', 'yref': 'y',
             'text': 'USL: ' + str(round(usl, 3)),
             'showarrow': False},
            {'x': 0.75, 'y': lsl, 'xref': 'paper', 'yref': 'y',
             'text': 'LSL: ' + str(round(lsl, 3)),
             'showarrow': False},
            {'x': 0.75, 'y': mean, 'xref': 'paper', 'yref': 'y',
             'text': 'Targeted mean: ' + str(round(mean, 3)),
             'showarrow': False}
        ],
        shapes=[
            {
                'type': 'line',
                'xref': 'x',
                'yref': 'y',
                'x0': 1,
                'y0': usl,
                'x1': len_figure + 1,
                'y1': usl,
                'line': {
                    'color': 'rgb(50, 171, 96)',
                    'width': 1,
                    'dash': 'dashdot'
                }
            },
            {
                'type': 'line',
                'xref': 'x',
                'yref': 'y',
                'x0': 1,
                'y0': lsl,
                'x1': len_figure + 1,
                'y1': lsl,
                'line': {
                    'color': 'rgb(50, 171, 96)',
                    'width': 1,
                    'dash': 'dashdot'
                }
            },
            {
                'type': 'line',
                'xref': 'x',
                'yref': 'y',
                'x0': 1,
                'y0': ucl,
                'x1': len_figure + 1,
                'y1': ucl,
                'line': {
                    'color': 'rgb(255,127,80)',
                    'width': 1,
                    'dash': 'dashdot'
                }
            },
            {
                'type': 'line',
                'xref': 'x',
                'yref': 'y',
                'x0': 1,
                'y0': mean,
                'x1': len_figure + 1,
                'y1': mean,
                'line': {
                    'color': 'rgb(255,127,80)',
                    'width': 2
                }
            },
            {
                'type': 'line',
                'xref': 'x',
                'yref': 'y',
                'x0': 1,
                'y0': lcl,
                'x1': len_figure + 1,
                'y1': lcl,
                'line': {
                    'color': 'rgb(255,127,80)',
                    'width': 1,
                    'dash': 'dashdot'
                }
            }
        ],
        xaxis2={
            'title': 'count',
            'domain': [0.8, 1],  # 70 to 100 % of width
            'titlefont': {'color': '#95969A'}
        },
        yaxis2={
            'anchor': 'free',
            'overlaying': 'y',
            'side': 'right',
            'showticklabels': False,
            'titlefont': {'color': '#95969A'}
        }
    )

    return fig


@app.callback(
    output=[Output('app-tabs', 'value'),
            Output('app-content', 'children'),
            Output('Specs-tab', 'disabled'),
            Output('Control-chart-tab', 'disabled'),
            Output('tab-trigger-btn', 'style')],
    inputs=[Input('tab-trigger-btn', 'n_clicks')]
)
def render_tab_content(tab_switch):
    if tab_switch == 0:
        return 'tab1', build_tab_1(), False, True, {'display': 'inline-block', 'float': 'right'}

    if tab_switch:
        return ['tab2', daq.DarkThemeProvider(theme=theme, children=[
            html.Div(
                id='status-container',
                children=[
                    build_quick_stats_panel(),
                    build_top_panel(),
                    build_chart_panel(),
                ]
            )
        ]), True, False, {'display': 'none'}]


# ======= Callbacks for modal popup =======
@app.callback(Output("markdown", "style"),
              [Input("learn-more-button", "n_clicks"), Input("markdown_close", "n_clicks")])
def update_click_output(button_click, close_click):
    ctx = dash.callback_context

    if ctx.triggered:
        prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if prop_id == "learn-more-button":
            return {"display": "block"}

    return {'display': 'none'}


# Callbacks for stopping interval update
@app.callback(
    [Output('interval-component', 'disabled'),
     Output('stop-button', 'buttonText')],
    [Input('stop-button', 'n_clicks')],
    state=[State('interval-component', 'disabled')]
)
def stop_production(_, current):
    return not current, "stop" if current else "start"


# ======= update progress gauge =========
# @app.callback(
#     output=Output('progress-gauge', 'value'),
#     inputs=[Input('interval-component', 'n_intervals')]
# )
# def update_gauge(interval):
#     if interval < max_length:
#         total_count = interval
#     else:
#         total_count = max_length

#     return int(total_count)


def update_sparkline(interval, param):
    x_array = state_dict['Batch']['data'].tolist()
    y_array = state_dict[param]['data'].tolist()

    if interval == 0:
        x_new = y_new = None

    else:
        if interval >= max_length:
            total_count = max_length
        else:
            total_count = interval
        x_new = x_array[:total_count][-1]
        y_new = y_array[:total_count][-1]

    return dict(x=[[x_new]], y=[[y_new]]), [0]


def update_count(interval, col, data):
    if interval == 0:
        return '0', '0.00%', 0.00001, theme['primary']

    elif interval > 0:

        if interval >= max_length:
            total_count = max_length - 1
        else:
            total_count = interval - 1

        ooc_percentage_f = data[col]['ooc'][total_count] * 100
        ooc_percentage_str = "%.2f" % ooc_percentage_f + '%'

        # Set maximum ooc to 15 for better grad bar display
        if ooc_percentage_f > 15:
            ooc_percentage_f = 15

        if ooc_percentage_f == 0.0:
            ooc_grad_val = 0.00001
        else:
            ooc_grad_val = float(ooc_percentage_f)

        # Set indicator theme according to threshold 5%
        if 0 <= ooc_grad_val <= 5:
            color = theme['primary']
        else:
            color = '#FF0000'

    return str(total_count + 1), ooc_percentage_str, ooc_grad_val, color


# ======= update each row at interval =========
@app.callback(
    output=[
        Output(params[1] + suffix_count, 'children'),
        Output(params[1] + suffix_sparkline_graph, 'extendData'),
        Output(params[1] + suffix_ooc_n, 'children'),
        Output(params[1] + suffix_ooc_g, 'value'),
        Output(params[1] + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param1_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, params[1], stored_data)
    spark_line_data = update_sparkline(interval, params[1])
    return count, spark_line_data, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output(params[2] + suffix_count, 'children'),
        Output(params[2] + suffix_sparkline_graph, 'extendData'),
        Output(params[2] + suffix_ooc_n, 'children'),
        Output(params[2] + suffix_ooc_g, 'value'),
        Output(params[2] + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param2_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, params[2], stored_data)
    spark_line_data = update_sparkline(interval, params[2])
    return count, spark_line_data, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output(params[3] + suffix_count, 'children'),
        Output(params[3] + suffix_sparkline_graph, 'extendData'),
        Output(params[3] + suffix_ooc_n, 'children'),
        Output(params[3] + suffix_ooc_g, 'value'),
        Output(params[3] + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param3_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, params[3], stored_data)
    spark_line_data = update_sparkline(interval, params[3])
    return count, spark_line_data, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output(params[4] + suffix_count, 'children'),
        Output(params[4] + suffix_sparkline_graph, 'extendData'),
        Output(params[4] + suffix_ooc_n, 'children'),
        Output(params[4] + suffix_ooc_g, 'value'),
        Output(params[4] + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param4_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, params[4], stored_data)
    spark_line_data = update_sparkline(interval, params[4])
    return count, spark_line_data, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output(params[5] + suffix_count, 'children'),
        Output(params[5] + suffix_sparkline_graph, 'extendData'),
        Output(params[5] + suffix_ooc_n, 'children'),
        Output(params[5] + suffix_ooc_g, 'value'),
        Output(params[5] + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param5_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, params[5], stored_data)
    spark_line_data = update_sparkline(interval, params[5])
    return count, spark_line_data, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output(params[6] + suffix_count, 'children'),
        Output(params[6] + suffix_sparkline_graph, 'extendData'),
        Output(params[6] + suffix_ooc_n, 'children'),
        Output(params[6] + suffix_ooc_g, 'value'),
        Output(params[6] + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param6_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, params[6], stored_data)
    spark_line_data = update_sparkline(interval, params[6])
    return count, spark_line_data, ooc_n, ooc_g_value, indicator


@app.callback(
    output=[
        Output(params[7] + suffix_count, 'children'),
        Output(params[7] + suffix_sparkline_graph, 'extendData'),
        Output(params[7] + suffix_ooc_n, 'children'),
        Output(params[7] + suffix_ooc_g, 'value'),
        Output(params[7] + suffix_indicator, 'color')
    ],
    inputs=[Input('interval-component', 'n_intervals')],
    state=[State('value-setter-store', 'data')]
)
def update_param7_row(interval, stored_data):
    count, ooc_n, ooc_g_value, indicator = update_count(interval, params[7], stored_data)
    spark_line_data = update_sparkline(interval, params[7])
    return count, spark_line_data, ooc_n, ooc_g_value, indicator


#  ======= button to choose/update figure based on click ============
@app.callback(
    output=Output('control-chart-live', 'figure'),
    inputs=[
        Input('interval-component', 'n_intervals'),
        Input(params[1] + suffix_button_id, 'n_clicks'),
        Input(params[2] + suffix_button_id, 'n_clicks'),
        Input(params[3] + suffix_button_id, 'n_clicks'),
        Input(params[4] + suffix_button_id, 'n_clicks'),
        Input(params[5] + suffix_button_id, 'n_clicks'),
        Input(params[6] + suffix_button_id, 'n_clicks'),
        Input(params[7] + suffix_button_id, 'n_clicks'),
    ],
    state=[State("value-setter-store", 'data'), State('control-chart-live', 'figure')]
)
def update_control_chart(interval, n1, n2, n3, n4, n5, n6, n7, data, cur_fig):
    # Find which one has been triggered
    ctx = dash.callback_context

    if not ctx.triggered:
        return generate_graph(interval, data, params[1])

    if ctx.triggered:
        # Get most recently triggered id and prop_type
        splitted = ctx.triggered[0]['prop_id'].split('.')
        prop_id = splitted[0]
        prop_type = splitted[1]

        if prop_type == 'n_clicks':
            curr_id = cur_fig['data'][0]['name']
            prop_id = prop_id[:-7]
            if curr_id == prop_id:
                return generate_graph(interval, data, curr_id)
            else:
                return generate_graph(interval, data, prop_id)

        if prop_type == 'n_intervals' and cur_fig is not None:
            curr_id = cur_fig['data'][0]['name']
            return generate_graph(interval, data, curr_id)


# Update piechart
@app.callback(
    output=Output('piechart', 'figure'),
    inputs=[
        Input('interval-component', 'n_intervals')],
    state=[State("value-setter-store", 'data')]
)
def update_piechart(interval, stored_data):
    if interval == 0:
        return {'data': [], 'layout': {'font': {'color': '#95969A'},
                                       'paper_bgcolor': 'rgb(45, 48, 56)',
                                       'plot_bgcolor': 'rgb(45, 48, 56)'}}

    if interval >= max_length:
        total_count = max_length - 1
    else:
        total_count = interval - 1

    values = []
    colors = []
    for param in params[1:]:
        ooc_param = (stored_data[param]['ooc'][total_count] * 100) + 1
        values.append(ooc_param)
        if ooc_param > 6:
            colors.append('rgb(206,0,5)')
        else:
            colors.append('rgb(0, 116, 57)')

    new_figure = {
        'data': [
            {
                'labels': params[1:],
                'values': values,
                'type': 'pie',
                'marker': {'colors': colors, 'line': dict(color='#53555B', width=2)},
                'hoverinfo': 'label',
                'textinfo': 'label'
            }],
        'layout': {
            'uirevision': True,
            'font': {'color': '#95969A'},
            'showlegend': True,
            'legend': {'font': {'color': '#95969A'}},
            'paper_bgcolor': 'rgb(45, 48, 56)',
            'plot_bgcolor': 'rgb(45, 48, 56)'
        }
    }
    return new_figure


# Running the server
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
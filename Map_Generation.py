import dash_table
import dash_table.FormatTemplate as FormatTemplate
import dash_core_components as dcc


def make_dcc_country_tab(countryName, dataframe):
    '''This is for generating tab component for country table'''
    return dcc.Tab(label=countryName,
            value=countryName,
            className='custom-tab',
            selected_className='custom-tab--selected',
            children=[dash_table.DataTable(
                    id='datatable-interact-location-{}'.format(countryName),
                    # Don't show coordinates
                    columns=[{"name": i, "id": i, "type": "numeric","format": FormatTemplate.percentage(2)}
                             if i == 'Death rate' else {"name": i, "id": i}
                             for i in dataframe.columns[0:6]],
                    # But still store coordinates in the table for interactivity
                    data=dataframe.to_dict("rows"),
                    row_selectable="single" if countryName != 'Schengen' else False,
                    sort_action="native",
                    style_as_list_view=True,
                    style_cell={'font_family': 'Arial',
                                  'font_size': '1.1rem',
                                  'padding': '.1rem',
                                  'backgroundColor': '#f4f4f2', },
                    fixed_rows={'headers': True, 'data': 0},
                    style_table={'minHeight': '800px',
                                 'height': '800px',
                                 'maxHeight': '800px',
                                 #'overflowX': 'scroll'
                                 },
                    style_header={'backgroundColor': '#f4f4f2',
                                    'fontWeight': 'bold'},
                    style_cell_conditional=[{'if': {'column_id': 'Province/State'}, 'width': '26%'},
                                            {'if': {'column_id': 'Country/Region'}, 'width': '26%'},
                                            {'if': {'column_id': 'Active'}, 'width': '14.2%'},
                                            {'if': {'column_id': 'Confirmed'}, 'width': '15.8%'},
                                            {'if': {'column_id': 'Recovered'}, 'width': '15.8%'},
                                            {'if': {'column_id': 'Deaths'}, 'width': '14.2%'},
                                            {'if': {'column_id': 'Death rate'}, 'width': '14%'},
                                            {'if': {'column_id': 'Active'}, 'color':'#e36209'},
                                            {'if': {'column_id': 'Confirmed'}, 'color': '#d7191c'},
                                            {'if': {'column_id': 'Recovered'}, 'color': '#1a9622'},
                                            {'if': {'column_id': 'Deaths'}, 'color': '#6c6c6c'},
                                            {'textAlign': 'center'}],
                        )
            ]
          )


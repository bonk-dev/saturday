import traceback
from flask import request
from flask_restx import Resource, Namespace, fields

from backend import logger
from backend.models import (
    error_response_fields, axis_config_fields, dataset_config_fields,
    filter_config_fields, dataset_response_fields, query_info_fields,
    schema_response_fields, aggregations_response_fields
)
from backend.routes.queries.dynamicChartHelperFunctions import execute_separate_queries, build_table_structure, \
    generate_random_colors

ns_dynamicChart = Namespace('dynamic-chart', description='Dynamic charting operations')
axis_config_model = ns_dynamicChart.model('AxisConfig', axis_config_fields)
dataset_config_model = ns_dynamicChart.model('DatasetConfig', dataset_config_fields)
filter_config_model = ns_dynamicChart.model('FilterConfig', filter_config_fields)
dataset_response_model = ns_dynamicChart.model('DatasetResponse', dataset_response_fields)
query_info_model = ns_dynamicChart.model('QueryInfo', query_info_fields)
schema_response_model = ns_dynamicChart.model('SchemaResponse', schema_response_fields)
aggregations_response_model = ns_dynamicChart.model('AggregationsResponse', aggregations_response_fields)
error_response_model = ns_dynamicChart.model('ErrorResponse', error_response_fields)

# New models for the enhanced features
having_filter_model = ns_dynamicChart.model('HavingFilter', {
    'field': fields.String(required=True, description='Field name (can be aggregated field alias)'),
    'value': fields.Raw(required=True, description='Filter value'),
    'operator': fields.String(required=False, default='=',
                              description='Comparison operator: =, >, <, >=, <=, !=, IN, NOT NULL, NULL')
})

order_by_model = ns_dynamicChart.model('OrderBy', {
    'field': fields.String(required=True, description='Field name to order by (can be aggregated field alias)'),
    'direction': fields.String(required=False, default='ASC',
                               description='Sort direction: ASC or DESC')
})

# Table structure models
table_header_model = ns_dynamicChart.model('TableHeader', {
    'key': fields.String(required=True, description='Column key/identifier'),
    'label': fields.String(required=True, description='Display label for column'),
    'type': fields.String(required=True, description='Data type: string, number, date'),
})


table_structure_model = ns_dynamicChart.model('TableStructure', {
    'headers': fields.List(fields.Nested(table_header_model), description='Table column headers'),
    'rows': fields.List(fields.Raw, description='Table data rows'),
})

# Nested references have to be here
chart_data_model = ns_dynamicChart.model('ChartData', {
    'labels': fields.List(fields.String, description='Chart labels (x-axis values)'),
    'datasets': fields.List(fields.Nested(dataset_response_model), description='Chart datasets')
})

chart_data_request_model = ns_dynamicChart.model('ChartDataRequest', {
    'x_axis': fields.Nested(axis_config_model, required=True, description='X-axis configuration'),
    'y_axis_datasets': fields.List(fields.Nested(dataset_config_model), required=True,
                                   description='Y-axis datasets configuration'),
    'filters': fields.List(fields.Nested(filter_config_model), required=False,
                           description='Optional filters to apply (WHERE clause)'),
    'having_filters': fields.List(fields.Nested(having_filter_model), required=False,
                                  description='Optional filters for aggregated fields (HAVING clause)'),
    'order_by': fields.List(fields.Nested(order_by_model), required=False,
                            description='Optional custom ordering'),
    'limit': fields.Integer(required=False, description='Maximum number of results to return (0 or null for no limit)'),
    'chart_type': fields.String(required=False, default='line',
                                description='Chart type: line, bar, pie, doughnut, radar'),
    'include_table': fields.Boolean(required=False, default=True,
                                    description='Whether to include table structure in response')
})

chart_data_response_model = ns_dynamicChart.model('ChartDataResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'data': fields.Nested(chart_data_model, description='Chart.js compatible data'),
    'table': fields.Nested(table_structure_model, required=False, description='Tabular representation of data'),
    'chart_type': fields.String(description='Recommended chart type'),
    'query_info': fields.Nested(query_info_model, description='Query execution information')
})


@ns_dynamicChart.route('/data')
class DynamicChartData(Resource):
    @ns_dynamicChart.expect(chart_data_request_model)
    @ns_dynamicChart.response(200, 'Success', chart_data_response_model)
    @ns_dynamicChart.response(400, 'Bad Request', error_response_model)
    @ns_dynamicChart.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Generate dynamic chart data using separate queries for each Y-axis dataset.
        This approach prevents interference between datasets and ensures consistent results
        regardless of how many datasets are added. Now includes table structure for comprehensive data display.
        """
        try:
            data = request.get_json()
            # Extract parameters from payload
            x_axis = data.get('x_axis', {})
            y_axis_datasets = data.get('y_axis_datasets', [])
            filters = data.get('filters', [])
            having_filters = data.get('having_filters', [])
            order_by = data.get('order_by', [])
            limit = data.get('limit', None)
            chart_type = data.get('chart_type', 'bar')
            style_config = data.get('style', {})
            # Validate required fields
            if not x_axis or not y_axis_datasets:
                return {'error': 'x_axis and y_axis_datasets are required', 'success': False}, 400

            # Validate limit
            if limit is not None and limit != 0 and (not isinstance(limit, int) or limit < 0):
                return {'error': 'limit must be a non-negative integer or null for no limit', 'success': False}, 400

            # Execute separate queries
            x_values, dataset_results = execute_separate_queries(
                x_axis, y_axis_datasets, filters, having_filters, order_by, limit
            )

            # Apply custom ordering if specified
            if order_by:
                combined_data = list(zip(x_values, *[ds['data'] for ds in dataset_results]))
                # Apply sorting based on order_by configuration
                for order_item in reversed(order_by):
                    field = order_item['field']
                    direction = order_item.get('direction', 'ASC').upper()
                    reverse = direction == 'DESC'
                    # Find which column to sort by
                    if field == x_axis.get('alias', x_axis['field']):
                        # Sort by x-axis
                        combined_data.sort(key=lambda x: x[0], reverse=reverse)
                    else:
                        for i, ds in enumerate(dataset_results):
                            if ds['name'] == field:
                                combined_data.sort(key=lambda x: x[i + 1], reverse=reverse)
                                break
                # Unzip back to separate arrays
                if combined_data:
                    x_values = [row[0] for row in combined_data]
                    for i, ds in enumerate(dataset_results):
                        ds['data'] = [row[i + 1] for row in combined_data]

            table_structure = build_table_structure(x_values, dataset_results, x_axis)

            # Prepare Chart.js format
            chart_datasets = []
            colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']


            # Check if this is a pie-type chart that needs individual colors per data point
            pie_chart_types = ['pie', 'doughnut', 'radar', 'polararea']
            is_pie_type = chart_type.lower() in pie_chart_types

            for i, dataset_result in enumerate(dataset_results):
                background_color = dataset_result.get('background_color') or colors[i % len(colors)]
                dataset_config = {
                    'label': dataset_result['label'],
                    'data': dataset_result['data'],
                    'backgroundColor': background_color,
                    'borderWidth': 1
                }

                if is_pie_type:
                    # For pie-type charts, generate individual colors for each data point
                    num_data_points = len(dataset_result['data'])
                    individual_colors = generate_random_colors(num_data_points)
                    dataset_config['backgroundColor'] = individual_colors
                    dataset_config['borderColor'] = individual_colors
                else:
                    # For other chart types, use single color per dataset
                    single_color = dataset_config['backgroundColor'] or colors[i % len(colors)]
                    dataset_config['borderColor'] = single_color

                    if chart_type == 'line':
                        dataset_config['fill'] = False

                chart_datasets.append(dataset_config)

            chart_data = {
                'labels': [str(val) for val in x_values],
                'datasets': chart_datasets
            }


            default_style = {
                'backgroundColor': '#ffffff',
                'fontColor': '#333333',
                'legendPosition': 'bottom',
                'titleFontSize': 18,
                'titleFontColor': '#000000',
                'gridColor': '#cccccc'
            }

            final_style = {**default_style, **style_config}

            response = {
                'success': True,
                'data': chart_data,
                'chart_type': chart_type,
                'style': final_style,
                'table': table_structure,
                'query_info': {
                    'total_records': len(x_values),
                    'query': f"Executed {len(y_axis_datasets) + 1} separate queries",
                    'limited': limit is not None and limit > 0,
                    'limit_value': limit if limit is not None and limit > 0 else None
                }
            }
            return response

        except Exception as e:
            logger.info(f'Error in DynamicChartData: {str(e)}')
            traceback.print_exc()
            return {'error': str(e), 'success': False}, 500

# Export endpoint for different formats
@ns_dynamicChart.route('/export/<format>')
class ExportData(Resource):
    @ns_dynamicChart.expect(chart_data_request_model)
    @ns_dynamicChart.response(200, 'Success')
    @ns_dynamicChart.response(400, 'Bad Request', error_response_model)
    @ns_dynamicChart.response(500, 'Internal Server Error', error_response_model)
    def post(self, format):
        """
        Export chart/table data in various formats (csv, json, xlsx).
        Supports the same query parameters as the main data endpoint.
        """
        try:
            if format.lower() not in ['csv', 'json']:
                return {'error': 'Supported formats: csv, json', 'success': False}, 400

            data = request.get_json()
            # Extract parameters from payload
            x_axis = data.get('x_axis', {})
            y_axis_datasets = data.get('y_axis_datasets', [])
            filters = data.get('filters', [])
            having_filters = data.get('having_filters', [])
            order_by = data.get('order_by', [])
            limit = data.get('limit', None)

            # Validate required fields
            if not x_axis or not y_axis_datasets:
                return {'error': 'x_axis and y_axis_datasets are required', 'success': False}, 400

            # Execute queries and build table structure
            x_values, dataset_results = execute_separate_queries(
                x_axis, y_axis_datasets, filters, having_filters, order_by, limit
            )

            # Apply custom ordering if specified
            if order_by:
                combined_data = list(zip(x_values, *[ds['data'] for ds in dataset_results]))
                for order_item in reversed(order_by):
                    field = order_item['field']
                    direction = order_item.get('direction', 'ASC').upper()
                    reverse = direction == 'DESC'
                    if field == x_axis.get('alias', x_axis['field']):
                        combined_data.sort(key=lambda x: x[0], reverse=reverse)
                    else:
                        for i, ds in enumerate(dataset_results):
                            if ds['name'] == field:
                                combined_data.sort(key=lambda x: x[i + 1], reverse=reverse)
                                break
                if combined_data:
                    x_values = [row[0] for row in combined_data]
                    for i, ds in enumerate(dataset_results):
                        ds['data'] = [row[i + 1] for row in combined_data]

            table_structure = build_table_structure(x_values, dataset_results, x_axis)

            # Format data based on requested format
            if format.lower() == 'json':
                return {
                    'success': True,
                    'format': 'json',
                    'data': table_structure,
                }, 200

            elif format.lower() == 'csv':
                # Convert to CSV format
                import io
                import csv

                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=[h['key'] for h in table_structure['headers']])
                writer.writeheader()

                for row in table_structure['rows']:
                    # Remove internal fields that start with underscore
                    clean_row = {k: v for k, v in row.items() if not k.startswith('_')}
                    writer.writerow(clean_row)

                csv_content = output.getvalue()
                output.close()

                return {
                    'success': True,
                    'format': 'csv',
                    'content': csv_content,
                    'headers': [h['label'] for h in table_structure['headers']],
                }, 200


        except Exception as e:
            logger.error(f"Error in ExportData: {str(e)}")
            return {'error': str(e), 'success': False}, 500
from flask_restx import fields

### Api insertion
error_response_fields = {
    'error': fields.String(description='Error message'),
    'success': fields.Boolean(description='Operation success status (always false for errors)')
}

insert_request_fields = {
    'search_query': fields.String(required=True, description='Search query string'),
}

insert_response_fields = {
    'success': fields.Boolean(description='Operation success status'),
    'search_query': fields.String(description='The search query used'),
    'count': fields.Integer(description='Number of results found'),
}

status_response_fields = {
    'status': fields.String(description='Service status'),
    'endpoints': fields.List(fields.String, description='Available endpoints'),
    'environment': fields.Raw(description='Environment configuration status'),
    'configuration': fields.Raw(description='Current app configuration')
}

### Chart

axis_config_fields = {
    'table': fields.String(required=True, description='Database table name'),
    'field': fields.String(required=True, description='Field name from the table'),
    'alias': fields.String(required=False, description='Alias for the field in output')
}

dataset_config_fields = {
    'table': fields.String(required=True, description='Database table name'),
    'field': fields.String(required=False, default='ID', description='Field to aggregate'),
    'method': fields.String(required=False, default='count',
                           description='Aggregation method: count, sum, average, min, max'),
    'name': fields.String(required=True, description='Dataset identifier'),
    'label': fields.String(required=False, description='Display label for the dataset'),
    'color': fields.String(required=False, description='Color code for the dataset (hex)')
}

filter_config_fields = {
    'table': fields.String(required=True, description='Database table name'),
    'field': fields.String(required=True, description='Field name to filter on'),
    'value': fields.Raw(required=True, description='Filter value (string, number, or array)'),
    'operator': fields.String(required=False, default='=',
                             description='Comparison operator: =, >, <, IN, LIKE, !=')
}

dataset_response_fields = {
    'label': fields.String(description='Dataset display label'),
    'data': fields.List(fields.Raw, description='Data points for the dataset'),
    'backgroundColor': fields.String(description='Background color'),
    'borderColor': fields.String(description='Border color'),
    'borderWidth': fields.Integer(description='Border width'),
    'fill': fields.Boolean(description='Whether to fill area under line (line charts)')
}



query_info_fields = {
    'total_records': fields.Integer(description='Number of records returned'),
    'query': fields.String(description='Generated SQL query'),
}

### Chart options

column_info_fields = {
    'name': fields.String(description='Column name'),
    'type': fields.String(description='Column data type')
}

schema_response_fields = {
    'success': fields.Boolean(description='Operation success status'),
    'schema': fields.Raw(description='Database schema information'),
    'available_tables': fields.List(fields.String, description='List of available table names')
}

aggregations_response_fields = {
    'success': fields.Boolean(description='Operation success status'),
    'aggregation_methods': fields.List(fields.String, description='Available aggregation methods'),
    'chart_types': fields.List(fields.String, description='Supported chart types'),
    'filter_operators': fields.List(fields.String, description='Supported filter operators'),
    'examples': fields.Raw(description='Example payloads')
}



### Filter Options
multiselect_values_fields = {
    'success': fields.Boolean(required=True, description='Indicates if the operation was successful'),
    'values': fields.List(fields.String, required=True, description='A list of values')
}

column_request_fields = {
    'table_name': fields.String(required=True, description='Table name'),
}

values_request_fields = {
    'table_name': fields.String(required=True, description='Table name'),
    'column_name': fields.String(required=True, description='Table name'),
}
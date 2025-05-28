from flask import request
from flask_restx import Resource, Namespace

from backend.models import (
    error_response_fields, multiselect_values_fields, column_request_fields,
    values_request_fields
)

from database.dbQueries.execQuery import executeQuery, getTableInfo

# Create namespace
ns_filter_options = Namespace('filter-options', description='Endpoints for combo boxes values')

multiselect_values_model = ns_filter_options.model('AxisConfig', multiselect_values_fields)
error_response_model = ns_filter_options.model('ErrorResponse', error_response_fields)
column_request_model = ns_filter_options.model('ColumnRequest', column_request_fields)
values_request_model = ns_filter_options.model('ValuesRequest', values_request_fields)


@ns_filter_options.route('/tableList')
class TableList(Resource):

    @ns_filter_options.response(200, 'Success', multiselect_values_model)
    @ns_filter_options.response(400, 'Bad Request', error_response_model)
    @ns_filter_options.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Retrieve list of available database tables for filter options.
        Returns hardcoded table names excluding many-to-many relationship tables and system tables.

        :return: Dictionary containing success status and list of table names, with optional HTTP status code.
        """
        try:
            # table_query = "SELECT name FROM sqlite_master WHERE type='table'"
            # rows = executeQuery(table_query)
            # tablesStr = [str(row['name']) for row in rows]
            # return {'success': True, 'values': tablesStr}
            # TODO change hardcoded values without showing n:n and system tables
            return {'success': True, "values": [
                'Affiliation',
                'Article',
                'Author',
                'InsertLog',
                'Keywords',
            ]}

        except Exception as e:
            return {'error': str(e), 'success': False}, 500


@ns_filter_options.route('/columnList')
class ColumnList(Resource):
    @ns_filter_options.expect(column_request_model)
    @ns_filter_options.response(200, 'Success', multiselect_values_model)
    @ns_filter_options.response(400, 'Bad Request', error_response_model)
    @ns_filter_options.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Retrieve list of column names for a specified database table.
        Validates table name input and fetches column information using database metadata queries.

        :return: Dictionary containing success status and list of column names with HTTP status code.
        """
        try:
            data = request.get_json()
            table_name = data.get('table_name', '')

            if not table_name:
                return {'error': 'table_name is required', 'success': False}, 400

            columns = getTableInfo(table_name)
            values = [str(row['name']) for row in columns]

            return {'success': True, 'values': values}, 200

        except Exception as e:
            return {'error': str(e), 'success': False}, 500


@ns_filter_options.route('/uniqueValues')
class ValueList(Resource):
    @ns_filter_options.expect(values_request_model)
    @ns_filter_options.response(200, 'Success', multiselect_values_model)
    @ns_filter_options.response(400, 'Bad Request', error_response_model)
    @ns_filter_options.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Retrieve distinct values from a specified column in a database table.
        Executes SQL DISTINCT query to fetch unique values for filter dropdown options.
        Validates both table name and column name parameters before query execution.

        :return: Dictionary containing success status and list of unique column values with HTTP status code.
        """
        try:
            data = request.get_json()
            table_name = data.get('table_name', '')
            column_name = data.get('column_name', '')

            if not table_name or not column_name:
                return {'error': 'table_name and column_name are required', 'success': False}, 400

            query = f"SELECT DISTINCT {column_name} FROM {table_name};"
            rows = executeQuery(query)
            values = [str(row[0]) for row in rows]

            return {'success': True, 'values': values}, 200

        except Exception as e:
            return {'error': str(e), 'success': False}, 500


@ns_filter_options.route('/methods')
class MethodsList(Resource):
    @ns_filter_options.response(200, 'Success', multiselect_values_model)
    @ns_filter_options.response(400, 'Bad Request', error_response_model)
    @ns_filter_options.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Retrieve list of available aggregation methods for data analysis.
        Returns predefined statistical functions that can be applied to database columns.
        Used for chart generation and data summarization operations.

        :return: Dictionary containing success status and list of aggregation methods with HTTP status code.
        """
        try:
            return {'success': True, 'values': ['count', 'count_distinct', 'sum', 'average', 'min', 'max']}, 200

        except Exception as e:
            return {'error': str(e), 'success': False}, 500


@ns_filter_options.route('/operator')
class OperatorsList(Resource):
    @ns_filter_options.response(200, 'Success', multiselect_values_model)
    @ns_filter_options.response(400, 'Bad Request', error_response_model)
    @ns_filter_options.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        """
        Retrieve list of available SQL comparison operators for filtering data.
        Returns predefined operators used in WHERE clauses for database queries.
        Supports equality, inequality, range, set membership, and pattern matching operations.

        :return: Dictionary containing success status and list of SQL operators with HTTP status code.
        """
        try:
            return {'success': True, 'values': ['=', '>', '<', '!=', 'IN', 'LIKE', 'NOT NULL']}, 200

        except Exception as e:
            return {'error': str(e), 'success': False}, 500

@ns_filter_options.route('/chart-type')
class ChartTypes(Resource):
    @ns_filter_options.response(200, 'Success', multiselect_values_model)
    @ns_filter_options.response(400, 'Bad Request', error_response_model)
    @ns_filter_options.response(500, 'Internal Server Error', error_response_model)
    def post(self):
        try:
            return {'success': True, 'values': ["bar","line","pie","doughnut","radar","polarArea"]}, 200

        except Exception as e:
            return {'error': str(e), 'success': False}, 500
import traceback

from flask import request
from flask_restx import Resource, Namespace, fields


from backend.models import (
    error_response_fields, axis_config_fields, dataset_config_fields,
    filter_config_fields, dataset_response_fields, query_info_fields,
    schema_response_fields, aggregations_response_fields
)
from database.dbQueries.execQuery import executeQuery


def build_where_clause(filters: list) -> tuple[str, list]:
    """
    Build SQL WHERE clause and parameter list from filter configuration.
    Constructs parameterized WHERE conditions based on filter operators to prevent SQL injection.

    :param list filters: List of filter dictionaries containing table, field, value, and operator.
    :return: Tuple containing WHERE clause string and list of parameters.
    :rtype: tuple[str, list]
    """
    where_conditions = []
    params = []

    for filter_item in filters:
        table = filter_item['table']
        field = filter_item['field']
        value = filter_item['value']
        operator = filter_item.get('operator', '=')

        if operator == '>':
            where_conditions.append(f"{table}.{field} > ?")
            params.append(value)
        elif operator == '<':
            where_conditions.append(f"{table}.{field} < ?")
            params.append(value)
        elif operator == 'IN' and isinstance(value, list):
            placeholders = ','.join(['?' for _ in value])
            where_conditions.append(f"{table}.{field} IN ({placeholders})")
            params.extend(value)
        elif operator == 'LIKE':
            where_conditions.append(f"{table}.{field} LIKE ?")
            params.append(f"%{value}%")
        elif operator == '!=':
            where_conditions.append(f"{table}.{field} != ?")
            params.append(value)
        elif operator == 'NOT NULL':
            where_conditions.append(f"{table}.{field} IS NOT NULL")
        else:  # Default equality
            where_conditions.append(f"{table}.{field} = ?")
            params.append(value)

    return ' AND '.join(where_conditions), params


def get_aggregation(method: str, field: str) -> str:
    """
    Generate SQL aggregation function based on method type and field name.
    Maps common aggregation methods to their SQL equivalents with fallback to COUNT.

    :param str method: Aggregation method name (count, sum, average, avg, max, min).
    :param str field: Database field name to apply aggregation to.
    :return: SQL aggregation function string.
    :rtype: str
    """
    if method.lower() == 'count':
        return f"COUNT({field})"
    elif method.lower() == 'count_distinct':
        return f"COUNT(DISTINCT {field})"
    elif method.lower() == 'sum':
        return f"SUM({field})"
    elif method.lower() == 'average' or method.lower() == 'avg':
        return f"AVG({field})"
    elif method.lower() == 'max':
        return f"MAX({field})"
    elif method.lower() == 'min':
        return f"MIN({field})"
    else:
        return f"COUNT({field})"  # Default to count


def determine_joins_v2(tables_used: set, primary_table: str = None) -> list[str]:
    """
    Generate SQL JOIN statements based on table relationships using predefined patterns.
    Uses graph-based approach to determine necessary joins between database tables through many-to-many relationships.

    :param set tables_used: Set of table names that need to be joined.
    :param str primary_table: Primary table to start joins from (defaults to first table if None).
    :return: List of SQL JOIN statements.
    :rtype: list[str]
    """
    joins = []
    tables_set = set(tables_used)

    # If no primary table specified, use the first table
    if not primary_table:
        primary_table = list(tables_used)[0]

    # Remove primary table from tables that need to be joined
    tables_to_join = tables_set - {primary_table}

    # Define the relationship patterns based on primary table
    if primary_table == 'Article':
        patterns = {
            'Author': [
                "LEFT JOIN ArticlexAuthor ON Article.ID = ArticlexAuthor.ArticleID",
                "LEFT JOIN Author ON ArticlexAuthor.AuthorID = Author.ID"
            ],
            'Affiliation': [
                "LEFT JOIN ArticlexAffiliation ON Article.ID = ArticlexAffiliation.ArticleID",
                "LEFT JOIN Affiliation ON ArticlexAffiliation.AffiliationID = Affiliation.ID"
            ],
            'Keywords': [
                "LEFT JOIN ArticlexKeywords ON Article.ID = ArticlexKeywords.ArticleID",
                "LEFT JOIN Keywords ON ArticlexKeywords.KeywordsID = Keywords.ID"
            ]
        }
    elif primary_table == 'Author':
        patterns = {
            'Article': [
                "LEFT JOIN ArticlexAuthor ON Author.ID = ArticlexAuthor.AuthorID",
                "LEFT JOIN Article ON ArticlexAuthor.ArticleID = Article.ID"
            ],
            'Affiliation': [
                "LEFT JOIN ArticlexAuthor ON Author.ID = ArticlexAuthor.AuthorID",
                "LEFT JOIN Article ON ArticlexAuthor.ArticleID = Article.ID",
                "LEFT JOIN ArticlexAffiliation ON Article.ID = ArticlexAffiliation.ArticleID",
                "LEFT JOIN Affiliation ON ArticlexAffiliation.AffiliationID = Affiliation.ID"
            ],
            'Keywords': [
                "LEFT JOIN ArticlexAuthor ON Author.ID = ArticlexAuthor.AuthorID",
                "LEFT JOIN Article ON ArticlexAuthor.ArticleID = Article.ID",
                "LEFT JOIN ArticlexKeywords ON Article.ID = ArticlexKeywords.ArticleID",
                "LEFT JOIN Keywords ON ArticlexKeywords.KeywordsID = Keywords.ID"
            ]
        }
    elif primary_table == 'Affiliation':
        patterns = {
            'Article': [
                "LEFT JOIN ArticlexAffiliation ON Affiliation.ID = ArticlexAffiliation.AffiliationID",
                "LEFT JOIN Article ON ArticlexAffiliation.ArticleID = Article.ID"
            ],
            'Author': [
                "LEFT JOIN ArticlexAffiliation ON Affiliation.ID = ArticlexAffiliation.AffiliationID",
                "LEFT JOIN Article ON ArticlexAffiliation.ArticleID = Article.ID",
                "LEFT JOIN ArticlexAuthor ON Article.ID = ArticlexAuthor.ArticleID",
                "LEFT JOIN Author ON ArticlexAuthor.AuthorID = Author.ID"
            ],
            'Keywords': [
                "LEFT JOIN ArticlexAffiliation ON Affiliation.ID = ArticlexAffiliation.AffiliationID",
                "LEFT JOIN Article ON ArticlexAffiliation.ArticleID = Article.ID",
                "LEFT JOIN ArticlexKeywords ON Article.ID = ArticlexKeywords.ArticleID",
                "LEFT JOIN Keywords ON ArticlexKeywords.KeywordsID = Keywords.ID"
            ]
        }
    elif primary_table == 'Keywords':
        patterns = {
            'Article': [
                "LEFT JOIN ArticlexKeywords ON Keywords.ID = ArticlexKeywords.KeywordsID",
                "LEFT JOIN Article ON ArticlexKeywords.ArticleID = Article.ID"
            ],
            'Author': [
                "LEFT JOIN ArticlexKeywords ON Keywords.ID = ArticlexKeywords.KeywordsID",
                "LEFT JOIN Article ON ArticlexKeywords.ArticleID = Article.ID",
                "LEFT JOIN ArticlexAuthor ON Article.ID = ArticlexAuthor.ArticleID",
                "LEFT JOIN Author ON ArticlexAuthor.AuthorID = Author.ID"
            ],
            'Affiliation': [
                "LEFT JOIN ArticlexKeywords ON Keywords.ID = ArticlexKeywords.KeywordsID",
                "LEFT JOIN Article ON ArticlexKeywords.ArticleID = Article.ID",
                "LEFT JOIN ArticlexAffiliation ON Article.ID = ArticlexAffiliation.ArticleID",
                "LEFT JOIN Affiliation ON ArticlexAffiliation.AffiliationID = Affiliation.ID"
            ]
        }
    else:
        patterns = {}

    # Add joins for each table that needs to be connected
    for table in tables_to_join:
        if table in patterns:
            joins.extend(patterns[table])
        elif table != 'InsertLog':  # Skip InsertLog, handle separately
            # Fallback - shouldn't happen with proper patterns
            pass

    # Add InsertLog joins if needed
    if 'InsertLog' in tables_to_join:
        main_tables_with_insert = ['Article', 'Author', 'Affiliation', 'Keywords']
        if primary_table in main_tables_with_insert:
            joins.append(f"LEFT JOIN InsertLog ON {primary_table}.InsertID = InsertLog.ID")

    # Remove duplicates while preserving order
    seen = set()
    unique_joins = []
    for join in joins:
        if join not in seen:
            seen.add(join)
            unique_joins.append(join)

    return unique_joins


ns_dynamicChart = Namespace('dynamic-chart', description='Dynamic charting operations')

axis_config_model = ns_dynamicChart.model('AxisConfig', axis_config_fields)
dataset_config_model = ns_dynamicChart.model('DatasetConfig', dataset_config_fields)
filter_config_model = ns_dynamicChart.model('FilterConfig', filter_config_fields)
dataset_response_model = ns_dynamicChart.model('DatasetResponse', dataset_response_fields)
query_info_model = ns_dynamicChart.model('QueryInfo', query_info_fields)
schema_response_model = ns_dynamicChart.model('SchemaResponse', schema_response_fields)
aggregations_response_model = ns_dynamicChart.model('AggregationsResponse', aggregations_response_fields)
error_response_model = ns_dynamicChart.model('ErrorResponse', error_response_fields)

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
                          description='Optional filters to apply'),
    'chart_type': fields.String(required=False, default='line',
                               description='Chart type: line, bar, pie, doughnut, radar')
})

chart_data_response_model = ns_dynamicChart.model('ChartDataResponse', {
    'success': fields.Boolean(description='Operation success status'),
    'data': fields.Nested(chart_data_model, description='Chart.js compatible data'),
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
        Generate dynamic chart data by executing SQL queries based on axis and dataset configuration.
        Builds aggregated SQL queries with necessary joins and filters, then formats results for Chart.js compatibility.

        'examples': {
                'simple_count': {
                    'x_axis': {'table': 'Article', 'field': 'PublishDate', 'alias': 'year'},
                    'y_axis_datasets': [
                        {'table': 'Article', 'field': 'ID', 'method': 'count', 'name': 'article_count', 'label': 'Articles Published'}
                    ],
                    'chart_type': 'bar'
                },
                'with_filters': {
                    'x_axis': {'table': 'Affiliation', 'field': 'Country', 'alias': 'country'},
                    'y_axis_datasets': [
                        {'table': 'Author', 'field': 'ID', 'method': 'count', 'name': 'author_count', 'label': 'Authors'}
                    ],
                    'filters': [
                        {'table': 'Affiliation', 'field': 'Country', 'value': ['Poland', 'Germany'], 'operator': 'IN'}
                    ],
                    'chart_type': 'pie'
                }
            }

        :return: JSON response containing Chart.js compatible data structure with labels and datasets.
        :rtype: dict
        :raises: 400 error if x_axis or y_axis_datasets are missing from request.
        :raises: 500 error if SQL query execution fails or other processing errors occur.
        """
        try:
            data = request.get_json()

            # Extract parameters from payload
            x_axis = data.get('x_axis', {})
            y_axis_datasets = data.get('y_axis_datasets', [])
            filters = data.get('filters', [])
            chart_type = data.get('chart_type', 'line')

            # Validate required fields
            if not x_axis or not y_axis_datasets:
                return {'error': 'x_axis and y_axis_datasets are required', 'success': False}, 400

            # Build the main query
            x_table = x_axis['table']
            x_field = x_axis['field']
            x_alias = x_axis.get('alias', x_field)

            # Start building the SELECT clause
            select_fields = [f"{x_table}.{x_field} as {x_alias}"]

            # Add y-axis aggregations
            dataset_info = []
            for dataset in y_axis_datasets:
                y_table = dataset['table']
                y_field = dataset.get('field', 'ID')  # Default to ID for counting
                method = dataset.get('method', 'count')
                name = dataset.get('name', f"{method}_{y_field}")

                aggregation = get_aggregation(method, f"{y_table}.{y_field}")
                select_fields.append(f"{aggregation} as {name}")

                dataset_info.append({
                    'name': name,
                    'label': dataset.get('label', name),
                    'color': dataset.get('color', None)
                })

            # Build FROM clause with JOINs
            tables_used = {x_table}
            for dataset in y_axis_datasets:
                tables_used.add(dataset['table'])

            for filter in filters:
                tables_used.add(filter['table'])


            # Determine necessary joins
            joins = determine_joins_v2(tables_used, x_table)

            # Build WHERE clause
            where_clause = ""
            params = []
            if filters:
                where_clause, params = build_where_clause(filters)
                where_clause = f"WHERE {where_clause}" if where_clause else ""

            # Construct the full query
            query = f"""
            SELECT {', '.join(select_fields)}
            FROM {x_table}
            {' '.join(joins)}
            {where_clause}
            GROUP BY {x_table}.{x_field}
            ORDER BY {x_table}.{x_field}
            """

            print(params)
            # Execute query
            results = executeQuery(query, params)


            # Format data for Chart.js
            labels = []
            datasets = {info['name']: [] for info in dataset_info}

            for row in results:
                labels.append(str(row[x_alias]))
                for info in dataset_info:
                    datasets[info['name']].append(row[info['name']] or 0)

            # Prepare Chart.js format
            chart_datasets = []
            colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']

            for i, info in enumerate(dataset_info):
                dataset_config = {
                    'label': info['label'],
                    'data': datasets[info['name']],
                    'backgroundColor': info['color'] or colors[i % len(colors)],
                    'borderColor': info['color'] or colors[i % len(colors)],
                    'borderWidth': 1
                }

                if chart_type == 'line':
                    dataset_config['fill'] = False

                chart_datasets.append(dataset_config)

            chart_data = {
                'labels': labels,
                'datasets': chart_datasets
            }

            response = {
                'success': True,
                'data': chart_data,
                'chart_type': chart_type,
                'query_info': {
                    'total_records': len(results),
                    'query': query.replace('\n', ' ').strip()
                }
            }

            return response

        except Exception as e:
            return {'error': str(e), 'success': False}, 500
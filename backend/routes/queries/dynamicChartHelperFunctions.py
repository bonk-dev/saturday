from backend import logger
from database.dbQueries.execQuery import executeQuery
import random
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


def build_having_clause(having_filters: list, y_axis_datasets: list, x_axis: dict) -> tuple[str, list]:
    """
    Build SQL HAVING clause and parameter list from having filter configuration.
    Used to filter on aggregated fields after GROUP BY operation.
    :param list having_filters: List of having filter dictionaries containing field, value, and operator.
    :param list y_axis_datasets: List of y-axis dataset configurations for mapping aliases to aggregations.
    :param dict x_axis: X-axis configuration for field mapping.
    :return: Tuple containing HAVING clause string and list of parameters.
    :rtype: tuple[str, list]
    """
    having_conditions = []
    params = []
    # Create mapping of aliases to actual SQL expressions
    field_mapping = {}
    # Add x-axis field mapping
    x_alias = x_axis.get('alias', x_axis['field'])
    field_mapping[x_alias] = f"{x_axis['table']}.{x_axis['field']}"
    # Add y-axis aggregation mappings - build the aggregation expressions here
    for dataset in y_axis_datasets:
        y_table = dataset['table']
        y_field = dataset.get('field', 'ID')
        method = dataset.get('method', 'count')
        name = dataset.get('name', f"{method}_{y_field}")
        # Build the actual aggregation SQL expression - this is the key fix
        aggregation = get_aggregation(method, f"{y_table}.{y_field}")
        field_mapping[name] = aggregation
    for filter_item in having_filters:
        field = filter_item['field']
        value = filter_item['value']
        operator = filter_item.get('operator', '=')
        # Get the actual SQL expression for the field - use the full aggregation, not alias
        sql_field = field_mapping.get(field, field)
        # Convert string values to appropriate types for numeric comparisons
        if operator in ['>', '<', '>=', '<=', '!=', '='] and isinstance(value, str):
            try:
                # Try to convert to int first, then float
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                # Keep as string if conversion fails
                pass
        if operator == '>':
            having_conditions.append(f"{sql_field} > ?")
            params.append(value)
        elif operator == '<':
            having_conditions.append(f"{sql_field} < ?")
            params.append(value)
        elif operator == '>=':
            having_conditions.append(f"{sql_field} >= ?")
            params.append(value)
        elif operator == '<=':
            having_conditions.append(f"{sql_field} <= ?")
            params.append(value)
        elif operator == 'IN' and isinstance(value, list):
            placeholders = ','.join(['?' for _ in value])
            having_conditions.append(f"{sql_field} IN ({placeholders})")
            params.extend(value)
        elif operator == '!=':
            having_conditions.append(f"{sql_field} != ?")
            params.append(value)
        elif operator == 'NOT NULL':
            having_conditions.append(f"{sql_field} IS NOT NULL")
        elif operator == 'NULL':
            having_conditions.append(f"{sql_field} IS NULL")
        else:  # Default equality
            having_conditions.append(f"{sql_field} = ?")
            params.append(value)
    return ' AND '.join(having_conditions), params


def build_order_by_clause(order_by: list, y_axis_datasets: list, x_axis: dict) -> str:
    """
    Build SQL ORDER BY clause from order configuration.
    Supports ordering by both regular fields and aggregated fields.
    :param list order_by: List of order dictionaries containing field and direction.
    :param list y_axis_datasets: List of y-axis dataset configurations for mapping aliases to aggregations.
    :param dict x_axis: X-axis configuration for field mapping.
    :return: ORDER BY clause string.
    :rtype: str
    """
    if not order_by:
        return ""
    order_conditions = []
    # Create mapping of aliases to actual SQL expressions
    field_mapping = {}
    # Add x-axis field mapping
    x_alias = x_axis.get('alias', x_axis['field'])
    field_mapping[x_alias] = f"{x_axis['table']}.{x_axis['field']}"
    # Add y-axis aggregation mappings - build the aggregation expressions here
    for dataset in y_axis_datasets:
        y_table = dataset['table']
        y_field = dataset.get('field', 'ID')
        method = dataset.get('method', 'count')
        name = dataset.get('name', f"{method}_{y_field}")
        # Build the actual aggregation SQL expression
        aggregation = get_aggregation(method, f"{y_table}.{y_field}")
        field_mapping[name] = aggregation
    for order_item in order_by:
        field = order_item['field']
        direction = order_item.get('direction', 'ASC').upper()
        # Validate direction
        if direction not in ['ASC', 'DESC']:
            direction = 'ASC'
        # Get the actual SQL expression for the field
        sql_field = field_mapping.get(field, field)
        order_conditions.append(f"{sql_field} {direction}")
    return f"ORDER BY {', '.join(order_conditions)}"


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
            ],
            'InsertLog': [
                "LEFT JOIN InsertLog ON Article.InsertID = InsertLog.ID"
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
            ],
            'InsertLog': [
                "LEFT JOIN InsertLog ON Author.InsertID = InsertLog.ID"
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
            ],
            'InsertLog': [
                "LEFT JOIN InsertLog ON Affiliation.InsertID = InsertLog.ID"
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
            ],
            'InsertLog': [
                "LEFT JOIN InsertLog ON Keywords.InsertID = InsertLog.ID"
            ]
        }
    elif primary_table == 'InsertLog':
        # NEW: Handle InsertLog as primary table
        patterns = {
            'Article': [
                "LEFT JOIN Article ON InsertLog.ID = Article.InsertID"
            ],
            'Author': [
                "LEFT JOIN Author ON InsertLog.ID = Author.InsertID"
            ],
            'Affiliation': [
                "LEFT JOIN Affiliation ON InsertLog.ID = Affiliation.InsertID"
            ],
            'Keywords': [
                "LEFT JOIN Keywords ON InsertLog.ID = Keywords.InsertID"
            ]
        }
    else:
        patterns = {}
    # Add joins for each table that needs to be connected
    for table in tables_to_join:
        if table in patterns:
            joins.extend(patterns[table])

    # Remove duplicates while preserving order
    seen = set()
    unique_joins = []
    for join in joins:
        if join not in seen:
            seen.add(join)
            unique_joins.append(join)
    return unique_joins


def execute_separate_queries(x_axis, y_axis_datasets, filters, having_filters, order_by, limit):
    """
    Execute separate queries for each Y-axis dataset to avoid JOIN interference.
    This ensures that adding additional datasets doesn't affect existing ones.
    """
    x_table = x_axis['table']
    x_field = x_axis['field']
    x_alias = x_axis.get('alias', x_field)
    # Step 1: Get all unique X-axis values first
    x_values_query = f"""
    SELECT DISTINCT {x_table}.{x_field} as {x_alias}
    FROM {x_table}
    """
    # Add WHERE clause for X-axis filters only
    x_filters = [f for f in filters if f['table'] == x_table]
    where_clause = ""
    where_params = []
    if x_filters:
        where_clause, where_params = build_where_clause(x_filters)
        x_values_query += f" WHERE {where_clause}"
    x_values_query += f" ORDER BY {x_table}.{x_field}"
    # Apply limit to X-axis values if specified
    if limit is not None and limit > 0:
        x_values_query += f" LIMIT {limit}"
    logger.info(x_values_query)
    x_results = executeQuery(x_values_query, where_params)
    x_values = [row[x_alias] for row in x_results]
    # Step 2: Execute separate query for each Y-axis dataset
    dataset_results = []
    for dataset in y_axis_datasets:
        y_table = dataset['table']
        y_field = dataset.get('field', 'ID')
        method = dataset.get('method', 'count')
        name = dataset.get('name', f"{method}_{y_field}")
        # Build tables needed for this specific dataset
        tables_used = {x_table, y_table}
        # Add tables from filters that are relevant to this dataset
        relevant_filters = []
        for filter_item in filters:
            filter_table = filter_item['table']
            # Include filter if it's for x_table, y_table, or a connecting table
            if filter_table in [x_table, y_table] or is_connecting_table(filter_table, x_table, y_table):
                tables_used.add(filter_table)
                relevant_filters.append(filter_item)
        # Determine JOINs for this specific dataset
        joins = determine_joins_v2(tables_used, x_table)
        # Build aggregation
        aggregation = get_aggregation(method, f"{y_table}.{y_field}")
        # Build the query for this dataset
        dataset_query = f"""
        SELECT {x_table}.{x_field} as {x_alias}, {aggregation} as {name}
        FROM {x_table}
        {' '.join(joins)}
        """
        # Add WHERE clause for relevant filters
        dataset_params = []
        if relevant_filters:
            where_clause, dataset_params = build_where_clause(relevant_filters)
            dataset_query += f" WHERE {where_clause}"
        dataset_query += f" GROUP BY {x_table}.{x_field}"
        # Add HAVING clause if applicable to this dataset
        applicable_having_filters = [hf for hf in having_filters if hf['field'] == name]
        if applicable_having_filters:
            having_clause, having_params = build_having_clause(applicable_having_filters, [dataset], x_axis)
            dataset_query += f" HAVING {having_clause}"
            dataset_params.extend(having_params)
        # Add ORDER BY
        dataset_query += f" ORDER BY {x_table}.{x_field}"
        logger.info(f"Dataset {name} query: {dataset_query}, {dataset_params}")
        # Execute query for this dataset
        dataset_data = executeQuery(dataset_query, dataset_params)
        # Convert to dictionary for easy lookup
        data_dict = {row[x_alias]: row[name] for row in dataset_data}
        # Fill in data for all x_values (including zeros for missing values)
        dataset_values = []
        for x_val in x_values:
            dataset_values.append(data_dict.get(x_val, 0))
        dataset_results.append({
            'name': name,
            'label': dataset.get('label', name),
            'background_color': dataset.get('background_color', None),
            'data': dataset_values
        })
    return x_values, dataset_results

def is_connecting_table(table):
    """
    Check if a table is a connecting/junction table between x_table and y_table.
    This helps determine which filters are relevant for each dataset query.
    """
    connecting_tables = {
        'ArticlexAuthor', 'ArticlexAffiliation', 'ArticlexKeywords'
    }
    return table in connecting_tables
def build_table_structure(x_values, dataset_results, x_axis):
    """
    Build a structured table representation of the chart data.
    Creates headers, rows, and summary statistics for tabular display.

    :param list x_values: X-axis values (labels)
    :param list dataset_results: Y-axis dataset results
    :param dict x_axis: X-axis configuration
    :return: Dictionary containing table structure
    :rtype: dict
    """
    x_alias = x_axis.get('alias', x_axis['field'])

    # Build table headers
    headers = [
        {
            'key': x_alias,
            'label': x_axis.get('label', x_alias),
        }
    ]

    # Add dataset headers
    for dataset in dataset_results:
        headers.append({
            'key': dataset['name'],
            'label': dataset['label'],
        })

    # Build table rows
    rows = []
    for i, x_val in enumerate(x_values):
        row = {x_alias: x_val}

        for dataset in dataset_results:
            value = dataset['data'][i]
            row[dataset['name']] = value

        row['_row_index'] = i
        rows.append(row)

    return {
        'headers': headers,
        'rows': rows,
    }

def generate_random_colors(count):
    """
    Generate a list of random colors for chart data points.
    Uses a mix of predefined colors and randomly generated ones.

    :param int count: Number of colors to generate
    :return: List of color strings in hex format
    :rtype: list[str]
    """
    # Base color palette
    base_colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3',
        '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43', '#EE5A24', '#0DD3F8',
        '#C44569', '#F8B500', '#3742FA', '#2F3542', '#FF3838', '#FF9500'
    ]

    colors = []

    # Use base colors first
    for i in range(min(count, len(base_colors))):
        colors.append(base_colors[i])

    # Generate additional random colors if needed
    for i in range(count - len(base_colors)):
        # Generate random RGB values with good saturation and brightness
        r = random.randint(100, 255)
        g = random.randint(100, 255)
        b = random.randint(100, 255)
        colors.append(f'#{r:02x}{g:02x}{b:02x}')

    return colors



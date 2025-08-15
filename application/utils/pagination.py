from flask import request, jsonify # Import request to read URL query parameters and jsonify to send JSON responses

# Function to paginate a SQLAlchemy query result and return JSON data
def paginate_query(query, schema, default_per_page=10):
    """
    Paginate a SQLAlchemy query.

    Args:
        query: SQLAlchemy query object.
        schema: Marshmallow schema to convert results to JSON.
        default_per_page: Number of items per page, default is 10.

    Returns:
        JSON response with paginated data and info about pages.
    """

    # Get 'page' from URL query parameters, default to 1, convert to int
    page = request.args.get('page', 1, type=int)

    # Get 'per_page' from URL query parameters, default to default_per_page, convert to int
    per_page = request.args.get('per_page', default_per_page, type=int)

    # Run the paginate method on the query with page and per_page; don't throw error if page is out of range
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    # Return a JSON response with:
    # - the serialized items for the current page
    # - total number of items in the whole query
    # - total number of pages
    # - the current page number
    return jsonify({
        "items": schema.dump(paginated.items, many=True),
        "total": paginated.total,
        "pages": paginated.pages,
        "current_page": paginated.page
    })

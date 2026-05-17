def paginate(query, page=1, limit=10):
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed), default 1
        limit: Items per page, default 10
    
    Returns:
        dict with items, total, pages, current_page
    """
    # Validate inputs
    page = max(1, int(page)) if page else 1
    limit = max(1, min(100, int(limit))) if limit else 10  # Cap at 100
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = (total + limit - 1) // limit
    
    # Get paginated items
    items = query.offset((page - 1) * limit).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }

'''
Issues Resolved:
No input validation — doesn't check if page or limit are valid
No metadata — only returns data, not total count or pages info
No error handling — crashes on invalid input
Returns raw list — better to return a structured response
'''
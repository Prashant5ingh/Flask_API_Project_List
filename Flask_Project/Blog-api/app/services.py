from .models import Blog
from . import db
from .cache import get_cache, set_cache, delete_cache

CACHE_KEY = "blogs_page_{}"


def create_blog(data):
    blog = Blog(
        title=data["title"],
        content=data["content"]
    )
    db.session.add(blog)
    db.session.commit()

    # invalidate cache
    delete_cache("blogs_page_1")

    return blog


def get_blogs(page, per_page=5): # Default to 5 blogs per page

    cache_key = CACHE_KEY.format(page)

    cached = get_cache(cache_key)
    if cached:
        return cached

    pagination = Blog.query.order_by(
        Blog.created_at.desc()
    ).paginate(page=page, per_page=per_page)

    result = [blog.to_dict() for blog in pagination.items]

    set_cache(cache_key, result)

    return result


def get_blog(blog_id):
    return Blog.query.get(blog_id)


def update_blog(blog, data):
    blog.title = data.get("title", blog.title)
    blog.content = data.get("content", blog.content)

    db.session.commit()

    delete_cache("blogs_page_1")

    return blog


def delete_blog(blog):
    db.session.delete(blog)
    db.session.commit()

    delete_cache("blogs_page_1")
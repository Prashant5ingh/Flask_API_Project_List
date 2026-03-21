from flask import Blueprint, request, jsonify
from .services import (
    create_blog,
    get_blogs,
    get_blog,
    update_blog,
    delete_blog
)

blog_bp = Blueprint("blogs", __name__)


# CREATE
@blog_bp.route("/blogs", methods=["POST"])
def create():
    data = request.json
    blog = create_blog(data)
    return jsonify(blog.to_dict()), 201


# READ ALL (Pagination + Cache)
@blog_bp.route("/blogs", methods=["GET"])
def get_all():
    page = request.args.get("page", 1, type=int)

    blogs = get_blogs(page)

    return jsonify(blogs)


# READ ONE
@blog_bp.route("/blogs/<int:blog_id>", methods=["GET"])
def get_one(blog_id):
    blog = get_blog(blog_id)

    if not blog:
        return {"error": "Not found"}, 404

    return jsonify(blog.to_dict())


# UPDATE
@blog_bp.route("/blogs/<int:blog_id>", methods=["PUT"])
def update(blog_id):
    blog = get_blog(blog_id)

    if not blog:
        return {"error": "Not found"}, 404

    updated = update_blog(blog, request.json)

    return jsonify(updated.to_dict())


# DELETE
@blog_bp.route("/blogs/<int:blog_id>", methods=["DELETE"])
def delete(blog_id):
    blog = get_blog(blog_id)

    if not blog:
        return {"error": "Not found"}, 404

    delete_blog(blog)

    return {"message": "Deleted"}
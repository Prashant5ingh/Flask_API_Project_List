from flask import Blueprint, request, jsonify
from app.models.task import Task
from app.models.project import Project
from app.models.comment import Comment
from app import db, limiter
from app.utils.pagination import paginate
from app.utils.permissions import is_owner, is_admin, can_access, can_delete
from app.utils.cache import get_cache, set_cache, delete_cache
from app.utils.jwt import jwt_required
from app.services.org_members_service import get_user_role

comments_bp = Blueprint("comments", __name__)

@comments_bp.route("/tasks/<int:task_id>/comments", methods=["POST"])
@jwt_required
def add_comment(task_id):
    """Add a comment to a task."""
    data = request.json or {}
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "Content is required"}), 400

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    # Later we can check or add code for role based comments (owner/admin can comment, or only assigned users can comment etc.) For now, we will allow any user with access to the project to comment on the task.
    try:
        comment = Comment(
            content=data["content"],
            task_id=task_id,
            # user_id=2# Assuming we have user_id from JWT token
            user_id=request.user_id # Assuming we have user_id from JWT token

        )
        db.session.add(comment)
        db.session.commit()

        delete_cache(f"user_tasks:{request.user_id}")
        delete_cache(f"task_comments:{task_id}")  # Invalidate cache for comments of this task to ensure the new comment is included in future fetches. 

        return jsonify({
            "message": "Comment added successfully",
            "comment": comment.to_dict()
            # "comment": {
            #     "id": comment.id,
            #     "content": comment.content,
            #     "user_id": comment.user_id,
            #     "created_at": comment.created_at.isoformat(),
            #     "task_id": comment.task_id
            # }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add comment: {str(e)}"}), 500

@comments_bp.route("/tasks/<int:task_id>/comments", methods=["GET"])
@jwt_required
def get_comments(task_id):
    """Get comments for a task with pagination."""

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    commented_task = Comment.query.filter_by(task_id=task_id, user_id=request.user_id).first()
    if not commented_task:
        return jsonify({"error": "Commented task not found for the specified user"}), 404

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)

    cache_key = f"task_comments:{task_id}:{page}:{limit}"
    cached = get_cache(cache_key)

    if cached:
        return jsonify(cached)

    try:
        query = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.desc())
        result = paginate(query, page, limit)

        result["items"] = [c.to_dict() for c in result["items"]]

        set_cache(cache_key, result, expiry=300)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch comments: {str(e)}"}), 400
    
@comments_bp.route("/tasks/comments", methods=["GET"])
@jwt_required
@limiter.limit("5 per minute")  # 👈 prevent brute force attacks on this api endpoint
def get_user_comments():
    """Get comments made by the user with pagination."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)

    cache_key = f"user_comments:{request.user_id}:{page}:{limit}"
    cached = get_cache(cache_key)

    if cached:
        return jsonify(cached)

    try:
        query = Comment.query.filter_by(user_id=request.user_id).order_by(Comment.created_at.desc())
        result = paginate(query, page, limit)

        result["items"] = [c.to_dict() for c in result["items"]]

        set_cache(cache_key, result, expiry=300)

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch user comments: {str(e)}"}), 400

@comments_bp.route("/tasks/comments/<int:comment_id>", methods=["GET"])
@jwt_required
def get_comment(comment_id):
    """GET a single comment by user."""
    cache_key = f"comment:{comment_id}"
    cached = get_cache(cache_key)

    if cached:
        return jsonify(cached)

    comment = Comment.query.filter_by(id=comment_id, user_id=request.user_id).first()

    if not comment:
        return jsonify({"error": "Comment not found for the user"}), 404

    data = comment.to_dict()
    set_cache(cache_key, data, expiry=300)

    return jsonify(data)

@comments_bp.route("/tasks/comments/<int:comment_id>", methods=["PATCH"])
@jwt_required
def update_comment(comment_id):
    """Update a comment by owner."""

    # Owner check is done in the query itself to ensure only the owner can update their comment. This prevents unauthorized access and updates to comments that do not belong to the user.
    comment = Comment.query.filter_by(id=comment_id, user_id=request.user_id).first()

    if not comment:
        return jsonify({"error": "Comment not found for the user"}), 404
    
    # user_role = None  # TODO: Fetch user role from database or JWT token if needed for admin override in permissions check. This will allow admins to update comments that do not belong to them if we implement that functionality in the future.
    
    # Check if the user has permission to update the comment (either owner or admin)
    # if not can_access(request.user_id, comment.user_id, user_role=user_role):
    #     return jsonify({"error": "Unauthorized"}), 403
    
    # Safely parse JSON with error handling
    try:
        data = request.get_json(force=False, silent=False) or {}
    except Exception as e:
        return jsonify({"error": "Invalid JSON format"}), 400
    if not data:
        return jsonify({"error": "No data provided for update"}), 400
    
    
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"error": "Content is required"}), 400
    
    task_id = comment.task_id  # Get the task_id before updating the comment, as we will need it to invalidate the cache after the update.
    
    try:
        comment.content = content
        db.session.commit()

        delete_cache(f"comment:{comment_id}")
        delete_cache(f"user_comments:{request.user_id}")
        delete_cache(f"task_comments:{task_id}:*")
        return jsonify({
            "message": "Comment updated successfully",
            "comment": comment.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback() # Rollback the session in case of an error to prevent partial updates
        return jsonify({"error": f"Failed to update comment: {str(e)}"}), 500
    

@comments_bp.route("/tasks/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required
def delete_comment(comment_id):
    """Delete a comment by owner or admin or access given to delete."""
    # comment = Comment.query.get(comment_id) # Due to permission checks.
    comment = Comment.query.filter_by(id=comment_id, user_id=request.user_id).first() # delete comments belongs to logged in user only.
    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    
    # Deletion method same as other routes using org_member service.
    # if request.user_id != org.owner_id and not is_org_admin(request.user_id, org_id):
    #     return jsonify({"error": "Forbidden: Only organization owner or admins can remove members"}), 403
    
    # Get task and project to find organization
    task = Task.query.get(comment.task_id) # We need to get the task to find the project and organization to check the user's role in that organization for permissions. 
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    project = Project.query.get(task.project_id) # We need to get the project to find the organization to check the user's role in that organization for permissions.
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    # Fetch user role from organization membership service
    user_role = get_user_role(request.user_id, project.organization_id)
    
    # Check if user can delete (owner OR admin). Using RBAC utility function to check if the user has permission to delete the comment based on ownership or admin role in the organization.
    if not can_delete(request.user_id, comment.user_id, user_role=user_role.value if user_role else None):
        return jsonify({"error": "Unauthorized - only owner or admin can delete"}), 403

    task_id = comment.task_id  # Get the task_id before deleting the comment, as we will need it to invalidate the cache after the deletion.
    try:
        db.session.delete(comment)
        db.session.commit()

        delete_cache(f"comment:{comment_id}")
        delete_cache(f"user_comments:{request.user_id}")
        delete_cache(f"task_comments:{task_id}:*")
        return jsonify({"message": "Comment deleted successfully"}), 200
    except Exception as e:
        db.session.rollback() # Rollback the session in case of an error to prevent partial deletions
        return jsonify({"error": f"Failed to delete comment: {str(e)}"}), 500   

from flask import Blueprint, request, jsonify
from app.services.task_service import create_task, update_task, delete_task
from app.models.task import Task
from app.utils.jwt import jwt_required
from app.utils.pagination import paginate
from app.utils.cache import get_cache, set_cache, delete_cache

task_bp = Blueprint("tasks", __name__)

@task_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Task API is healthy and pls navigate to api/auth/register or api/auth/login. Readme File --> https://github.com/Prashant5ingh/Flask_API_Project_List/blob/main/Flask_Project/saas-taskflow-api/Readme.md"}), 200
@task_bp.route("", methods=["POST"])
@jwt_required
def create():
    """Create a new task."""
    data = request.json or {}
    
    task, error = create_task(data, request.user_id)
    
    if error:
        return jsonify({"error": error}), 400
    
    delete_cache(f"user_tasks:{request.user_id}:*")  # Invalidate cache for user's tasks to reflect new task creation. Cache key should match the one used in get_tasks() for user. will this work ? Yes, as long as the cache key in get_tasks() for user tasks is formatted as "user_tasks:{user_id}:{page}:{limit}",
    delete_cache(f"project_tasks:{task.project_id}:*")  # Invalidate cache for project's tasks to reflect new task creation. Cache key should match the one used in get_tasks() for project. will this work ? Yes, as long as the cache key in get_tasks() for project tasks is formatted as "project_tasks:{project_id}:{page}:{limit}", 
    # invalidating "project_tasks:{task.project_id}" will ensure that any cached pages of tasks for that project are cleared, forcing a fresh fetch from the database on the next request. This is a common approach to cache invalidation when related data changes.
    return jsonify({
        "message": "Task created",
        "task": task.to_dict()
    }), 201

@task_bp.route("/", methods=["GET"])
@jwt_required
def get_tasks():
    """Get user's tasks with pagination."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int) # Default to 5 tasks per page for better UX and performance. Can be adjusted as needed.
    
    # Cache key includes user_id for security
    cache_key = f"user_tasks:{request.user_id}:{page}:{limit}"
    cached = get_cache(cache_key)
    
    if cached:
        return jsonify(cached)
    
    try:
        # Filter tasks by current user only
        query = Task.query.filter_by(created_by=request.user_id)
        if query.count() == 0:
            return jsonify({"msg": "No tasks found for user"}), 200
        result = paginate(query, page, limit)
        
        # Serialize data
        result["items"] = [t.to_dict() for t in result["items"]]
        
        set_cache(cache_key, result, expiry=300)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch tasks: {str(e)}"}), 400

@task_bp.route("/<int:task_id>", methods=["GET"])
@jwt_required
def get_task(task_id):
    """Get a single task."""
    cache_key = f"task:{task_id}"
    cached = get_cache(cache_key)
    
    if cached:
        return jsonify(cached)
    
    task = Task.query.filter_by(id=task_id, created_by=request.user_id).first()
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    data = task.to_dict()
    set_cache(cache_key, data, expiry=300)
    
    return jsonify(data)

@task_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required
def update(task_id):
    """Update a task."""
    task, error = update_task(task_id, request.json or {}, request.user_id)
    
    if error:
        return jsonify({"error": error}), 400 if error == "Task not found" else 403
    
    return jsonify({
        "message": "Task updated",
        "task": task.to_dict()
    })

@task_bp.route("/<int:task_id>", methods=["DELETE"])
@jwt_required
def delete(task_id):
    """Delete a task."""
    success, error = delete_task(task_id, request.user_id)
    
    if not success:
        return jsonify({"error": error}), 404 if error == "Task not found" else 403
    
    return jsonify({"message": "Task deleted"}), 200


    
'''
Problems:
Security issue in get_tasks() — Shows all users' tasks, not just current user's
Cache key doesn't include user_id
Query filters aren't set
Cache pollution — All users share same cache (page:limit)
Pagination mismatch — Your improved paginate() returns dict with items/total/page/limit, but code treats it as list
No error handling — create_task() might fail silently
Limited response — Only returns id and title
Missing routes — No GET single task, UPDATE, DELETE

Key improvements:
✅ Security: Filters tasks by created_by, user can only see their own tasks
✅ Cache isolation: Cache key includes user_id
✅ Proper pagination: Handles dict result from paginate()
✅ Error handling: Catches errors from services
✅ Full CRUD: All four operations (Create, Read, Update, Delete)
✅ Proper HTTP codes: 201 for created, 404 for not found, 403 for unauthorized
✅ Full data: Returns complete task objects, not just ID/title
✅ Uses jsonify(): Consistent JSON responses
'''
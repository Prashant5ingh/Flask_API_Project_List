from asyncio import Task

from flask import Blueprint, request, jsonify
from app.models.project import Project
from app.models.organization import Organization
from app import db
from app.utils.jwt import jwt_required
from app.utils.pagination import paginate
from app.utils.cache import get_cache, set_cache, delete_cache

project_bp = Blueprint("projects", __name__)

@project_bp.route("", methods=["POST"])
@jwt_required
def create_project():
    """Create a new project."""
    data = request.json or {}
    
    # Validate input
    if not data.get("name"):
        return jsonify({"error": "Project name required"}), 400
    
    if not data.get("organization_id"):
        return jsonify({"error": "Organization ID required"}), 400
    
    # TODO: Check if user owns organization
    org = Organization.query.filter_by(id=data["organization_id"], owner_id=request.user_id).first() # Ensure user can only create projects in their own organizations 
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    if not org:
        return jsonify({"error": "User does not own the specified organization or company"}), 403 
    
    try:
        project = Project(
            name=data["name"],
            # description=data.get("description", ""),
            organization_id=data["organization_id"],
            created_by=request.user_id
        )
        db.session.add(project)
        #db.session.flush()  # assigns defaults like created_at and id
        
        # Try serializing before commit. Need flush() to work with this line. Also isformat() works fine with flush().
        # project_data = project.to_dict() 

        # If serialization succeeds, then commit
        db.session.commit()

        delete_cache(f"org_projects:{data['organization_id']}") # Clear organization's project list cache to reflect new project creation
        delete_cache(f"user_projects:{request.user_id}:*") # Clear user's project list cache to reflect new project creation. Cache key should match the one used in get
        return jsonify({
            "message": "Project created",
            "project": project.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create project: {str(e)}"}), 400

@project_bp.route("/", methods=["GET"])
@jwt_required
def get_projects(): # all projects for user with pagination
    """Get user's projects with pagination."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int) # Default to 5 tasks per page for better UX and performance. Can be adjusted as needed.
    
    # Cache key includes user_id for security
    cache_key = f"user_projects:{request.user_id}:{page}:{limit}"
    cached = get_cache(cache_key)
    
    if cached:
        return jsonify(cached)
    
    try:
        # Filter projects by current user only
        query = Project.query.filter_by(created_by=request.user_id)
        result = paginate(query, page, limit)
        
        # Serialize data
        result["items"] = [t.to_dict() for t in result["items"]]
        
        set_cache(cache_key, result, expiry=300)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Failed to fetch projects: {str(e)}"}), 400

@project_bp.route("/<int:project_id>", methods=["GET"])
@jwt_required
def get_project(project_id):
    """Get project details."""
    cache_key = f"project:{project_id}"
    
    # Check cache first
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached)
    
    project = Project.query.filter_by(id=project_id, created_by=request.user_id).first() # Ensure user can only access their own projects
    
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    # TODO: Verify user has access to project
    
    data = project.to_dict()
    set_cache(cache_key, data, expiry=300)
    return jsonify(data)

@project_bp.route("/<int:project_id>", methods=["PUT"])
@jwt_required
def update_project(project_id):
    """Update project."""
    project = Project.query.filter_by(id=project_id, created_by=request.user_id).first() # Ensure user can only update their own projects

    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    if project.created_by != request.user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json or {}
    
    try:
        if "name" in data:
            project.name = data["name"]
        if "description" in data:
            project.description = data["description"]
        
        db.session.commit()
        delete_cache(f"project:{project_id}")
        
        return jsonify({
            "message": "Project updated",
            "project": project.to_dict()
        })
    except Exception as e:
        db.session.rollback() # Rollback on error to prevent partial updates
        return jsonify({"error": f"Failed to update project: {str(e)}"}), 400

@project_bp.route("/<int:project_id>", methods=["DELETE"])
@jwt_required
def delete_project(project_id):
    """Delete project."""
    project = Project.query.filter_by(id=project_id, created_by=request.user_id).first() # Ensure user can only delete their own projects

    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    if project.created_by != request.user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        db.session.delete(project)
        db.session.commit()
        delete_cache(f"project:{project_id}")
        
        return jsonify({"message": "Project deleted along with its dependent tasks"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete project: {str(e)}"}), 400


'''
Problems:
No input validation — doesn't check if fields exist
KeyError risk — crashes if name or organization_id missing
No authorization check — user can create projects for any organization
No error handling — database errors will crash
Limited response — only returns id, not full project data
No HTTP status code — should return 201 for created resource
Incomplete — missing GET, UPDATE, DELETE routes

Key improvements:
✅ Input validation with error messages
✅ Authorization checks (user owns project)
✅ Proper HTTP status codes (201, 403, 404)
✅ Error handling with try/except
✅ Full CRUD operations
✅ Caching support
✅ Returns full project object, not just ID
✅ Uses jsonify() consistently
'''
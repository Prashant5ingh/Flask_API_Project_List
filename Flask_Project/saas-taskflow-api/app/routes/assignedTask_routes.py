from flask import Blueprint, request, jsonify
from app.models.task import Task
from app.models.project import Project
from app.models.organization import Organization
from app.models.assignment import TaskAssignment
from app import db, limiter
from app.utils.pagination import paginate
from app.utils.permissions import is_owner, is_admin, can_access, can_delete
from app.utils.cache import get_cache, set_cache, delete_cache
from app.utils.jwt import jwt_required
from app.services.org_members_service import get_user_role

assignments_bp = Blueprint("assignments", __name__)

@assignments_bp.route("/tasks/<int:task_id>/assign", methods=["POST"])
@jwt_required
def assign_task(task_id):
    """Assign a task to a user."""
    data = request.json or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    project = Project.query.get(task.project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    organization = Organization.query.get(project.organization_id)
    if not organization:
        return jsonify({"error": "Organization not found"}), 404
    
    # Task visibility: Assigned users should see tasks assigned to them, not just created by them
    # Check permissions
    # get_user_role() can also be used here to check same condition below,
    if not can_access(request.user_id, organization.owner_id): # checks if current user is owner or admin of the org.
        print(request.user_id, organization.owner_id)
        # Is it visible to the assigned user ? Yes, as long as the can_access() function checks if the user has access to the project that the task belongs to, then it will ensure that only users who have access to the project can be assigned tasks within that project. 
        # This means that if a user does not have access to the project, they cannot be assigned tasks from that project, 
        # and thus will not see those tasks in their task list. This is a common way to manage permissions and visibility in a multi-user application where tasks are organized under projects.
        return jsonify({"error": "Access denied"}), 403

    # ✅ Check if target user is a member of the organization
    target_user_role = get_user_role(user_id, project.organization_id)
    if not target_user_role:
        return jsonify({"error": "User is not a member of this organization"}), 400
    
    try:
        assignment = TaskAssignment(task_id=task_id, user_id=user_id)
        db.session.add(assignment)
        db.session.commit()

        # Invalidate relevant caches to reflect the new assignment
        delete_cache(f"task:{task_id}")                    # Task details cache
        delete_cache(f"project_tasks:{task.project_id}")  # Project's task list 
        delete_cache(f"user_tasks:{user_id}")              # Assigned user's task list
        delete_cache(f"assigned_tasks:{user_id}")          # User's assigned tasks
        delete_cache(f"project_org:{project.organization_id}")   # Project's tasks 
        # delete_cache(f"user_tasks:{user_id}:*")  # All pages for this user
        # delete_cache(f"project_tasks:{task.project_id}:*")  # All pages for this project
        
        return jsonify({
            "message": "Task assigned successfully",
            "assignment": assignment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to assign task: {str(e)}"}), 500
    
 # GET    /api/tasks/assigned  → Get tasks assigned to me
@assignments_bp.route("/tasks/assign", methods=["GET"])
@jwt_required
def get_assigned_tasks():
    ''' Get tasks assigned to the current user with pagination. '''
    
    user_id = request.user_id
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("per_page", 10, type=int)
    
    cache_key = f"assigned_tasks:{user_id}:{page}:{limit}"
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached)
    try:
        assignments = TaskAssignment.query.filter_by(user_id=user_id)
        result = paginate(assignments, page, limit)
        
        #task_ids = [assignment.task_id for assignment in assignments]
        # tasks = Task.query.filter(Task.id.in_(task_ids)).all()
        
        result['items'] = [task.to_dict() for task in result['items']]
        # Cache the result
        set_cache(cache_key,result, expiry=300)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch assigned tasks: {str(e)}"}), 500

# GET    /api/tasks/{id}/assignments   → See who task is assigned to
@assignments_bp.route("/tasks/<int:task_id>/assign", methods=["GET"])
@jwt_required
def get_task_assignments(task_id):
    ''' Get users assigned to a specific task. '''
    cache_key = f"task_assignments:{task_id}"
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached)
    
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    project = Project.query.get(task.project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    organization = Organization.query.get(project.organization_id)
    if not organization:
        return jsonify({"error": "Organization not found"}), 404
    
    # Check permissions
    if not can_access(request.user_id, organization.owner_id):
        return jsonify({"error": "Access denied. Not the owner of the organization."}), 403

    try:
        assignments = TaskAssignment.query.filter_by(task_id=task_id)
        
        assigned_users = [assignment.user_id for assignment in assignments]
        if not assigned_users:
            return jsonify({"message": "No users assigned to this task"}), 200
        result = {
            "task_id": task_id,
            "total_assigned": len(assigned_users),
            "assigned_users": assigned_users
        }
        set_cache(cache_key, result, expiry=300)
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"error": f"Failed to fetch task assignments: {str(e)}"}), 500

# DELETE /api/tasks/{id}/assign/{user_id} → Unassign user from task
@assignments_bp.route("/tasks/<int:task_id>/assign/<int:assignment_id>", methods=["DELETE"])
@jwt_required
def delete_assignment(task_id, assignment_id):
    ''' Unassign a user from a task. '''
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    project = Project.query.get(task.project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    
    organization = Organization.query.get(project.organization_id)
    if not organization:
        return jsonify({"error": "Organization not found"}), 404
    
    # Check permissions
    if not can_delete(request.user_id, organization.owner_id):
        return jsonify({"error": "Access denied. Not the owner of the organization."}), 403

    assignment = TaskAssignment.query.filter_by(task_id=task_id, id=assignment_id).first()
    
    if not assignment:
        return jsonify({"error": "Assignment not found for the specified task or assignment IDs"}), 404
    
    try:
        db.session.delete(assignment)
        db.session.commit()

        # Invalidate relevant caches to reflect the unassignment
        delete_cache(f"task:{task_id}")                    # Task details cache
        delete_cache(f"project_tasks:{task.project_id}")  # Project's task list 
        delete_cache(f"user_tasks:{assignment.user_id}")              # Assigned user's task list
        delete_cache(f"assigned_id:{assignment_id}")          # User's assigned tasks
        delete_cache(f"project_org:{project.organization_id}")   # Project's tasks 

        return jsonify({"message": "User unassigned from task successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to unassign user from task: {str(e)}"}), 500
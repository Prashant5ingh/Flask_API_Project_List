def is_owner(user_id, resource_user_id):
    """Check if user owns the resource."""
    if not user_id or not resource_user_id:
        return False
    return user_id == resource_user_id

def is_admin(user_role):
    """Check if user is admin."""
    return user_role == "admin"

def can_access(user_id, resource_user_id, user_role=None):
    """Check if user can access resource (owner or admin)."""
    if not user_id or not resource_user_id:
        return False
    return is_owner(user_id, resource_user_id) or is_admin(user_role)

def can_delete(user_id, resource_user_id, user_role=None):
    """Check if user can delete resource."""
    return can_access(user_id, resource_user_id, user_role)


'''
Issues Resolved:
No error handling — doesn't check for None values
No admin override — admins can't access other users' data
Limited functionality — only checks ownership, not other permissions
'''

'''
Yes, this is a basic RBAC (Role-Based Access Control) utility file, but it's very simple. Here's what it does:

Purpose
It provides permission checking functions to determine if a user can perform actions on resources.

How It Works
Function	                 Purpose	                         Example
is_owner()	    Checks if user created/owns the resource	  Only the comment creator can edit their comment
is_admin()	    Checks if user has admin role	              Admin can delete any comment
can_access()	Checks if user can access (owner OR admin)	  Owner or admin can view/edit
can_delete()	Checks if user can delete (owner OR admin)	  Owner or admin can delete

Example usage in comment_routes.py:
# for this we need comments without query filter by user_id, so we can check if the user is admin or not and then decide if they can access the comment or not.
comment = Comment.query.get(comment_id)

# In comment_routes.py
user_role = getattr(request, 'user_role', None)

if not can_access(request.user_id, comment.user_id, user_role=user_role):
    return jsonify({"error": "Unauthorized"}), 403

--------------------------------------------------------------------------    
Limitations (Not Full RBAC Yet)
This file only checks:
✓ Ownership (user_id == resource_user_id)
✓ Admin role (is user an admin?)

It doesn't check:
✗ Organization/project membership
✗ Fine-grained permissions (view, edit, delete separately)
✗ Role hierarchy (moderator, viewer, etc.)

True RBAC Would Include
For a complete RBAC system, you'd need:
def can_edit_comment(user_id, comment_user_id, user_role, project_id):
    # Check if user is:
    # 1. The comment owner
    # 2. An admin
    # 3. A project member with edit permissions
    pass
-------------------------------------------------------------------------    
Current use: Basic ownership + admin override for your comment system.
'''

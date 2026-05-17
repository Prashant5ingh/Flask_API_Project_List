from flask import Blueprint, request, jsonify
from app.models.organization import Organization
from app.models.user import User
from app import db
from app.utils.pagination import paginate
from app.utils.cache import get_cache, set_cache, delete_cache
from app.services.org_members_service import get_user_role, is_org_admin
from app.models.organization_member import MemberRole, OrganizationMember
from app.utils.jwt import jwt_required

org_bp = Blueprint("organization_members", __name__)

@org_bp.route("/organizations/<int:org_id>/members", methods=["POST"])
@jwt_required
def add_org_member(org_id):
    """Add a new member to an organization (Admin only)."""
    data = request.json or {}
    new_user_id = data.get("user_id")
    role = data.get("role", "member").lower()

    # Remember to use cache for fetching organization details if needed, but for critical checks like ownership and existence, we should query the database directly to ensure data integrity.
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404
    
    # Allow owner OR admin to add members
    is_owner = request.user_id == org.owner_id
    is_admin = is_org_admin(request.user_id, org_id)
    
    if not (is_owner or is_admin):
        return jsonify({"error": "Forbidden: Only organization owner or admin can add members"}), 403
    
    if not new_user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    # check if user id exist or not
    if not User.query.get(new_user_id):
        return jsonify({"error": "User with given user_id does not exist"}), 404

    if new_user_id == org.owner_id:
        return jsonify({"error": "Cannot add organization owner as a member"}), 400

        
    # # Only admins can add members
    # if not is_org_admin(request.user_id, org_id):
    #     return jsonify({"error": "Forbidden: Admin role required"}), 403


    # Only allow adding other users as members.
    if new_user_id != request.user_id:
        if role == "admin":
            return jsonify({"error": "Cannot assign admin role to another user. Only organization owner can have admin role."}), 400
        

    # Validate role
    try:
        role_enum = MemberRole(role)
    except ValueError:
        return jsonify({"error": f"Invalid role '{role}'. Must be 'admin' or 'member'"}), 400

    # Prevent duplicate membership
    existing = OrganizationMember.query.filter_by(
        user_id=new_user_id, organization_id=org_id
    ).first()
    if existing:
        return jsonify({"error": "User is already a member of this organization"}), 400

    try:
        member = OrganizationMember(
            user_id=new_user_id,
            organization_id=org_id,
            role=role_enum
        )
        db.session.add(member)
        db.session.commit()

        # Invalidate cache for this user’s orgs
        delete_cache(f"user_org:{new_user_id}")
        delete_cache(f"org_members:{org_id}:*")  # Invalidate all member list caches for this organization since the member list has changed

        return jsonify({
            "message": "Member added successfully",
            "member": member.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to add member: {str(e)}"}), 500
    
# Can be extended with fine-grained permissions (e.g., can_edit_task, can_delete_comment) so roles can control specific actions beyond just admin/member

@org_bp.route("/organizations/<int:org_id>/members", methods=["GET"])
@jwt_required
def get_org_members(org_id):
    """Get all members of an organization (Admin only). with pagination"""
    # Fetches members to that particular organization.
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int) # Default to 5 tasks per page for better UX and performance. Can be adjusted as needed.
    
    # Cache key includes user_id for security
    # cache_key = f"user_orgs:{request.user_id}:{page}:{limit}"
    cache_key = f"org_members:{org_id}:{request.user_id}:{page}:{limit}"
    cached = get_cache(cache_key)

    if cached:
        return jsonify(cached)
    
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    if request.user_id != org.owner_id and not is_org_admin(request.user_id, org_id):
        return jsonify({"error": "Forbidden: Only organization owner or admins can view members"}), 403

    try:
        members = OrganizationMember.query.filter_by(organization_id=org_id) # fetching members of the organization from the database. We filter the OrganizationMember records by the organization_id to get all members associated with that organization. This allows us to retrieve the list of members who belong to the specified organization, which we can then return in the response.
        result = paginate(members, page, limit)

        # Serialize data
        result["items"] = [t.to_dict() for t in result["items"]]
        
        set_cache(cache_key, result, expiry=300) # 300 sec
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch members: {str(e)}"}), 400
    
@org_bp.route("/organizations/<int:org_id>/members/<int:mem_id>", methods=["GET"])
@jwt_required
def get_org_member(org_id,mem_id):
    """Get a single member of an organization (Admin only)."""
    cache_key = f"org_member:{org_id}:{mem_id}" 
    
    # Check cache first
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached)
    
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    if request.user_id != org.owner_id and not is_org_admin(request.user_id, org_id):
        return jsonify({"error": "Forbidden: Only organization owner or admins can view members"}), 403

    member = OrganizationMember.query.filter_by(id=mem_id, organization_id=org_id).first()
    
    if not member:
        return jsonify({"error": "Member not found"}), 404
    
    data = member.to_dict()
    set_cache(cache_key, data, expiry=300)
    
    return jsonify(data)

@org_bp.route("/organizations/<int:org_id>/members/<int:mem_id>", methods=["PATCH"])
@jwt_required
def update_org_member(org_id, mem_id):
    """Update a member's role in an organization (Admin only)."""
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    if request.user_id != org.owner_id and not is_org_admin(request.user_id, org_id):
        return jsonify({"error": "Forbidden: Only organization owner or admins can update members"}), 403

    member = OrganizationMember.query.filter_by(id=mem_id, organization_id=org_id).first()
    
    if not member:
        return jsonify({"error": "Member not found"}), 404
    
    data = request.json or {}
    new_role = data.get("role", "").lower()
    # user_id = data.get("user_id")

    try:
        if new_role:
            try:
                member.role = MemberRole(new_role)
            except ValueError:
                return jsonify({"error": f"Invalid role '{new_role}'. Must be 'admin' or 'member'"}), 400
        
        # if user_id:
        #     if not User.query.get(user_id):
        #         return jsonify({"error": "User with given user_id does not exist"}), 404
        #     member.user_id = user_id
        db.session.commit()

        # Invalidate cache for this user’s orgs and member details
        delete_cache(f"user_org:{member.user_id}")
        delete_cache(f"org_member:{org_id}:{mem_id}")
        delete_cache(f"org_members:{org_id}:*")  # Invalidate all member list caches for this organization since the member list has changed

        return jsonify({
            "message": "Member updated successfully",
            "member": member.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update member: {str(e)}"}), 500

@org_bp.route("/organizations/<int:org_id>/members/<int:mem_id>", methods=["DELETE"])
@jwt_required
def delete_org_member(org_id, mem_id):
    """Remove a member from an organization (Admin only)."""
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"error": "Organization not found"}), 404

    if request.user_id != org.owner_id and not is_org_admin(request.user_id, org_id):
        return jsonify({"error": "Forbidden: Only organization owner or admins can remove members"}), 403

    member = OrganizationMember.query.filter_by(id=mem_id, organization_id=org_id).first()
    
    if not member:
        return jsonify({"error": "Member not found"}), 404
    
    try:
        db.session.delete(member)
        db.session.commit()

        # Invalidate cache for this user’s orgs and member details
        delete_cache(f"user_org:{member.user_id}")
        delete_cache(f"org_member:{org_id}:{mem_id}")
        delete_cache(f"org_members:{org_id}:*")  # Invalidate all member list caches for this organization since the member list has changed

        return jsonify({"message": "Member removed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to remove member: {str(e)}"}), 500
    
    
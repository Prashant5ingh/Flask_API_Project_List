from flask import Blueprint, request, jsonify
from app.models.organization import Organization
from app.models.organization_member import OrganizationMember, MemberRole
from app import db
from app.utils.jwt import jwt_required
from app.utils.pagination import paginate
from app.utils.cache import get_cache, set_cache, delete_cache


organization_bp = Blueprint("organizations", __name__)

@organization_bp.route("", methods=["POST"])
@jwt_required
def create_organization():
    """Create a new organization."""
    data = request.json or {}
    
    # Validate input
    if not data.get("name"):
        return jsonify({"error": "Organization name required"}), 400
    
    # if not data.get("owner_id"):
    #     return jsonify({"error": "Owner ID required"}), 400
    
    
    try:
        organization = Organization(
            name=data["name"],
            # description=data.get("description", ""),
            owner_id=request.user_id,
        )
        db.session.add(organization)
        #db.session.flush()  # assigns defaults like created_at and id
        
        # Try serializing before commit. Need flush() to work with this line. Also isformat() works fine with flush().
        # project_data = project.to_dict() 

        # If serialization succeeds, then commit
        db.session.commit()

        # Add creator as admin 
        # Note: We should add the creator as an admin member of the organization to ensure they have the necessary permissions to manage it. 
        # This is important for maintaining proper access control and allowing the creator to perform administrative tasks on the organization they just created.
        admin_member = OrganizationMember(
        user_id=request.user_id,
        organization_id=organization.id,
        role=MemberRole.ADMIN
            )
        db.session.add(admin_member)
        db.session.commit()

        delete_cache(f"user_org:{request.user_id}:*") # Clear user's org list cache to reflect new org creation. Cache key should match the one used in get
        delete_cache(f"org_members:{organization.id}:*")  # Invalidate all member list caches for this organization since the member list has changed (new org means new member list with creator as admin)     
        
        return jsonify({
            "message": "Organization created",
            "organization": organization.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create organization: {str(e)}"}), 400

@organization_bp.route("/", methods=["GET"])
@jwt_required
def get_organizations(): # all organizations for user with pagination
    """Get user's organizations with pagination."""
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int) # Default to 5 tasks per page for better UX and performance. Can be adjusted as needed.
    
    # Cache key includes user_id for security
    cache_key = f"user_org:{request.user_id}:{page}:{limit}"
    cached = get_cache(cache_key)
    
    if cached:
        return jsonify(cached)
    
    try:
        # Filter organizations by current user only
        query = Organization.query.filter_by(owner_id=request.user_id)
        result = paginate(query, page, limit)
        
        # Serialize data
        result["items"] = [t.to_dict() for t in result["items"]]
        
        set_cache(cache_key, result, expiry=300)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch organizations: {str(e)}"}), 400

@organization_bp.route("/<int:organization_id>", methods=["GET"])
@jwt_required
def get_organization(organization_id):
    """Get organization details."""
    cache_key = f"organization:{organization_id}"
    
    # Check cache first
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached)
    
    organization = Organization.query.filter_by(id=organization_id, owner_id=request.user_id).first()

    
    if not organization:
        return jsonify({"error": "Organization not found"}), 404
    
    # TODO: Verify user has access to organization
    
    data = organization.to_dict()
    set_cache(cache_key, data, expiry=300)
    return jsonify(data)

@organization_bp.route("/<int:organization_id>", methods=["PUT"])
@jwt_required
def update_organization(organization_id):
    """Update organization."""
    organization = Organization.query.filter_by(id=organization_id, owner_id=request.user_id).first() # Ensure user can only update their own organizations

    if not organization:
        return jsonify({"error": "Organization not found"}), 404
    if organization.owner_id != request.user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json or {}
    
    try:
        if "name" in data:
            organization.name = data["name"]
        if "description" in data:
            organization.description = data["description"]
        
        db.session.commit()
        delete_cache(f"organization:{organization_id}")
        
        return jsonify({
            "message": "Organization updated",
            "organization": organization.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update organization: {str(e)}"}), 400

@organization_bp.route("/<int:organization_id>", methods=["DELETE"])
@jwt_required
def delete_organization(organization_id):
    """Delete organization."""
    organization = Organization.query.filter_by(id=organization_id, owner_id=request.user_id).first() # Ensure user can only delete their own organizations 

    if not organization:
        return jsonify({"error": "Organization not found"}), 404

    if organization.owner_id != request.user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    try:
        db.session.delete(organization)
        db.session.commit()
        delete_cache(f"organization:{organization_id}")
        
        return jsonify({"message": "Organization deleted along with its dependent projects"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete organization: {str(e)}"}), 400


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
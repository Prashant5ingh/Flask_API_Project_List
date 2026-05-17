from app.models.organization import Organization
from app.models.user import User
from app.models.organization_member import OrganizationMember, MemberRole


def get_user_role(user_id, organization_id):
    membership = OrganizationMember.query.filter_by(
        user_id=user_id, organization_id=organization_id
    ).first()
    return membership.role if membership else None

def is_org_admin(user_id, organization_id):
    role = get_user_role(user_id, organization_id)
    return role == MemberRole.ADMIN


from datetime import datetime
from enum import Enum
from app import db

class MemberRole(Enum): # Using Enum for role management 
    ADMIN = 'admin'
    MEMBER = 'member'

class OrganizationMember(db.Model):
    __tablename__ = 'organization_members'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id', ondelete="CASCADE"), nullable=False) # ondelete cascade to automatically delete memberships when organization is deleted. needs to be added to be added in fk before table is created. 
    role = db.Column(db.Enum(MemberRole), default=MemberRole.MEMBER, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationships 
    user = db.relationship('User', back_populates='organization_memberships')
    organization = db.relationship('Organization', back_populates='members')
    # Relationships are built on Foreign Keys. With FK → Use Relationships for easier access to related data. FK → Relationship. No FK → No Relationship.

    # Option A: Use back_populates on both sides for more explicit control:
    # Option B: Use backref on one side only for simpler setup. Here we use backref for simplicity, but back_populates can be used for more complex relationships or if you want to avoid circular imports.
    
    # Unique constraint - prevent duplicate memberships
    __table_args__ = (
        db.UniqueConstraint('user_id', 'organization_id', name='unique_user_org'),
    )
    
    def is_admin(self):
        """Check if member is an admin"""
        return self.role == MemberRole.ADMIN
    
    def __repr__(self):
        return f'<OrganizationMember user_id={self.user_id} org_id={self.organization_id} role={self.role.value}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "organization_id": self.organization_id,
            "role": self.role.value,
            "created_at": self.created_at.isoformat()
        }

# Using an association table organization_members to implement RBAC instead of tightly coupling users and organizations.
# Role-Based Access Control for Authorization, which allows for flexible permission management based on user roles within an organization.

# 🔥 How it Works (Concept)
# Instead of: ❌ user → organization (direct)
# We do: User ↔ OrganizationMember ↔ Organization
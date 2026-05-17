from datetime import datetime
from app import db

class Organization(db.Model):
    __tablename__ = 'organizations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationship to User model (optional but useful)
    owner = db.relationship('User', backref='organizations')
    # No explicit projects relationship here — backref already gives you `organization.projects`
    
    # Access members
    # members = db.relationship('OrganizationMember', back_populates='organization')
    members = db.relationship(
        'OrganizationMember', back_populates="organization",
    cascade="all, delete-orphan",
    passive_deletes=True)

    # Ways to handle dependent projects when organization is deleted:
    # Set organization_id to NULL (if allowed) or cascade delete projects when organization is deleted or Prevent deletion (with err msg) if projects exist

    def __repr__(self):
        return f'<Organization {self.name}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat()
        }
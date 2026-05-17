from datetime import datetime
from app import db

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    # Relationships
    # organization = db.relationship('Organization', backref='projects')
    organization = db.relationship('Organization', backref=db.backref('projects', cascade="all, delete-orphan")) # This ensures that when an organization is deleted, all its associated projects (and their tasks) are also deleted automatically. It maintains referential integrity and prevents orphaned records in the database.
    
    creator = db.relationship('User', backref='created_projects')
    
    tasks = db.relationship('Task', back_populates='project', cascade="all, delete-orphan", passive_deletes=True) 
    # This ensures that when a project is deleted, all its associated tasks are also deleted automatically. 
    # It maintains referential integrity and prevents orphaned tasks in the database.
    
    # Ways to handle dependent projects when organization is deleted:
    # Set organization_id to NULL (if allowed) or cascade delete projects when organization is deleted or Prevent deletion (with err msg) if projects exist

    # Unique constraint - prevent duplicate project names within same org
    __table_args__ = (
        db.UniqueConstraint('name', 'organization_id', name='unique_project_per_org'),
    )
    
    def __repr__(self):
        return f'<Project {self.name} (org_id={self.organization_id})>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "organization_id": self.organization_id,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat()

        }

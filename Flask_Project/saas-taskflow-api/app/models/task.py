from datetime import datetime, timedelta
from app import db


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.Enum("todo", "inprogress", "done","pending", name="task_status"),
        default="todo",
        nullable=False
    )

    project_id = db.Column(
        db.Integer,
        db.ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    due_date = db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(days=2), nullable=True)


    created_at = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )

    # Relationships (optional but recommended)
    creator = db.relationship("User", backref="created_tasks")
    
    project = db.relationship('Project', back_populates='tasks') 
    # This sets up a bidirectional relationship between Task and Project models. It allows us to access the project of a task via task.project and also access all tasks of a project via project.tasks. 
    # The cascade option ensures that if a project is deleted, all its associated tasks are also deleted automatically.

    comments = db.relationship("Comment", back_populates="task", cascade="all, delete-orphan", passive_deletes=True) # This sets up a bidirectional relationship between Task and Comment models. It allows us to access the task of a comment via comment.task and also access all comments of a task via task.comments. The cascade option ensures that if a task is deleted, all its associated comments are also deleted automatically.

    task_assignments = db.relationship("TaskAssignment", back_populates="task", cascade="all, delete-orphan", passive_deletes=True)

    def __repr__(self):
        return f"<Task {self.title}>"
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "project_id": self.project_id,
            "created_by": self.created_by,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "created_at": self.created_at.isoformat() if self.due_date else None
        }
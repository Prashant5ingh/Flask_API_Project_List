from datetime import datetime
from app import db


class TaskAssignment(db.Model):
    __tablename__ = "task_assignments"

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    assigned_at = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    ) # for future use - can implement  assigned_by to track who assigned the task, role of the assigner and priority of the assignment (e.g. if a manager assigns a task vs a peer assigns a task)

    # Relationships
    task = db.relationship("Task", back_populates="task_assignments")
    user = db.relationship("User", backref="task_assignments")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "assigned_at": self.assigned_at.isoformat()
        }

    def __repr__(self):
        return f"<TaskAssignment task={self.task_id} user={self.user_id}>"
    
# Key features:

# ondelete="CASCADE" — If a task/user is deleted, assignments are automatically deleted too
# Composite relationship — Connects tasks to users via many-to-many

# 🔥 Why this design is correct
# Enables:
# One task → many users
# One user → many tasks
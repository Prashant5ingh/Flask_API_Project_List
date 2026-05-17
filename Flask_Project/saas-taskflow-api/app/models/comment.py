from datetime import datetime
from app import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)

    task_id = db.Column(
        db.Integer,
        db.ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.now,
        nullable=False
    )

    # Relationships
    # task = db.relationship("Task", backref="comments")
    task = db.relationship("Task", back_populates="comments") 
    user = db.relationship("User", backref="comments")

    def __repr__(self):
        return f"<Comment {self.id} Task={self.task_id}>"
    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "user_id": self.user_id,
            "content": self.content,
            "created_at": self.created_at.isoformat()
        }
    
# 🔥 Key Design Decisions
# task_id (CASCADE)
# 👉 If task is deleted → all comments are deleted
# user_id (SET NULL)
# 👉 If user is deleted → comment remains (important for audit/history)
# content as Text
# 👉 Supports long comments (better than String)
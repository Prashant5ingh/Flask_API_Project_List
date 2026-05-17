from app.models.task import Task
from app.models.project import Project
from app import db
from app.utils.cache import delete_cache

def validate_task_data(data):
    """Validate task data."""
    if not data.get('title'):
        return False, "Title is required"
    
    if len(data['title']) < 3:
        return False, "Title must be at least 3 characters"
    
    if len(data.get('description', '')) > 500:
        return False, "Description too long (max 500 chars)"
    
    project = Project.query.get(data["project_id"])
    if not project:
        return False, "Invalid project ID or project does not exist"
 
    return True, None

def create_task(data, user_id):
    """Create a new task for user."""
    is_valid, error = validate_task_data(data)
    if not is_valid:
        return None, error
    
    try:
        # Only allow specific fields
        task = Task(
            title=data['title'],
            description=data.get('description', ''),
            project_id=data.get('project_id'),
            status="todo",
            created_by=user_id
        )
        db.session.add(task)
        db.session.commit()
        
        # Clear cache
        delete_cache(f"user_tasks:{user_id}")
        
        return task, None
    except Exception as e:
        db.session.rollback()
        return None, f"Failed to create task: {str(e)}"

def update_task(task_id, data, user_id):
    """Update a task."""
    task = Task.query.filter_by(id=task_id, created_by=user_id).first()
    
    if not task:
        return None, "Task not found"
    
    try:
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            print("In status update block")
            # task.status = data['status']
            if data['status'] in ['todo', 'inprogress', 'done', 'pending']:
                task.status = data['status']
            else:
                return None, "Invalid status value (allowed: todo, inprogress, done, pending)"
        

        db.session.commit()
        delete_cache(f"user_tasks:{user_id}")
        
        return task, None
    except Exception as e:
        db.session.rollback()
        return None, f"Failed to update task: {str(e)}"

def delete_task(task_id, user_id):
    """Delete a task."""
    task = Task.query.filter_by(id=task_id, created_by=user_id).first()
    
    if not task:
        return False, "Task not found"
    
    try:
        db.session.delete(task)
        db.session.commit()
        delete_cache(f"user_tasks:{user_id}")
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, f"Failed to delete task: {str(e)}"
    

'''
Issues Resolved:
No input validation — doesn't check required fields
Mass assignment vulnerability — **data accepts any fields, potential security issue
No error handling — crashes on database errors
No cache invalidation — if you use caching, stale data remains
No transaction management — can leave database in bad state
'''
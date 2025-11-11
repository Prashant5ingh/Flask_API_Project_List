from flask import Flask, render_template, request,redirect, url_for
from flask_scss import Scss
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

'''
No — not necessary if you use the default folder names and locations.

By default Flask looks for:
templates/ (for Jinja templates) and static/ (for static files)
both relative to your app package/module root. So this is equivalent:
'''
app = Flask(__name__, template_folder='templates', static_folder='static')

Scss(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasklist.db"
# app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://root:Primesql%409@localhost:3306/tasklist_db'
# app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:mysecretpassword@localhost:5433/tasklist_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Data Class ~ Row of data in table
class Todo(db.Model):
    """A Model for an Item in the Todo List

    Args:
        db (_type_): database model

    Returns:
        __repr__: string rep.
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.id}'
    

with app.app_context(): # Create the database and the db table
    db.create_all()

# Routes to webpages
# Home Page    
@app.route('/', methods=["POST","GET"])
def index():
    """Main page for App

    Returns:
        page: home page
    """
    # Add a task
    if request.method == "POST":
        current_task = request.form['content']
        new_task = Todo(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('index'))
            # return redirect("/")
        except Exception as e:
            print(f"Error:{e}")
            return f'Error:{e}'

    # See all current tasks
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks = tasks)

@app.route("/delete/<int:id>")
def delete(id):         # id:int --> it is optional to specify type here
    """delete an item from the todo list

    Args:
        id (int): uuid for each item in the todo list

    Returns:
        redirect: delete and return to home
    """
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()  
        return redirect("/")
        # return redirect(url_for('index'))
    except Exception as e:
        return f"Error:{e}"
    
# Edit an item 
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form.get('content')
        try:
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            print(f"ERROR:{e}")
            return "Error"
    else:
        return render_template("update.html", task=task)

if __name__ in "__main__":

    app.run(debug=True, host="0.0.0.0", port=5500) # This port will serve as docker server port. If not provided any port then it will use 5000 here and also in docker.
    # app.run(debug=True, host="0.0.0.0", port=5500)
    
    # docker build --tag primedochub/todo_app-docker:latest .
    # docker container run -d -p 4200:5500 primedochub/todo_app-docker
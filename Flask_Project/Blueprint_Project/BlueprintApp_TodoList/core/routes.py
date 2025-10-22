from flask import Flask,render_template, request,redirect,url_for,Blueprint

core = Blueprint('Core', __name__, template_folder='templates') # Todos is blueprint name and 'todos' is blueprint variable used for route decorators and registering blueprint in main app

@core.route('/')
def index():
    return render_template('core/index.html') # render template is not using blueprint name instead given dir path for index.html

from flask import Flask,render_template, request,redirect,url_for,flash

from models import Person, UserAuth
from flask_login import login_user, logout_user, current_user, login_required # login_required will make sure that login is required for certain endpoints.

# To avoid circular imports we will use function here
def register_routes(app,db):
    @app.route('/', methods=['GET','POST'])
    def index():
        if request.method == 'GET':
            people = Person.query.all() # to fetch all usersdetails from db
            return render_template('index.html',people = people)
        elif request.method == 'POST':
            name = request.form.get('name')
            age = int(request.form['age'])
            job = request.form.get('job')

            person = Person(name=name, age=age, job=job)

            db.session.add(person) # Adding data in db
            db.session.commit() # saving the changes

            #people = Person.query.all()
            return redirect(url_for('index'))  # Redirect after POST
            # After handling the POST and committing to the database, redirect to the GET route instead of rendering the template directly.
            # This prevents duplicate submissions on reload.Update your POST handler in routes.py
            
            # Remove extra spaces in your form’s action.
            # Use redirect(url_for('index')) after POST to prevent duplicate submissions on page reload.

    @app.route('/delete/<pid>', methods=['DELETE'])
    def delete(pid):
        Person.query.filter(Person.pid == pid).delete()
        
        db.session.commit()
        people = Person.query.all()
        return render_template('index.html',people = people)
        #return redirect(url_for('index'))
    
    @app.route('/userdetail/<pid>')
    def detail(pid):
        person = Person.query.filter(Person.pid == pid).first()
        return render_template('userdetail.html', person = person)
    
def authRoutes(app,db, bcrypt):
     @app.route('/')
     def authIndex():
        #  if current_user.is_authenticated:
        #      return str(current_user.username)
        #  else:
        #      return "No user is logged in"
        return render_template('index.html')
     
     @app.route('/signup', methods=['GET','POST'])
     def signup():
        if request.method == 'GET':
            return render_template('signup.html')
        elif (request.method == 'POST'):
            username = request.form.get('username')
            password = request.form.get('password')

            # Now we hash the password then store that hash code to db
            hash_password = bcrypt.generate_password_hash(password)

            user = UserAuth(username = username, password = hash_password)
            db.session.add(user)
            db.session.commit()
            flash('SignUp successfull !!!')
            return redirect(url_for('authIndex'))

     @app.route('/login', methods=['GET','POST'])
     def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif (request.method == 'POST'):
             username = request.form.get('username')
             password = request.form.get('password')

             user = UserAuth.query.filter(UserAuth.username == username).first()

             if not user:
                 signup_url = url_for('signup')
                 message = f"<h1>User Doesn't exist</h1> <a href='{signup_url}'>Sign Up</a>"
                 return message

                 

             # Now compare the entered hash password with the stored hash password in db
             if bcrypt.check_password_hash(user.password, password):
                 login_user(user) # using flask_login feature
                 flash('Login successfull !!!')

                 return redirect(url_for('authIndex'))
             else:
                 return "Login Failed"

     
    #  @app.route('/login/<uid>')
    #  def login(uid):
    #      user = UserAuth.query.get(uid)
    #      login_user(user)
    #      return "Login Success"
     
     @app.route('/logout')
     def logout():
         logout_user() # flask_logout feature
         return redirect(url_for('authIndex'))
     

     # Protect any endpoint when user is authenticated
     @app.route('/secret')
     @login_required
     def secret():
         # role based access
        #  if current_user.role == 'admin':
        #      return 'My secret message !!!'
        #  else:
        #      return 'No permission'

        # if not current_user.is_authenticated:
           
        return 'My secret message !!!'
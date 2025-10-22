# ORM converts python classes of models into relational database tables

from flask_login import UserMixin # flask login doesn't implement any login procedure or logic like how you login or when you login in and out or login using password, token, without any security measure. 
# That is up to the developer how to implement all that.
# flask login only does that it logs you in and keeps you logged in and handles the user currently logged in or logged you out.

from app import db


# Going to build authentication system around user class --> login, signup and keep the track of which user is logged in currently.
# Using login and bcrypt lib ( stores credentials in db as hash code)

class Person(db.Model):
    __tablename__ = 'people' # name of table in db
    pid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)  # In sqlite there is no varchar, this field can't be empty.
    age = db.Column(db.Integer)  
    job = db.Column(db.Text) 

    def __repr__(self):
         return f'Person with name {self.name} and age {self.age}'
    

class UserAuth(db.Model, UserMixin):
     __tablename__ = 'users' # name of table in db

     uid = db.Column(db.Integer, primary_key=True)
     username = db.Column(db.String, nullable=False)
     password = db.Column(db.String, nullable=False)
     role = db.Column(db.String)
     description = db.Column(db.String)

     def __repr__(self):
          return f'User: {self.username}, Role: {self.role}'
    
    # access user by id
     def get_id(self):
          return self.uid
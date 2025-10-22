from flask import Flask,session, flash,request, make_response,render_template # type: ignore

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/') # created the application
app.secret_key = 'some123'  # secret key for session id of login user's data on the server side
@app.route('/')  # route decorator
def index():
    # return ("Hello, Flask!") --> both are same
     return render_template('index.html', message='Index')



# cookies --> on client side, change and seen by users
# session --> server side, sensitive data
@app.route('/set_session_data')
def set_data():
     session['name'] = 'Prime' # session data is sensitive and should not be changed or seen by user.
     session['other'] = 'Session data'
     # This data will be stored on the server side but a session id as value will be stored in cookies section.

     return render_template('index.html', message='Sesssion data set')

@app.route('/get_session_data')
def get_Data():
     if 'name' in session.keys() and 'other' in session.keys():
          name = session['name']
          other = session.get('other')
          # The above data can only be fetched when the server confirms that the cookies have same session identifier or id of the same user who had send the session data
          # If user is same and session id is present in cookies section then data can be fetched for the same user else id not present then error occurs
          return render_template('index.html', message=f'Fetched Session data Name: {name} and Other: {other}')
     else:
          return render_template('index.html', message=f'No session found to get data')


@app.route('/clear_session_data')
def clear_data():
    if (session.keys()):
         session.clear()
         # session.pop('name') # to remove specific session identifier or data not the whole data (in form of dict)
         return render_template('index.html', message='Sesssion data cleared')
    else: 
          return render_template('index.html', message='No session data or id exist !!!')



@app.route('/set_cookies_data')
def cookies_data():
     # can set condition for not adding same cookies agian
     response = make_response(render_template('index.html', message='Cookies are set'))
     response.set_cookie('cookie_name', 'cookie_value') # key-value pair --> this data can be changed by user
     return response

@app.route('/get_cookies_data')
def get_cookies():
     # set condition for fetching cookies if exist else error msg
     cookie_value = request.cookies['cookie_name']
     return render_template('index.html', message=f'Cookies fetched and value is: {cookie_value}')

@app.route('/remove_cookies_data')
def remove_cookies():
     response = make_response(render_template('index.html', message='Cookies are removed'))
     response.set_cookie('cookie_name', expires=0) # key-value pair --> this data can be changed by user
     return response



@app.route('/flash_message_login', methods=['GET','POST'])
def flash_message():
     if request.method == 'GET':
          return render_template('flash_message.html')
     elif request.method == 'POST':
          username = request.form.get('username')
          password = request.form.get('password')
          if username == "Prime" and password == "12345":
               flash('Successful Login')
               return render_template('flash_message.html',message='')
          else:    
               flash('Login Failed !!!') 
               return render_template('index.html',message='')



if __name__ == "__main__":
    app.run(host="localhost", port=5500, debug=True) # debug=True for dev mode while deploy false or remove it.
    # flask run cmd --> uses port 5000 by default.
    # python app.py --> uses user defined port. More effective for real time changes.
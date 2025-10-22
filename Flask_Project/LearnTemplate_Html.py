from flask import Flask, request, make_response, render_template, redirect, url_for # type: ignore

app = Flask(__name__, template_folder='templates') # created the application

@app.route('/')  # route decorator
def index():
     name="Prime"
     add=30+20

     myList = [10,20,30,40,50]
     newList = []
     for x in myList:
          if x > 20:
               newList.append(x)
    #  print(newList)
     
    # return ("Hello, Flask!") --> both are same
     return render_template('index.html', val1=name, val2=add, mylist=newList) # fetch html from template folder. Passing variables to html

@app.route('/other')  # route decorator # Dynamic URL
def other():
     some_text="My name is prashant"
     return render_template('other.html', text=some_text)

@app.route('/redirect_endpoint') # after putting this endpoint it will redirect user to "/other" endpoint
def redirect_endpoint():
     return redirect(url_for('other'))


#Custom filter template
# This filter exist in jinja but still creating to learn custom filters
@app.template_filter('reverse_string')
def reverse_string(s):
     return s[::-1]


@app.template_filter('repeat')
def repeat(s, times=2):
     return s * times

@app.template_filter('alter_case')
def alter_case(text):
     return ''.join([c.upper() if i% 2 == 0 else c.lower() for i,c in enumerate(text)])


if __name__ == "__main__":
    app.run(host="localhost", port=5500, debug=True)
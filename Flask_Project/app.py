from flask import Flask, request, make_response # type: ignore

app = Flask(__name__) # created the application

@app.route('/')  # route decorator
def index():
    # return ("Hello, Flask!") --> both are same
     return "<h1>Hello, Flask!</h1>"

@app.route('/home')  
def home():
     return ("<h2>Hello, Home Page!</h2>") 


@app.route('/dynamicUrl/<name>')  # url processor --> takes a dynamic endpoint as variable 
def url(name):
     return f"<h3>This is a dynamic url page! of name: {name}</h3>" 
     # return "<h3>Error: Please provide valid integers.</h3>", 400  --> status code


@app.route('/dynamicAdd/<num1>/<num2>')  # url processor --> takes a dynamic endpoint as variable 
def add(num1,num2):
    # return f"<h3>This is a dynamic url page! for addition of urls as string: {num1} + {num2} = {num1+num2}</h3>" # concat of string
     return f"<h3>This is a dynamic url page! for addition of urls as integer: {num1} + {num2} = {int(num1)+int(num2)}</h3>" # addition of int
# We can also define num1 and num2 as int in the route itself --> <int:num1>/<int:num2>


# url params handling with request object
@app.route('/urlParams')  # url processor --> takes a dynamic endpoint as variable 
def urlParams():
        # try: try except can also be used but for now we are using if else to handle errors
        if 'code' in request.args.keys() and 'name' in request.args.keys(): # to check if key exists in dict
            data="prime"
            # print(f"{data}",data) --> combination of print and fstring
            # return f"<h3>This is a url params {data} example</h3>"
            code = request.args.get('code') # or .args['code'] as it is a dict, gives error if any key not found in case of dictionary --> BadRequestKeyError
            name = request.args.get('name') # to get specific arg and to handle if any of the params is missing while using .get(), We need t handle it with if else or try except
            return f"<h3>{request.args}:: code as -> {code}:: name as -> {name}" # to get all args as dict from http://localhost:5500/urlParams?name=Prime&code=Python. Stores in ImmutableMultiDict([('name', 'Prime'), ('code', 'Python')])
        else:
             return "<h3> Some params are missing!</h3>",400    # 400 is for bad request
        # except Exception as e:
        #      return f"<h3>Error: {e} </h3>",400  # 400 is for bad request



# All of the above requests are GET request by default.      
# Make a POST request and GET request in same route
@app.route('/postRequest', methods=['POST','GET','PUT'])
def postRequest():

     # Making a custom response 
     response = make_response("This is a custome response for POST request") 
     response.status_code = 202 # 202 is for accepted
     response.headers['content-type'] = 'type/plain' #by default it is text/html

     # GET request is not allowed when methods=['POST]. To allow do: methods=['POST',"GET"]
     if request.method == 'GET':
          return "Made a GET request",200
     elif request.method == 'PUT':
          return 'Made a PUT request', 405 # method not allowed
     
     #return "Returned a POST Reqest",201 # This line only works for successful POST request. 201 is for created
     return response, response.status_code 





if __name__ == "__main__":
    app.run(host="localhost", port=5500, debug=True) # debug=True for dev mode while deploy false or remove it.
    # flask run cmd --> uses port 5000 by default.
    # python app.py --> uses user defined port. More effective for real time changes.
from flask import Flask, request, make_response,render_template # type: ignore

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/') # created the application

@app.route('/')  # route decorator
def index():
    # return ("Hello, Flask!") --> both are same
     return render_template('index.html')


if __name__ == "__main__":
    app.run(host="localhost", port=5500, debug=True) # debug=True for dev mode while deploy false or remove it.
    # flask run cmd --> uses port 5000 by default.
    # python app.py --> uses user defined port. More effective for real time changes.
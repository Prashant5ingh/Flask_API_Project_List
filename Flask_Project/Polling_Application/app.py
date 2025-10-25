from flask import Flask, request, redirect, render_template, url_for, make_response # type: ignore
import pandas as pd
import os.path

app = Flask(__name__, template_folder='templates') # created the application

if not os.path.exists("polls.csv"):
     structure = {
          "id":[],
          "poll":[],
          "option1": [],
          "option2": [],
          "option3": [],
          "votes1": [],
          "votes2": [],
          "votes3": []
     }
     pd.DataFrame(structure).set_index("id").to_csv("polls.csv") # converting structure in dataframe. Putting the structure data in csv file.

polls_df = pd.read_csv("polls.csv").set_index("id")


@app.route('/')  # route decorator
def index():
    # return ("Hello, Flask!") --> both are same
     return render_template("index.html", polls = polls_df)

@app.route('/polls/<id>')  # can make id integer here also. <int:id>
def polls(id):
     poll = polls_df.loc[int(id)]
     # return str(poll)
     return render_template("show_poll.html", poll = poll)

@app.route("/vote/<id>/<option>") # can make id integer here also. <int:id>
def vote(id, option):
     # polls_df.at[int(int(id), "votes"+str(option))] += 1
     
     # Setting up cookie for user, not to vote more than once
     if request.cookies.get(f"vote_{id}_cookie") is None:
          polls_df.at[int(id), "votes" + str(option)] = int(polls_df.at[int(id), "votes" + str(option)]) + 1
          polls_df.to_csv("polls.csv")
          response = make_response(redirect(url_for('polls', id = id)))
          response.set_cookie(f"vote_{id}_cookie", str(option)) # cookie name with id: vote_1_cookie  selected option ot of 2 of that id or index: 2
          return response
     else:
          return "Cannot vote more than once"

@app.route('/polls', methods=["GET","POST"])  
def create_poll():
     if request.method == "GET":
          return render_template("new_poll.html")
     elif request.method == "POST":
          poll = request.form['poll']
          option1 = request.form.get("option1")
          option2 = request.form.get("option2")
          option3 = request.form.get("option3")
          polls_df.loc[max(polls_df.index.values) + 1] = [poll, option1, option2, option3, 0 , 0 , 0]
          polls_df.to_csv("polls.csv")
          return redirect(url_for('index'))
     # return "<h3>Error: Please provide valid integers.</h3>", 400  --> status code


if __name__ == "__main__":
    app.run(host="localhost", port=5500, debug=True) # debug=True for dev mode while deploy false or remove it.
    # flask run cmd --> uses port 5000 by default.
    # python app.py --> uses user defined port. More effective for real time changes.
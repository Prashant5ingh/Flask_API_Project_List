from flask import Flask, request, make_response, render_template, redirect, url_for, Response, send_from_directory, jsonify # type: ignore
import pandas as pd # type : ignore
import os
import uuid
app = Flask(__name__, template_folder='templates') # created the application

# @app.route('/', methods=['GET','POST'])  # route decorator
# def index():
#      if request.method == 'GET':
#          return render_template('index.html') 
#      elif request.method == 'POST': # Can create seperate request just for POST. 
#          return ""

@app.route('/', methods=['GET'])  # route decorator
def index():
   
     return render_template('index.html') 
   

@app.route('/login', methods=['POST'])
def login():
    userName = request.form['username'] # request.form.get('username') either is fine
    password = request.form.get('password')

    # if 'username' in request.form.keys(): checks if the submitted form data contains a field named "username".
    # request.form is a dictionary-like object holding form data sent via POST.
    # .keys() returns all field names in the form.
    # This condition ensures "username" was included in the POST request before you try to access its value, helping avoid errors if the field is missing.
    
    # print(userName,request.form)
    if userName == "Prime" and password=="prime":
        return 'Success'
    else:
        return 'Failure'
    
@app.route('/fileupload', methods=['POST'])
def file_upload():
    file = request.files['file']

    if file.content_type == 'text/plain':
        return file.read().decode()
    elif file.content_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or file.content_type =='application/vnd.ms-excel':
        df = pd.read_excel(file)
        return df.to_html()

# Method 1:convert excel to csv and download
@app.route('/convert_csv', methods=['POST'])
def convert_to_csv():
    if 'filecsv' not in request.files:
        return "No file part in the request", 400
    file = request.files['filecsv']
    if file.filename == '':
        return "No file selected", 400
    df = pd.read_excel(file)
    res = Response(
        df.to_csv(index=False),
        mimetype='text/csv', # content type
        headers={'Content-Disposition': 'attachment; filename=result.csv'}
    )
    return res


# Method 2:Convert to CSV for download in a directory and download that file using a link.
@app.route('/convert_csv_display', methods=['POST'])
def convert_to_csv_display():
    if 'filecsv' not in request.files:
        return "No file part in the request", 400
    file = request.files['filecsv']
    if file.filename == '':
        return "No file selected", 400
    df = pd.read_excel(file)

    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    filename= f'{uuid.uuid4()}.csv'
    
    df.to_csv(os.path.join('downloads', filename))
    # mimetype='text/csv', # content type
    # headers={'Content-Disposition': 'attachment; filename=result.csv'}
 
    return render_template('download.html', filename=filename)

# To download the converted csv file using the directory of that converted file.
@app.route('/download/<filename>')
def download(filename):
    print("klhjjlkghkjghjk")
    return send_from_directory('downloads', filename, download_name='dresult.csv')


# Handle json data using javascript and adding the json data in file.txt
@app.route('/handle_post_js', methods=['POST'])
def handle_post():
    greeting = request.json['greeting']
    name = request.json['name']

    with open('file.txt', 'w') as f:
        f.write(f'{greeting}, {name}')
    
    return jsonify({'message': 'Successfully Written !!!'})


if __name__ == "__main__":
    app.run(host="localhost", port=5500, debug=True)
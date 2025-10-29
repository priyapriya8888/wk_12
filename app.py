from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('myform.html')

@app.route('/submit', methods=['GET','POST'])
def submit():
    # Get data from the form
    username = request.form['username']
    return render_template('greeting.html', name=username)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port= 5000, debug = True)
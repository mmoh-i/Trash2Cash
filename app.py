from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle sign up logic
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    email = request.form['email']
    message = request.form['message']
    # Handle sending message logic (e.g., save to database, send email, etc.)
    print(f"Received message from {email}: {message}")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

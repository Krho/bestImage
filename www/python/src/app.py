from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
   return "Finding the best image of a Commons category"

@app.route('/category/<category>')
def show_user_profile(username):
    # show the user profile for that user
    return 'Best image of %s' % category

if __name__ == "__main__":
   app.run()


# main.py

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Stock Platform is running!"

if __name__ == "__main__":
    app.run(debug=True)
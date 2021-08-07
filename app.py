from flask import Flask
from pricefinder import run

app = Flask(__name__)

@app.route('/')
def check():
    details = run()
    return details

if __name__ == "__main__":
    app.run()


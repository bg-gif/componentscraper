from flask import Flask
import pricefinder as start


app = Flask(__name__)

@app.route('/')
def run():
    start
    return

if  __name__ == "__main__":
    app.run(port=8080)


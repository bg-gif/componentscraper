from flask import Flask, render_template
from flask_restful import Resource, Api, reqparse
import os
import pricefinder as scraper

app = Flask(__name__)
api = Api(app)

class Run(Resource):
    def get(self):
        results = scraper.run()
        return results, 200


class Hello(Resource):
    def get(self):
        return render_template(hello.html)


api.add_resource(Run, '/run')
api.add_resource(Hello, '/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))


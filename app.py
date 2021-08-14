from flask import Flask, render_template, make_response
from flask_restful import Resource, Api, reqparse
import os
import pricefinder as scraper

app = Flask(__name__)
api = Api(app)


class Run(Resource):
    def get(self):
        results = scraper.run()
        return make_response({'message': 'it ran', 'results': results}, 200)


class Hello(Resource):
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('hello.html'), 200, headers)


api.add_resource(Run, '/run')
api.add_resource(Hello, '/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

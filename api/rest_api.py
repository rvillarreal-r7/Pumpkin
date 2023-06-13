from flask import Flask
from flask_restful import Resource, Api

## Flask vars
app = Flask(__name__)
api = Api(app)

## Main Class
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

class DeviceInfo(Resource):
    def get(self):
        return {"asdf": "asdf"}

## Adds the API endpoint HelloWorld at the root
api.add_resource(HelloWorld, '/')
api.add_resource(DeviceInfo, '/device')

# ## main func
if __name__ == '__main__':
    app.run(debug=True)
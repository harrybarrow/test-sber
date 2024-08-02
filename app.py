from flask import Flask
from flask_restful import Api, Resource, reqparse
from formula import validate_and_return_params, ValidationError, deposit, date_to_str, rounded_float_or_int


class TestAPI(Resource):
    def get(self):  # noqa
        parser = reqparse.RequestParser()
        parser.add_argument('date').add_argument('periods').add_argument('amount').add_argument('rate')
        args = parser.parse_args()
        try:
            params = validate_and_return_params(args)
        except ValidationError as e:
            return {'error': str(e)}, 400
        return {date_to_str(date): rounded_float_or_int(amount) for date, amount in deposit(*params)}


app = Flask(__name__)
api = Api(app)
app.api_url = '/'
api.add_resource(TestAPI, app.api_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

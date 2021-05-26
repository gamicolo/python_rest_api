from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from datetime import datetime
import dateutil.parser as dp
import calendar
import pytz

app = Flask(__name__)
api = Api(app)

transactions={}
transactions_amount=0

transactions_post_args = reqparse.RequestParser()

#transactions_post_args.add_argument("amount", type=str, help="", required=True)
#transactions_post_args.add_argument("timestamp", type=str, help="", required=True)

transactions_post_args.add_argument("amount", type=str, help="")
transactions_post_args.add_argument("timestamp", type=str, help="")

def get_delta_time(utc_str):
    tx_ts = iso2unix(utc_str)
    utc_now = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
    curr_ts = iso2unix(utc_now.isoformat('T'))
    #print(tx_ts)
    #print(curr_ts)
    return (curr_ts - tx_ts)

def iso2unix(utc_str):
    parsed_t = dp.parse(utc_str)
    return calendar.timegm(parsed_t.timetuple())

class Transactions(Resource):

    def get(self):
        total_tx = []
        global transactions
        for k in transactions.keys():
            total_tx.append({'amount':transactions[k]['amount'],'timestamp':k})

        #return [{'amount':transactions['amount'],'timestamp':transactions['timestamp']}],200
        return total_tx,200

    def post(self):
        global transactions
        global transactions_amount

        args = transactions_post_args.parse_args()
        
        #422 campos del body no pueden ser parseados (no existe o es del tipo invalido)
        if not(args['amount']) or not(type(args['amount']) == str):
            print('amount is None or not type str')
            return {},422
        if not(args['timestamp']) or not(type(args['amount']) == str):
            #TODO: agregar validacion del tipo de dato (que sea timestamp UTC)
            print('timestamp is None or not type str')
            return {},422

        delta = get_delta_time(args['timestamp'])

        #422 transaccion con TS mayor al UTC actual
        if (delta < 0):
            return {},422

        #400 json invalido
        #TODO: validar el json

        #204 tx es anterior a 60 segundos
        if (delta > 60):
            return {},204

        #201 exito
        transactions_amount = transactions_amount + int(args['amount'])
        transactions.update({args['timestamp']:{'amount': transactions_amount}})
        return {},201

    def delete(self):
        global transactions
        global transactions_amount
        transactions = {}
        transactions_amount = 0
        return 204

class Statistics(Resource):
    def get(self):
        return {}

api.add_resource(Transactions, "/transactions")
api.add_resource(Statistics, "/statistics")

if __name__ == "__main__":
    app.run(debug=True)

#!/usr/bin/python3
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from datetime import datetime
import dateutil.parser as dp
import calendar
import pytz
import math
import logging

logging.basicConfig(filename='real_time_stats.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s')

logger = logging.getLogger('real_time_stats')

app = Flask(__name__)
api = Api(app)

transactions={}

transactions_post_args = reqparse.RequestParser()

transactions_post_args.add_argument("amount", type=str, help="")
transactions_post_args.add_argument("timestamp", type=str, help="")

def get_current_timestamp_utc():
    utc_now = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
    return iso2unix(utc_now.isoformat('T'))

def iso2unix(timestamp):
    parsed_t = dp.parse(timestamp)
    return calendar.timegm(parsed_t.timetuple())

def get_transactions(transactions):
    #make a local copy of the transactions dict to iterate over and not be affected when remove values older than 60 secs
    local_transactions = dict(transactions)
    result = []
    current_timestamp = get_current_timestamp_utc()
    logger.debug('The current timestamp is: %s' % current_timestamp)
    for timestamp in local_transactions.keys():
        logger.debug('The timestamp key in transactions dict is: %s' % timestamp)
        if (current_timestamp - timestamp) < 60:
            result.append(local_transactions[timestamp])
        else:
            #remove old values from the original and not the copy
            logger.debug('Removing timestamp key %s from transactions dict (older than 60 sec)' % timestamp)
            transactions.pop(timestamp)
    return result

def get_statistics(transactions):
    local_transactions = dict(transactions)
    statistics = {'sum': 0, 'avg': 0, 'max': 0, 'min': 0, 'p90': 0, 'count': 0}
    current_timestamp = get_current_timestamp_utc()
    logger.debug('The current timestamp is: %s' % current_timestamp)
    amount_list=[]
    for timestamp in local_transactions.keys():
        logger.debug('The timestamp key in transactions dict is: %s' % timestamp)
        if (current_timestamp - timestamp) < 60:
            statistics['sum'] += int(local_transactions[timestamp]['amount'])
            if (int(local_transactions[timestamp]['amount']) > statistics['max']):
                statistics['max']=int(local_transactions[timestamp]['amount'])
            if (statistics['min'] == 0):
                statistics['min']=int(local_transactions[timestamp]['amount'])
            if (int(local_transactions[timestamp]['amount']) < statistics['min']):
                statistics['min']=int(local_transactions[timestamp]['amount'])
            statistics['count'] += 1
            amount_list.append(int(local_transactions[timestamp]['amount']))
        else:
            #remove old values from the original and not the copy
            logger.debug('Removing timestamp key %s from transactions dict (older than 60 sec)' % timestamp)
            transactions.pop(timestamp)
    if (statistics['count'] > 0):
        statistics['avg'] = statistics['sum']/statistics['count']
    if amount_list:
        statistics['p90']=get_percentile(90, amount_list)
    return statistics

def get_percentile(percentile, samples = []):

    if not(len(samples) > 0):
        return samples
    samples.sort()
    p_index = math.ceil((len(samples)-1)*(percentile/100))
    return samples[p_index]

class Transactions(Resource):

    def get(self):
        global transactions
        result = get_transactions(transactions)
        return result,200

    def post(self):
        global transactions

        args = transactions_post_args.parse_args()
        
        #422 body fields cannot be parsed (non exists or invalid type)
        if not(args['amount']) or not(type(args['amount']) == str):
            logger.error('amount is None or not type str')
            return {},422
        if not(args['timestamp']) or not(type(args['amount']) == str):
            logger.error('timestamp is None or not type str')
            return {},422

        tx_ts = iso2unix(args['timestamp'])

        delta = get_current_timestamp_utc() - tx_ts

        #422 transaccion con TS mayor al UTC actual
        if (delta < 0):
            return {},422

        #400 json invalido
        #TODO: implement 

        #204 transactions older than 60 secs
        if (delta > 60):
            return {},204

        #201 exito
        transactions.update({tx_ts:{'amount':args['amount'],'timestamp':args['timestamp']}})
        print(transactions)
        return {},201

    def delete(self):
        global transactions
        global transactions_amount
        transactions = {}
        transactions_amount = 0
        return 204

class Statistics(Resource):

    def get(self):
        global transactions
        result = get_statistics(transactions)
        return result,200

api.add_resource(Transactions, "/transactions")
api.add_resource(Statistics, "/statistics")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

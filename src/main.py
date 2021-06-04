#!/usr/bin/python3
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from datetime import datetime
import dateutil.parser as dp
import calendar
import pytz
import math
import logging
from multiprocessing import Manager, Lock

#logging.basicConfig(level=logging.DEBUG, filename='real_time_stats.log', filemode='w', format='%(asctime)s %(name)s %(levelname)s %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('real_time_stats')

app = Flask(__name__)
api = Api(app)

shared_transactions = Manager().dict()
lock = Lock()

transactions_post_args = reqparse.RequestParser()

transactions_post_args.add_argument("amount", type=str, help="")
transactions_post_args.add_argument("timestamp", type=str, help="")

def get_current_timestamp_utc():
    utc_now = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
    return iso2unix(utc_now.isoformat('T'))

def iso2unix(timestamp):
    parsed_t = dp.parse(timestamp)
    return calendar.timegm(parsed_t.timetuple())

def post_transaction(transactions,amount,timestamp,lock):

    #422 body fields cannot be parsed (non exists or invalid type)
    if not amount or not(type(amount) == str):
        logger.error('amount is None or not type str')
        return 422
    if not timestamp or not(type(amount) == str):
        logger.error('timestamp is None or not type str')
        return 422

    unix = iso2unix(timestamp)

    delta = get_current_timestamp_utc() - unix

    logger.debug('The difference between the iso timestamp from transaction and current utc timestamp is: %s' % delta)

    #422 transaction with TS greather than current UTC timestamp
    if (delta < 0):
        return 422

    #400 invalid json
    #TODO: implement 

    #204 transactions older than 60 secs
    if (delta > 60):
        return 204

    #201 success
    with lock:
        transactions.update({timestamp:{'amount':amount,'timestamp':timestamp,'utimestamp':unix}})
        logger.debug('Adding iso timestamp key %s to transactions dict' % timestamp)
    return 201

def get_transactions(transactions,lock):
    result = []
    current_utimestamp = get_current_timestamp_utc()
    logger.debug('The current utc unix timestamp is: %s' % current_utimestamp)
    with lock:
        #make a local copy of the transactions dict to iterate over and not be affected when remove values older than 60 secs
        local_transactions = dict(transactions)
        for k in local_transactions.keys():
            utimestamp = local_transactions[k]['utimestamp']
            logger.debug('The unix timestamp in transactions dict is: %s' % utimestamp)
            if (current_utimestamp - utimestamp) < 60:
                result.append({'amount':local_transactions[k]['amount'],'timestamp': local_transactions[k]['timestamp']})
            else:
                #remove old values from the original and not the copy
                logger.info('Removing iso timestamp key %s from transactions dict (older than 60 sec)' % k)
                transactions.pop(k)
    return result

def get_statistics(transactions,lock):
    statistics = {'sum': 0, 'avg': 0, 'max': 0, 'min': 0, 'p90': 0, 'count': 0}
    current_utimestamp = get_current_timestamp_utc()
    logger.debug('The current utc unix timestamp is: %s' % current_utimestamp)
    amount_list=[]
    with lock:
        local_transactions = dict(transactions)
        for k in local_transactions.keys():
            utimestamp = local_transactions[k]['utimestamp']
            logger.debug('The unix timestamp in transactions dict is: %s' % utimestamp)

            if (current_utimestamp - utimestamp) < 60:
                statistics['sum'] += int(local_transactions[k]['amount'])
                if (int(local_transactions[k]['amount']) > statistics['max']):
                    statistics['max']=int(local_transactions[k]['amount'])
                if (statistics['min'] == 0):
                    statistics['min']=int(local_transactions[k]['amount'])
                if (int(local_transactions[k]['amount']) < statistics['min']):
                    statistics['min']=int(local_transactions[k]['amount'])
                statistics['count'] += 1
                amount_list.append(int(local_transactions[k]['amount']))
            else:
                #remove old values from the original and not the copy
                logger.info('Removing iso timestamp key %s from transactions dict (older than 60 sec)' % k)
                transactions.pop(k)
    if (statistics['count'] > 0):
        statistics['avg'] = statistics['sum']/statistics['count']
    if amount_list:
        statistics['p90']=get_percentile(90, amount_list)
    #return statistics
    return { key:str(value) for key,value in statistics.items()}

def get_percentile(percentile, samples = []):

    if not(len(samples) > 0):
        return 0
    samples.sort()
    p_index = math.ceil((len(samples)-1)*(percentile/100))
    return samples[p_index]

class Transactions(Resource):

    def post(self):

        args = transactions_post_args.parse_args()
        r_code = post_transaction(shared_transactions,args['amount'],args['timestamp'],lock)
        return {},r_code

    def get(self):

        result = get_transactions(shared_transactions,lock)
        return result,200

    def delete(self):

        shared_transactions.clear()
        return 204

class Statistics(Resource):

    def get(self):

        result = get_statistics(shared_transactions,lock)
        return result,200

api.add_resource(Transactions, "/transactions")
api.add_resource(Statistics, "/statistics")

if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000)

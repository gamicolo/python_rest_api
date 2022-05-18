#!/usr/bin/python3
from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from datetime import datetime
import dateutil.parser as dp
import calendar
import pytz
import math
import logging

from multiprocessing import Process, Manager, Lock, Pool, current_process

#logging.basicConfig(level=logging.DEBUG, filename='real_time_stats.log', filemode='w', format='%(asctime)s %(name)s %(levelname)s %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)s %(levelname)s %(message)s')

logger = logging.getLogger('real_time_stats')

app = Flask(__name__)
api = Api(app)

shared_transactions = Manager().dict()

lock = Lock()

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

def post_transaction(transactions,amount,timestamp):

    #args = transactions_post_args.parse_args()
    
    #timestamp = args['timestamp']
    #amount = args['amount']

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

    #422 transaccion con TS mayor al UTC actual
    if (delta < 0):
        return 422

    #400 json invalido
    #TODO: implement 

    #204 transactions older than 60 secs
    if (delta > 60):
        return 204

    #201 exito
    transactions.update({timestamp:{'amount':amount,'timestamp':timestamp,'utimestamp':unix}})
    shared_transactions.update({timestamp:{'amount':amount,'timestamp':timestamp,'utimestamp':unix}})
    logger.debug('Adding iso timestamp key %s to transactions dict' % timestamp)
    return 201

def get_transactions(transactions):
    #make a local copy of the transactions dict to iterate over and not be affected when remove values older than 60 secs
    local_transactions = dict(transactions)
    result = []
    current_utimestamp = get_current_timestamp_utc()
    logger.debug('The current utc unix timestamp is: %s' % current_utimestamp)
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

def get_mp_transactions_lock(shared_transactions,lock):
    #make a local copy of the transactions dict to iterate over and not be affected when remove values older than 60 secs
    local_transactions = dict(shared_transactions)
    result = []
    current_utimestamp = get_current_timestamp_utc()
    with lock:
        for k in local_transactions.keys():
            utimestamp = local_transactions[k]['utimestamp']
            #print(timestamp)
            #print(current_timestamp)
            if (current_utimestamp - utimestamp) < 60:
                result.append({'amount':local_transactions[k]['amount'],'timestamp': local_transactions[k]['timestamp']})
            else:
                #remove old values from the original and not the copy
                shared_transactions.pop(k)
    return result

def get_mp_statistics_lock(shared_transactions,lock):
    statistics = {'sum': 0, 'avg': 0, 'max': 0, 'min': 0, 'p90': 0, 'count': 0}
    current_utimestamp = get_current_timestamp_utc()
    amount_list=[]
    with lock:
        local_transactions = dict(shared_transactions)
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
                shared_transactions.pop(k)
        if (statistics['count'] > 0):
            statistics['avg'] = statistics['sum']/statistics['count']
        if amount_list:
            statistics['p90']=get_percentile(90, amount_list)
        #return statistics
        return { key:str(value) for key,value in statistics.items()}

def get_statistics(transactions):
    local_transactions = dict(transactions)
    statistics = {'sum': 0, 'avg': 0, 'max': 0, 'min': 0, 'p90': 0, 'count': 0}
    current_utimestamp = get_current_timestamp_utc()
    logger.debug('The current utc unix timestamp is: %s' % current_utimestamp)
    amount_list=[]
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

    def get(self):

        global transactions
        result = get_transactions(transactions)

        result_mp = get_mp_transactions_lock(shared_transactions,lock)

        print ("result old: %s" % result)
        print ("result new: %s" % result_mp)

        #return result,200
        #return list(result_mp),200
        return result_mp,200

    def post(self):

        global transactions
        #r_code = post_transaction(shared_transactions)
        #r_code = post_transaction(transactions)
        args = transactions_post_args.parse_args()
        r_code = post_transaction(transactions,args['amount'],args['timestamp'])

        return {},201

    def delete(self):
        shared_transactions.clear()
        return 204

class Statistics(Resource):

    def get(self):
        global transactions
        result = get_statistics(transactions)
        result_mp = get_mp_statistics_lock(shared_transactions,lock)
        print ("result old: %s" % result)
        print ("result new: %s" % result_mp)
        return result_mp,200

api.add_resource(Transactions, "/transactions")
api.add_resource(Statistics, "/statistics")

if __name__ == "__main__":
    app.run(process=4)
    #app.run(debug=True)
    #_pool = Pool(processes=2)
    #try:
    #    app.run(debug=True)
    #except KeyboardInterrupt:
    #    _pool.close()
    #    _pool_joint()

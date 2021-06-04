#!/usr/bin/python3

import unittest
from unittest import mock
import sys
sys.path.append('../src')
from main import iso2unix,get_current_timestamp_utc,get_transactions,get_statistics,post_transaction
from datetime import datetime, timedelta
import pytz

class TestPostTransaction(unittest.TestCase):

    def setUp(self):

        self.now = datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
        self.lock = mock.MagicMock()

    def test_post_success(self):

        u = get_current_timestamp_utc()
        k = self.now.isoformat('T')
        a = '1'
        t = {'amount': a, 'timestamp': k, 'utimestamp': u}
        r = {'amount': a, 'timestamp': k}
        transactions = {k: t}

        code = post_transaction(transactions,a,k,self.lock)

        self.assertEqual(code,201)

    def test_post_amount_empty(self):

        u = get_current_timestamp_utc()
        k = self.now.isoformat('T')
        a = None
        t = {'amount': a, 'timestamp': k, 'utimestamp': u}
        r = {'amount': a, 'timestamp': k}
        transactions = {k: t}

        code = post_transaction(transactions,a,k,self.lock)

        self.assertEqual(code,422)

    def test_post_timestamp_empty(self):

        u = get_current_timestamp_utc()
        k = None
        a = '1'
        t = {'amount': a, 'timestamp': k, 'utimestamp': u}
        r = {'amount': a, 'timestamp': k}
        transactions = {k: t}

        code = post_transaction(transactions,a,k,self.lock)

        self.assertEqual(code,422)

    def test_post_amount_int_type(self):

        u = get_current_timestamp_utc()
        k = self.now.isoformat('T')
        a = 1
        t = {'amount': a, 'timestamp': k, 'utimestamp': u}
        r = {'amount': a, 'timestamp': k}
        transactions = {k: t}

        code = post_transaction(transactions,a,k,self.lock)

        self.assertEqual(code,422)

    def test_post_timestamp_int_type(self):

        u = get_current_timestamp_utc()
        k = 0
        a = '1'
        t = {'amount': a, 'timestamp': k, 'utimestamp': u}
        r = {'amount': a, 'timestamp': k}
        transactions = {k: t}

        code = post_transaction(transactions,a,k,self.lock)

        self.assertEqual(code,422)

    def test_post_timestamp_greather_than_utc(self):

        u = get_current_timestamp_utc()
        k = (self.now + timedelta(hours = 1)).isoformat('T')
        a = '1'
        t = {'amount': a, 'timestamp': k, 'utimestamp': u}
        r = {'amount': a, 'timestamp': k}
        transactions = {k: t}

        code = post_transaction(transactions,a,k,self.lock)

        self.assertEqual(code,422)

    def test_post_timestamp_less_than_sixty_secs(self):

        u = get_current_timestamp_utc()
        k = (self.now - timedelta(seconds = 61)).isoformat('T')
        a = '1'
        t = {'amount': a, 'timestamp': k, 'utimestamp': u}
        r = {'amount': a, 'timestamp': k}
        transactions = {k: t}

        code = post_transaction(transactions,a,k,self.lock)

        self.assertEqual(code,204)

    def test_post_invalid_json(self):

        u = get_current_timestamp_utc()
        k = (self.now - timedelta(seconds = 61)).isoformat('T')
        a = '1'
        t = {'amount': a, 'timestamp': k, 'utimestamp': u}
        r = {'amount': a, 'timestamp': k}
        transactions = {k: t}

        code = post_transaction({'amount'},a,k,self.lock)

        self.assertEqual(code,204)

class TestGetTransactions(unittest.TestCase):

    def setUp(self):

        self.lock = mock.MagicMock()

    def test_transactions_empty(self):

        transactions = {}

        result = get_transactions(transactions,self.lock)

        self.assertEqual(result,[])

    def test_transactions_not_empty(self):

        u = get_current_timestamp_utc()
        transactions = {'2018-07-17T09:59:51.312Z':{'amount': '1', 'timestamp': '2018-07-17T09:59:51.312Z','utimestamp':u}}

        result = get_transactions(transactions,self.lock)

        self.assertNotEqual(result,[])

    def test_transactions_one_tx_one_result(self):

        u = get_current_timestamp_utc()
        k = '2018-07-17T09:59:51.312Z'
        tx = {'amount': '1', 'timestamp': k, 'utimestamp': u}
        t_result = {'amount': '1', 'timestamp': k}
        transactions = {k: tx}

        result = get_transactions(transactions,self.lock)

        self.assertEqual(result,[t_result])

    def test_transactions_one_tx_none_result(self):

        u = get_current_timestamp_utc() - 60
        k = '2018-07-17T09:59:51.312Z'
        tx = {'amount': '1', 'timestamp': u, 'utimestamp': u}
        transactions = {k: tx}

        result = get_transactions(transactions,self.lock)

        self.assertEqual(result,[])

    def test_transactions_several_tx_one_result(self):

        u1 = get_current_timestamp_utc() - 10
        k1 = '2021-06-01T10:00:00.000Z'
        t1 = {'amount': '1', 'timestamp': k1, 'utimestamp': u1}
        r1 = {'amount': '1', 'timestamp': k1}
        u2 = get_current_timestamp_utc() - 70
        k2 = '2021-06-01T11:00:00.000Z'
        t2 = {'amount': '2', 'timestamp': k2, 'utimestamp': u2}
        r2 = {'amount': '2', 'timestamp': k2}
        u3 = get_current_timestamp_utc() - 65
        k3 = '2021-06-01T12:00:00.000Z'
        r3 = {'amount': '3', 'timestamp': k3}
        t3 = {'amount': '3', 'timestamp': k3, 'utimestamp': u3}

        transactions = {k1: t1, k2: t2, k3: t3}

        result = get_transactions(transactions,self.lock)

        self.assertEqual(result,[r1])

class TestGetStatistics(unittest.TestCase):

    def setUp(self):

        self.lock = mock.MagicMock()

    def test_statistics_empty(self):

        u1 = get_current_timestamp_utc() - 80
        k1 = '2021-06-01T10:00:00.000Z'
        t1 = {'amount': '10', 'timestamp': k1, 'utimestamp': u1}
        r1 = {'amount': '10', 'timestamp': k1}
        u2 = get_current_timestamp_utc() - 70
        k2 = '2021-06-01T11:00:00.000Z'
        t2 = {'amount': '10', 'timestamp': k2, 'utimestamp': u2}
        r2 = {'amount': '10', 'timestamp': k2}
        u3 = get_current_timestamp_utc() - 65
        k3 = '2021-06-01T12:00:00.000Z'
        r3 = {'amount': '10', 'timestamp': k3}
        t3 = {'amount': '10', 'timestamp': k3, 'utimestamp': u3}

        transactions = {k1: t1, k2: t2, k3: t3}

        result = get_statistics(transactions,self.lock)

        self.assertEqual(result,{'sum': '0', 'avg': '0', 'max': '0', 'min': '0', 'p90': '0', 'count': '0'})

    def test_statistics_not_empty(self):

        u1 = get_current_timestamp_utc() - 10
        k1 = '2021-06-01T10:00:00.000Z'
        t1 = {'amount': '5', 'timestamp': k1, 'utimestamp': u1}
        r1 = {'amount': '5', 'timestamp': k1}
        u2 = get_current_timestamp_utc() - 15
        k2 = '2021-06-01T11:00:00.000Z'
        t2 = {'amount': '30', 'timestamp': k2, 'utimestamp': u2}
        r2 = {'amount': '30', 'timestamp': k2}
        u3 = get_current_timestamp_utc() - 20
        k3 = '2021-06-01T12:00:00.000Z'
        r3 = {'amount': '25', 'timestamp': k3}
        t3 = {'amount': '25', 'timestamp': k3, 'utimestamp': u3}

        transactions = {k1: t1, k2: t2, k3: t3}
        
        result = get_statistics(transactions,self.lock)

        self.assertEqual(result,{'sum': '60', 'avg': '20.0', 'max': '30', 'min': '5', 'p90': '30', 'count': '3'})
        
    def test_statistics_only_two_valid_transactions(self):

        u1 = get_current_timestamp_utc() - 10
        k1 = '2021-06-01T10:00:00.000Z'
        t1 = {'amount': '10', 'timestamp': k1, 'utimestamp': u1}
        r1 = {'amount': '10', 'timestamp': k1}
        u2 = get_current_timestamp_utc() - 15
        k2 = '2021-06-01T11:00:00.000Z'
        t2 = {'amount': '30', 'timestamp': k2, 'utimestamp': u2}
        r2 = {'amount': '30', 'timestamp': k2}
        u3 = get_current_timestamp_utc() - 70
        k3 = '2021-06-01T12:00:00.000Z'
        r3 = {'amount': '10', 'timestamp': k3}
        t3 = {'amount': '10', 'timestamp': k3, 'utimestamp': u3}

        transactions = {k1: t1, k2: t2, k3: t3}
        
        result = get_statistics(transactions,self.lock)

        self.assertEqual(result,{'sum': '40', 'avg': '20.0', 'max': '30', 'min': '10', 'p90': '30', 'count': '2'})

class TestCheckStoredData(unittest.TestCase):

    def setUp(self):

        self.lock = mock.MagicMock()

    def test_statistics_check_transaction_stored_data(self):

        u1 = get_current_timestamp_utc() - 10
        k1 = '2021-06-01T10:00:00.000Z'
        t1 = {'amount': '10', 'timestamp': k1, 'utimestamp': u1}
        r1 = {'amount': '10', 'timestamp': k1}
        u2 = get_current_timestamp_utc() - 15
        k2 = '2021-06-01T11:00:00.000Z'
        t2 = {'amount': '30', 'timestamp': k2, 'utimestamp': u2}
        r2 = {'amount': '30', 'timestamp': k2}
        u3 = get_current_timestamp_utc() - 70
        k3 = '2021-06-01T12:00:00.000Z'
        r3 = {'amount': '10', 'timestamp': k3}
        t3 = {'amount': '10', 'timestamp': k3, 'utimestamp': u3}

        transactions = {k1: t1, k2: t2, k3: t3}

        result = get_statistics(transactions,self.lock)

        self.assertEqual(transactions,{k1: t1, k2: t2})

if __name__ == "__main__":

    unittest.main()

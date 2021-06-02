#!/usr/bin/python3

import unittest
import sys
sys.path.append('../src')
from main import iso2unix,get_current_timestamp_utc,get_transactions,get_statistics

class TestGetTransactions(unittest.TestCase):

    def test_transactions_empty(self):

        transactions = {}

        result = get_transactions(transactions)

        self.assertEqual(result,[])

    def test_transactions_not_empty(self):

        u = get_current_timestamp_utc()
        #transactions = {k:{'amount': '1', 'timestamp': '2018-07-17T09:59:51.312Z'}}
        transactions = {'2018-07-17T09:59:51.312Z':{'amount': '1', 'timestamp': '2018-07-17T09:59:51.312Z','utimestamp':u}}

        result = get_transactions(transactions)

        self.assertNotEqual(result,[])

    def test_transactions_one_tx_one_result(self):

        u = get_current_timestamp_utc()
        k = '2018-07-17T09:59:51.312Z'
        tx = {'amount': '1', 'timestamp': u, 'utimestamp': u}
        t_result = {'amount': '1', 'timestamp': u}
        transactions = {k: tx}

        result = get_transactions(transactions)

        self.assertEqual(result,[t_result])

    def test_transactions_one_tx_none_result(self):

        u = get_current_timestamp_utc() - 60
        k = '2018-07-17T09:59:51.312Z'
        tx = {'amount': '1', 'timestamp': u, 'utimestamp': u}
        transactions = {k: tx}

        result = get_transactions(transactions)

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

        result = get_transactions(transactions)

        self.assertEqual(result,[r1])

class TestGetStatistics(unittest.TestCase):

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

        #k1 = get_current_timestamp_utc() - 80
        #tx1 = {'amount': '10', 'timestamp': '2021-06-01T10:00:00.000Z'}
        #k2 = get_current_timestamp_utc() - 70
        #tx2 = {'amount': '10', 'timestamp': '2021-06-01T11:00:00.000Z'}
        #k3 = get_current_timestamp_utc() - 65
        #tx3 = {'amount': '10', 'timestamp': '2021-06-01T12:00:00.000Z'}

        #transactions = {k1: tx1, k2: tx2, k3: tx3}
        
        result = get_statistics(transactions)

        self.assertEqual(result,{'sum': 0, 'avg': 0, 'max': 0, 'min': 0, 'p90': 0, 'count': 0})

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

        #k1 = get_current_timestamp_utc() - 10
        #tx1 = {'amount': '5', 'timestamp': '2021-06-01T10:00:00.000Z'}
        #k2 = get_current_timestamp_utc() - 15
        #tx2 = {'amount': '30', 'timestamp': '2021-06-01T11:00:00.000Z'}
        #k3 = get_current_timestamp_utc() - 20
        #tx3 = {'amount': '25', 'timestamp': '2021-06-01T12:00:00.000Z'}

        #transactions = {k1: tx1, k2: tx2, k3: tx3}
        
        result = get_statistics(transactions)

        self.assertEqual(result,{'sum': 60, 'avg': 20, 'max': 30, 'min': 5, 'p90': 30, 'count': 3})
        
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

        #k1 = get_current_timestamp_utc() - 10
        #tx1 = {'amount': '10', 'timestamp': '2021-06-01T10:00:00.000Z'}
        #k2 = get_current_timestamp_utc() - 15
        #tx2 = {'amount': '30', 'timestamp': '2021-06-01T11:00:00.000Z'}
        #k3 = get_current_timestamp_utc() - 70
        #tx3 = {'amount': '10', 'timestamp': '2021-06-01T12:00:00.000Z'}

        #transactions = {k1: tx1, k2: tx2, k3: tx3}
        
        result = get_statistics(transactions)

        self.assertEqual(result,{'sum': 40, 'avg': 20, 'max': 30, 'min': 10, 'p90': 30, 'count': 2})

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

        #k1 = get_current_timestamp_utc() - 10
        #tx1 = {'amount': '10', 'timestamp': '2021-06-01T10:00:00.000Z'}
        #k2 = get_current_timestamp_utc() - 15
        #tx2 = {'amount': '30', 'timestamp': '2021-06-01T11:00:00.000Z'}
        #k3 = get_current_timestamp_utc() - 70
        #tx3 = {'amount': '10', 'timestamp': '2021-06-01T12:00:00.000Z'}

        #transactions = {k1: tx1, k2: tx2, k3: tx3}
        print(transactions)
        
        result = get_statistics(transactions)

        print(transactions)
        self.assertEqual(transactions,{k1: t1, k2: t2})

if __name__ == "__main__":

    unittest.main()

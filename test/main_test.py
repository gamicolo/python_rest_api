#!/usr/bin/python3

import unittest
import sys
sys.path.append('../src/app')
from main import iso2unix,get_current_timestamp_utc,get_transactions,get_statistics

class TestGetTransactions(unittest.TestCase):

    def test_transactions_empty(self):

        transactions = {}

        result = get_transactions(transactions)

        self.assertEqual(result,[])

    def test_transactions_not_empty(self):

        k = get_current_timestamp_utc()
        transactions = {k:{'amount': '1', 'timestamp': '2018-07-17T09:59:51.312Z'}}

        result = get_transactions(transactions)

        self.assertNotEqual(result,[])

    def test_transactions_one_tx_one_result(self):

        k = get_current_timestamp_utc()
        tx = {'amount': '1', 'timestamp': '2018-07-17T09:59:51.312Z'}
        transactions = {k: tx}

        result = get_transactions(transactions)

        self.assertEqual(result,[tx])

    def test_transactions_one_tx_none_result(self):

        k = get_current_timestamp_utc() - 60
        tx = {'amount': '1', 'timestamp': '2018-07-17T09:59:51.312Z'}
        transactions = {k: tx}

        result = get_transactions(transactions)

        self.assertEqual(result,[])

    def test_transactions_several_tx_one_result(self):

        k1 = get_current_timestamp_utc() - 10
        tx1 = {'amount': '1', 'timestamp': '2021-06-01T10:00:00.000Z'}
        k2 = get_current_timestamp_utc() - 70
        tx2 = {'amount': '2', 'timestamp': '2021-06-01T11:00:00.000Z'}
        k3 = get_current_timestamp_utc() - 65
        tx3 = {'amount': '3', 'timestamp': '2021-06-01T12:00:00.000Z'}

        transactions = {k1: tx1, k2: tx2, k3: tx3}

        result = get_transactions(transactions)

        self.assertEqual(result,[tx1])

class TestGetStatistics(unittest.TestCase):

    def test_statistics_empty(self):

        k1 = get_current_timestamp_utc() - 80
        tx1 = {'amount': '10', 'timestamp': '2021-06-01T10:00:00.000Z'}
        k2 = get_current_timestamp_utc() - 70
        tx2 = {'amount': '10', 'timestamp': '2021-06-01T11:00:00.000Z'}
        k3 = get_current_timestamp_utc() - 65
        tx3 = {'amount': '10', 'timestamp': '2021-06-01T12:00:00.000Z'}

        transactions = {k1: tx1, k2: tx2, k3: tx3}
        
        result = get_statistics(transactions)

        self.assertEqual(result,{'sum': 0, 'avg': 0, 'max': 0, 'min': 0, 'p90': 0, 'count': 0})

    def test_statistics_not_empty(self):

        k1 = get_current_timestamp_utc() - 10
        tx1 = {'amount': '5', 'timestamp': '2021-06-01T10:00:00.000Z'}
        k2 = get_current_timestamp_utc() - 15
        tx2 = {'amount': '30', 'timestamp': '2021-06-01T11:00:00.000Z'}
        k3 = get_current_timestamp_utc() - 20
        tx3 = {'amount': '25', 'timestamp': '2021-06-01T12:00:00.000Z'}

        transactions = {k1: tx1, k2: tx2, k3: tx3}
        
        result = get_statistics(transactions)

        self.assertEqual(result,{'sum': 60, 'avg': 20, 'max': 30, 'min': 5, 'p90': 30, 'count': 3})
        
    def test_statistics_only_two_valid_transactions(self):

        k1 = get_current_timestamp_utc() - 10
        tx1 = {'amount': '10', 'timestamp': '2021-06-01T10:00:00.000Z'}
        k2 = get_current_timestamp_utc() - 15
        tx2 = {'amount': '30', 'timestamp': '2021-06-01T11:00:00.000Z'}
        k3 = get_current_timestamp_utc() - 70
        tx3 = {'amount': '10', 'timestamp': '2021-06-01T12:00:00.000Z'}

        transactions = {k1: tx1, k2: tx2, k3: tx3}
        
        result = get_statistics(transactions)

        self.assertEqual(result,{'sum': 40, 'avg': 20, 'max': 30, 'min': 10, 'p90': 30, 'count': 2})

    def test_statistics_check_transaction_stored_data(self):

        k1 = get_current_timestamp_utc() - 10
        tx1 = {'amount': '10', 'timestamp': '2021-06-01T10:00:00.000Z'}
        k2 = get_current_timestamp_utc() - 15
        tx2 = {'amount': '30', 'timestamp': '2021-06-01T11:00:00.000Z'}
        k3 = get_current_timestamp_utc() - 70
        tx3 = {'amount': '10', 'timestamp': '2021-06-01T12:00:00.000Z'}

        transactions = {k1: tx1, k2: tx2, k3: tx3}
        print(transactions)
        
        result = get_statistics(transactions)

        print(transactions)
        self.assertEqual(transactions,{k1: tx1, k2: tx2})

if __name__ == "__main__":

    unittest.main()

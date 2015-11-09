#! /usr/bin/python
#-*- coding: utf-8 -*-

import es3
import requests
import unittest
import validators

class URLTester(unittest.TestCase):
    good_urls = []
    bad_urls = []

    @classmethod
    def setUpClass(cls):
        cls.good_urls = [
            (0, True, "http://www.google.com/"),
            (1, True, "http://www.yahoo.com/")
        ]

        cls.bad_urls = [
            (2, False, "http://pippo/"),
            (3, False, "BADURL")
        ]

    def test_read_urls_from_bad_file(self):
        """
        Deve fallire quando prende in input un file inesistente
        """
        self.assertRaises(IOError, es3.read_urls_from("BADFILE"))

    def test_test_urls_bad_input(self):
        """
        Deve sollevare ConnectionError
        """
        self.assertRaises(requests.exceptions.ConnectionError,
            es3.test_urls(self.bad_urls))

    def test_test_urls_good_input(self):
        """
        Deve ritornare None
        """
        self.assertIsNone(es3.test_urls(self.good_urls))

    def test_test_url_bad_input(self):
        """
        Deve sollevare ConnectionError
        """
        for url in self.bad_urls:
            self.assertRaises(requests.exceptions.ConnectionError,
                es3.test_url(url))

if __name__ == "__main__":
    unittest.main()

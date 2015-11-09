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
            (3, False, "https://this.is.not.a.real.url/")
        ]

        cls.missing_schemas = [
            (4, False, "BADURL"),
            (5, False, "google.com")
        ]

    def test_read_urls_from_bad_file(self):
        """
        Deve fallire quando prende in input un file inesistente
        """
        self.assertRaises(IOError, es3.read_urls_from, ("BADFILE"))

    def test_test_url_bad_input(self):
        """
        Deve sollevare ConnectionError
        """
        for url in self.bad_urls:
            self.assertRaises(requests.exceptions.ConnectionError,
                es3.test_url, (url[2]))

    def test_test_url_missing_schema(self):
        """
        Deve sollevare MissingSchema
        """
        for url in self.missing_schemas:
            self.assertRaises(requests.exceptions.MissingSchema,
                    es3.test_url, (url[2]))

if __name__ == "__main__":
    unittest.main()

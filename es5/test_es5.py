#! /usr/bin/python
#-*- coding:utf-8 -*-

import es5
import unittest

class UrlValidationTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid_urls = [
            "http://www.example.com/",
            "http://www.example.com",   # missing final /
            "https://www.example.com/", # https protocol
            "https://www.example.com",  # https, missing final /
            "http://example.com/",      # missing www
            "http://example.com",       # missing www, final /
            "https://example.com/",     # https, missing www
            "https://example.com",      # https, missing www, final /
        ]

        cls.invalid_urls = [
            "ftp://www.example.com/",
            "ftp://www.example.com",
            "ftp://example.com/",
            "ftp://example.com",
            "mailto://someone@example.com/",
            "mailto://someone@example.com",
            "file:///some/path/to/file.txt/",
            "file:///some/path/to/file.txt",
            "data:,some_data",
        ]

    def test_validate_good_urls(self):
        """
        Controlla che validate torni True per gli url validi
        """
        for url in self.valid_urls:
            self.assertTrue(es5.validate(url))

    def test_validate_bad_urls(self):
        """
        Controlla che validate torni False per gli url non validi
        """
        for url in self.invalid_urls:
            self.assertFalse(es5.validate(url))


if __name__ == "__main__":
    unittest.main()

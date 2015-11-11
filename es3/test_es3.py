#! /usr/bin/python
#-*- coding: utf-8 -*-

import es3
import inspect
import requests
import unittest
import validators

class URLTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good_urls = [
            (0, "http://www.google.com/"),
            (1, "http://www.yahoo.com/")
        ]

        cls.bad_urls = [
            (2, "http://pippo/"),
            (3, "https://this.is.not.a.real.url/")
        ]

        cls.missing_schemas = [
            (4, "BADURL"),
            (5, "google.com"),
            (6, "")
        ]

        cls.bad_resps = [None, "", [], (), 0]

    def test_test_url_bad_input(self):
        """
        Deve sollevare ConnectionError
        """
        for url in self.bad_urls:
            self.assertRaises(requests.exceptions.ConnectionError,
                es3.test_url, (url[1]))

    def test_test_url_missing_schema(self):
        """
        Deve sollevare MissingSchema
        """
        for url in self.missing_schemas:
            self.assertRaises(requests.exceptions.MissingSchema,
                    es3.test_url, (url[1]))

    def test_print_url_bad_resp(self):
       """
       Deve sollevare AttributeError quando resp non possiede status_code
       """
       for resp in self.bad_resps:
           self.assertRaises(AttributeError, es3.print_url, ("" , 0) , resp, 0)

    def test_print_url_bad_time(self):
        """
        Deve sollevare ValueError quando elapsed non può essere formattato
        come numero decimale
        """
        resp = requests.Response()
        resp.status_code = 200
        bad_formats = [None, "", [], ()]
        for elapsed in bad_formats:
            self.assertRaises(ValueError, es3.print_url,
                              ("", 0) , resp, elapsed)

    def test_print_status_bad_resp(self):
        """
        Deve sollevare AttributeError quando resp non possiede status_code
        """
        for resp in self.bad_resps:
            self.assertRaises(AttributeError, es3.print_status, resp, "")

    def test_write_xml_bad_index(self):
        """
        Deve sollevare IndexError quando le tuple in xml_data hanno meno di 5
        elementi
        """
        bad_data = [
            [()],
            [(1,)],
            [(1,"2")],
            [(1,"2",3)],
            [(1,"2",3,4)]
        ]
        for xml_data in bad_data:
            self.assertRaises(IndexError, es3.write_xml, "", xml_data)

    def test_make_xml_tuple_bad_resp(self):
        """
        Deve sollevare AttributeError quando resp non possiede il metodo json()
        o l'attributo status_code
        """
        for resp in self.bad_resps:
            self.assertRaises(AttributeError, es3.make_xml_tuple,
                              (0, ""), resp, 0)

if __name__ == "__main__":
    unittest.main()

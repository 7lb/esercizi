import datetime
import es2
import os
import unittest

class TestLogParser(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLogParser, self).__init__(*args, **kwargs)

        self.concat_expected_result = \
        [
        "2010-05-07 12:33:44,8 Error: a.txt"        ,
        "2010-05-07 12:33:45,8 Error: a.txt"        ,
        "2010-08-05 15:21:52,0 Not an error"        ,
        "2013-06-27 18:12:11,8 Error: a.txt"        ,
        "2008-10-11 19:21:22,8 Error: a.log"        ,
        "2009-01-10 11:00:01,8 Error: a.log"        ,
        "2010-08-05 15:21:52,0 Not an error"        ,
        "2012-08-15 13:12:11,8 Error: a.log"        ,
        "2015-05-07 12:33:44,8 Error: nested/a.txt" ,
        "2010-08-05 15:21:52,0 Not an error"        ,
        "2003-04-21 11:01:47,8 Error: nested/a.log" ,
        "2010-08-05 15:21:52,0 Not an error"        ,
        "2009-05-12 11:53:29,8 Error: nested/a.log"
        ]

        self.makeTupList_expected_result = \
        [
        (datetime.datetime(2010, 5, 7, 12, 33, 44), 8, 'Error: a.txt')        ,
        (datetime.datetime(2010, 5, 7, 12, 33, 45), 8, 'Error: a.txt')        ,
        (datetime.datetime(2013, 6, 27, 18, 12, 11), 8, 'Error: a.txt')       ,
        (datetime.datetime(2008, 10, 11, 19, 21, 22), 8, 'Error: a.log')      ,
        (datetime.datetime(2009, 1, 10, 11, 0, 1), 8, 'Error: a.log')         ,
        (datetime.datetime(2012, 8, 15, 13, 12, 11), 8, 'Error: a.log')       ,
        (datetime.datetime(2015, 5, 7, 12, 33, 44), 8, 'Error: nested/a.txt') ,
        (datetime.datetime(2003, 4, 21, 11, 1, 47), 8, 'Error: nested/a.log') ,
        (datetime.datetime(2009, 5, 12, 11, 53, 29), 8, 'Error: nested/a.log')
        ]

        self.sortLogs_expected_result = \
        [
        (datetime.datetime(2015, 5, 7, 12, 33, 44), 8, 'Error: nested/a.txt') ,
        (datetime.datetime(2013, 6, 27, 18, 12, 11), 8, 'Error: a.txt')       ,
        (datetime.datetime(2012, 8, 15, 13, 12, 11), 8, 'Error: a.log')       ,
        (datetime.datetime(2010, 5, 7, 12, 33, 45), 8, 'Error: a.txt')        ,
        (datetime.datetime(2010, 5, 7, 12, 33, 44), 8, 'Error: a.txt')        ,
        (datetime.datetime(2009, 5, 12, 11, 53, 29), 8, 'Error: nested/a.log'),
        (datetime.datetime(2009, 1, 10, 11, 0, 1), 8, 'Error: a.log')         ,
        (datetime.datetime(2008, 10, 11, 19, 21, 22), 8, 'Error: a.log')      ,
        (datetime.datetime(2003, 4, 21, 11, 1, 47), 8, 'Error: nested/a.log')
        ]

        self.path       = "./logs/testlogs/"
        self.valid_exts = ["txt", "log"]

    def testConcatLength(self):
        """
        Testa che la lettura e lo split dei file sia corretto
        """
        self.assertEqual(len(es2.concat(self.path, self.valid_exts)),
                len(self.concat_expected_result))

    def testConcatResult(self):
        """
        Testa che il risultato di concat sia corretto
        """
        self.assertEqual(es2.concat(self.path, self.valid_exts),
                self.concat_expected_result)

    def testMakeTupListLength(self):
        """
        Testa che la lunghezza della lista di tuple restituita da makeTupList
        sia corretta
        """
        self.assertEqual(len(self.makeTupList_expected_result),
                len(es2.makeTupList(self.concat_expected_result, "%Y-%m-%d %H:%M:%S")))

    def testMakeTupListResult(self):
        """
        Testa che il risultato di makeTupList sia corretto
        """
        self.assertEqual(self.makeTupList_expected_result,
                es2.makeTupList(self.concat_expected_result, "%Y-%m-%d %H:%M:%S"))

    def testSortLogs(self):
        """
        Controlla che i log vengano ordinati nel modo giusto
        """
        self.assertEqual(es2.sortLogs(self.makeTupList_expected_result),
                self.sortLogs_expected_result)

    def testMakeTupListSanityCheck(self):
        """
        Controlla che ogni tupla generata da makeTupList contenga davvero
        3 elementi di tipo (datetime, int, str)
        """
        tl = es2.makeTupList(self.concat_expected_result, "%Y-%m-%d %H:%M:%S")
        for t in tl:
            self.assertTrue(len(t) == 3)
            self.assertTrue(type(t[0]) == datetime.datetime)
            self.assertTrue(type(t[1]) == int)
            self.assertTrue(type(t[2]) == str)

if __name__ == "__main__":
    unittest.main()

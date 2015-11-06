import datetime
import es2
import os
import unittest

class TestLogParser(unittest.TestCase):

    log_files = []
    filter_file_0_expected_res = []
    concat_expected_res = []
    sortl_expected_res = []
    path = ""
    valid_exts = []

    @classmethod
    def setUpClass(cls):

        cls.current_dir = os.path.dirname(os.path.realpath(__file__))
        cls.path       = cls.current_dir + "/logs/testlogs/"
        cls.valid_exts = ["txt", "log"]

        cls.log_files = [
            cls.current_dir + "/logs/testlogs/a.txt",
            cls.current_dir + "/logs/testlogs/a.log",
            cls.current_dir + "/logs/testlogs/nested/a.txt",
            cls.current_dir + "/logs/testlogs/nested/a.log"
        ]

        cls.filter_file_0_expected_res = [
            (datetime.datetime(2010, 5, 7, 12, 33, 44), 8, 'Error: a.txt'),
            (datetime.datetime(2010, 5, 7, 12, 33, 45), 8, 'Error: a.txt'),
            (datetime.datetime(2013, 6, 27, 18, 12, 11), 8, 'Error: a.txt')
        ]

        cls.concat_expected_res = [
            (datetime.datetime(2010, 5, 7, 12, 33, 44), 8, 'Error: a.txt'),
            (datetime.datetime(2010, 5, 7, 12, 33, 45), 8, 'Error: a.txt'),
            (datetime.datetime(2013, 6, 27, 18, 12, 11), 8, 'Error: a.txt'),
            (datetime.datetime(2008, 10, 11, 19, 21, 22), 8, 'Error: a.log'),
            (datetime.datetime(2009, 1, 10, 11, 0, 1), 8, 'Error: a.log'),
            (datetime.datetime(2012, 8, 15, 13, 12, 11), 8, 'Error: a.log'),
            (datetime.datetime(2015, 5, 7, 12, 33, 44), 8, 'Error: nested/a.txt'),
            (datetime.datetime(2003, 4, 21, 11, 1, 47), 8, 'Error: nested/a.log'),
            (datetime.datetime(2009, 5, 12, 11, 53, 29), 8, 'Error: nested/a.log')
        ]

        cls.sortl_expected_res = [
            (datetime.datetime(2015, 5, 7, 12, 33, 44), 8, 'Error: nested/a.txt'),
            (datetime.datetime(2013, 6, 27, 18, 12, 11), 8, 'Error: a.txt'),
            (datetime.datetime(2012, 8, 15, 13, 12, 11), 8, 'Error: a.log'),
            (datetime.datetime(2010, 5, 7, 12, 33, 45), 8, 'Error: a.txt'),
            (datetime.datetime(2010, 5, 7, 12, 33, 44), 8, 'Error: a.txt'),
            (datetime.datetime(2009, 5, 12, 11, 53, 29), 8, 'Error: nested/a.log'),
            (datetime.datetime(2009, 1, 10, 11, 0, 1), 8, 'Error: a.log'),
            (datetime.datetime(2008, 10, 11, 19, 21, 22), 8, 'Error: a.log'),
            (datetime.datetime(2003, 4, 21, 11, 1, 47), 8, 'Error: nested/a.log')
        ]

    def test_list_files(self):
        """
        Verifica che tutti e solo i file giusti vengano selezionati per essere
        letti
        """
        self.assertEqual(es2.list_files(self.path, self.valid_exts),
                         self.log_files)

    def test_filter_file(self):
        """
        Verifica che i file vengano filtrati correttamente
        """
        self.assertEqual(es2.filter_file(self.log_files[0]),
                         self.filter_file_0_expected_res)

    def test_concat_length(self):
        """
        Verifica che la lettura e lo split dei file sia corretto
        """
        self.assertEqual(len(es2.concat(self.path, self.valid_exts)),
                         len(self.concat_expected_res))

    def test_concat_res(self):
        """
        Verifica che il risultato di concat sia corretto
        """
        self.assertEqual(es2.concat(self.path, self.valid_exts),
                         self.concat_expected_res)

    def test_sortl(self):
        """
        Verifica che i log vengano ordinati nel modo giusto
        """
        self.assertEqual(es2.sortl(self.concat_expected_res),
                         self.sortl_expected_res)

    def test_concat_sanity_check(self):
        """
        Verifica che ogni tupla generata da concat contenga davvero
        3 elementi di tipo (datetime, int, str)
        """
        tl = es2.concat(self.path, self.valid_exts)
        for t in tl:
            self.assertTrue(len(t) == 3)
            self.assertTrue(isinstance(t[0], datetime.datetime))
            self.assertTrue(isinstance(t[1], int))
            self.assertTrue(isinstance(t[2], basestring))

if __name__ == "__main__":
    unittest.main()

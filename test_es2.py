import datetime
import es2
import os
import unittest
import shutil

class TestLogParser(unittest.TestCase):
    def setUp(self):
        """
        Crea cartelle e file temporanei di mock-up
        """
        self.path           = "/home/zero/esercizi/es2logs/.tmpdir/"
        self.valid_exts     = ("txt", "log")
        self.mock_files     = ("ok.txt", "ok.log", "ignore.bmp", "ignore")
        self.mock_dirs      = ("dir1/", "dir2/", "folder/", "folder/nested/")

        os.mkdir(self.path)
        for d in self.mock_dirs:
            os.mkdir(self.path + d)
            for f in self.mock_files:
                with open(self.path + d + f, "w") as fd:
                    fd.write("2010-05-05 18:23:15,5 Error: Testing file %s\n" %
                            (self.path + d + f))

        self.txt = es2.concat(self.path, self.valid_exts).split("\n")[:-1]

    def tearDown(self):
        """
        Elimina cartelle e file di mock-up creati da setUp
        """
        shutil.rmtree(self.path)

    def testConcatLength(self):
        """
        Testa che il numero di file letti sia corretto contando il numero
        di file che dovrebbero essere letti secondo le estensioni valide e il
        numero di linee di testo che sono state concatenate (1 file == 1 rinea)
        """
        files_read = 0
        for f in self.mock_files:
            for e in self.valid_exts:
                if f.endswith(".%s" % e): files_read += 1
        self.assertEqual(len(self.txt), files_read * len(self.mock_dirs))

    def testMakeTupListLength(self):
        """
        Testa che la lunghezza della lista di tuple restituita da makeTupList
        sia corretta comparandola con il numero di linee di testo concatenate
        """
        self.assertEqual(len(self.txt),
                len(es2.makeTupList(self.txt, "%Y-%m-%d %H:%M:%S")))

    def testMakeTupListSanityCheck(self):
        """
        Controlla che ogni tupla generata da makeTupList contenga davvero
        3 elementi di tipo (datetime, int, str)
        """
        tl = es2.makeTupList(self.txt, "%Y-%m-%d %H:%M:%S")
        for t in tl:
            self.assertTrue(len(t) == 3)
            self.assertTrue(type(t[0]) == datetime.datetime)
            self.assertTrue(type(t[1]) == int)
            self.assertTrue(type(t[2]) == str)

if __name__ == "__main__":
    unittest.main()

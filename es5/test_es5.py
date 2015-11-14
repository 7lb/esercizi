#! /usr/bin/python2
#-*- coding:utf-8 -*-

import es5
import itertools
import unittest

class UrlValidating(unittest.TestCase):
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
            "http://",
            "https://",
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


class TagHandling(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dummy_html = \
            """<!DOCTYPE html>
            <html>
            <head>
                <link href="http://abs-link.com/res.css" rel="stylesheet">
                <link href = "/rel-link/res.css" rel = "stylesheet" type = "text/css" />
                <link rel="author" type = "text/css" href ="/rel-link/authors.txt" >
            </head>
            <body>
                <a href="http://abs-a/a.html">an anchor</a>
                <a href ='/rel-a/a.htm' >another anchor</a >
                <img src=http://abs-unquoted-img/img.png>
                <img width="100" src=/rel-unquoted/img.png />
                <img src = "/rel-img/img.png/" />
                <script src='/rel-script/s.js' type = text/javascript ></script>
                <script src = "https://abs-script/s.js" ></script>
            </body>
            </html>"""

        cls.interesting_tags = [
            ("link", ' href="http://abs-link.com/res.css" rel="stylesheet"'),
            ("link", ' href = "/rel-link/res.css" rel = "stylesheet" type = "text/css" /'),
            ("link", ' rel="author" type = "text/css" href ="/rel-link/authors.txt" '),
            ("a", ' href="http://abs-a/a.html"'),
            ("a", " href ='/rel-a/a.htm' "),
            ("img", " src=http://abs-unquoted-img/img.png"),
            ("img", ' width="100" src=/rel-unquoted/img.png /'),
            ("img", ' src = "/rel-img/img.png/" /'),
            ("script", " src='/rel-script/s.js' type = text/javascript "),
            ("script", ' src = "https://abs-script/s.js" '),
        ]

        cls.target_links = [
            "http://abs-link.com/res.css",
            "/rel-link/res.css",
            "/rel-link/authors.txt",
            "http://abs-a/a.html",
            '/rel-a/a.htm',
            "http://abs-unquoted-img/img.png",
            "/rel-unquoted/img.png",
            "/rel-img/img.png/",
            '/rel-script/s.js',
            "https://abs-script/s.js",
        ]

    def test_find_all_tags(self):
        """
        Controlla che find_all_tags trovi tutti i tag
        """
        self.assertEqual(es5.find_all_tags(self.dummy_html),
                self.interesting_tags)

    def test_find_all_tags_order(self):
        """
        Controlla che, comunque specificato l'ordine dei tag da cercare, il
        risultato sia lo stesso

        Usare cautela nello specificare più di 7 tag (richiede ~1s con 7 tag,
        quasi 10s con 8, quasi 90s con 9)
        """
        tag_list = ["a", "img", "link", "script"]
        for  perm in itertools.permutations(tag_list):
            self.assertEqual(es5.find_all_tags(self.dummy_html, list(perm)),
                    self.interesting_tags)

    def test_isolate_links(self):
        """
        Controlla che i link vengano isolati correttamente
        """
        self.assertEqual(es5.isolate_links(self.interesting_tags),
                self.target_links)


class LinkFiltering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.invalid_links = [
            "#anchor_inside_page",
            "strange-scheme://something.com/path/file.ext",
            None,
        ]

        cls.valid_links = [
            "/relative/path/to/file.ext",
            "http://absolute-path/to/file.ext",
            "https://secure/connection",
        ]

        cls.main_url = "https://en.wikipedia.org/wiki/Main_Page"

        cls.rel_links = [
            "/w/api.php?action=featuredfeed&amp;feed=potd&amp;feedformat=atom",
            "/w/api.php?action=featuredfeed&amp;feed=featured&amp;feedformat=atom",
            "/w/api.php?action=featuredfeed&amp;feed=onthisday&amp;feedformat=atom",
            "/static/apple-touch/wikipedia.png",
            "/static/favicon/wikipedia.ico",
            "/w/opensearch_desc.php",
            "/w/index.php?title=Special:RecentChanges&amp;feed=atom",
            "/wiki/Wikipedia",
            "/wiki/Free_content",
            "/wiki/Encyclopedia",
            "/wiki/Wikipedia:Introduction",
            "/wiki/Special:Statistics",
            "/wiki/English_language",
            "/wiki/Harris%27s_List_of_Covent_Garden_Ladies",
            "/wiki/Rhodesia%27s_Unilateral_Declaration_of_Independence",
            "/wiki/1975_Australian_constitutional_crisis",
            "/wiki/Wikipedia:Today%27s_featured_article/November_2015",
            "/wiki/Wikipedia:Featured_articles",
            "/wiki/File:Nahem_Shoa_next_to_his_Giant_Portrait_of_Ben,_Hartlepool_Art_Gallery.jpg",
            "/wiki/Nahem_Shoa",
        ]

        cls.abs_links = [
            "https://en.wikipedia.org/w/api.php?action=rsd",
            "https://creativecommons.org/licenses/by-sa/3.0/",
            "https://en.wikipedia.org/wiki/Main_Page",
            "https://meta.wikimedia.org",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Gay_nov_20_1992_2115Z.jpg/120px-Gay_nov_20_1992_2115Z.jpg",
            "https://lists.wikimedia.org/mailman/listinfo/daily-article-l",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Nahem_Shoa_next_to_his_Giant_Portrait_of_Ben%2C_Hartlepool_Art_Gallery.jpg/100px-Nahem_Shoa_next_to_his_Giant_Portrait_of_Ben%2C_Hartlepool_Art_Gallery.jpg",
        ]

        cls.relativizable_links = [
            "https://en.wikipedia.org/w/api.php?action=rsd",
            "https://en.wikipedia.org/wiki/Main_Page",
        ]

        cls.non_relativizable_links = [
            "https://creativecommons.org/licenses/by-sa/3.0/",
            "https://meta.wikimedia.org",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Gay_nov_20_1992_2115Z.jpg/120px-Gay_nov_20_1992_2115Z.jpg",
            "https://lists.wikimedia.org/mailman/listinfo/daily-article-l"
        ]

    def test_link_filter(self):
        """
        Controlla che la funzione di link filtering funzioni correttamente
        """
        for link in self.invalid_links:
            self.assertFalse(es5.link_filter(link))

        for link in self.valid_links:
            self.assertTrue(es5.link_filter(link))

    def test_is_relative(self):
        """
        Deve tornare true per i link relativi e false per quelli assoluti
        """
        for link in self.rel_links:
            self.assertTrue(es5.is_relative_link(link))

        for link in self.abs_links:
            self.assertFalse(es5.is_relative_link(link))

    def test_can_be_relative(self):
        """
        Deve tornare true per i link assoluti che sono relativizzabili per
        "https://en.wikipedia.org/", false per quelli che non lo sono
        """
        url = "https://en.wikipedia.org/"
        for link in self.relativizable_links:
            self.assertTrue(es5.can_be_relative(link, url))
        for link in self.non_relativizable_links:
            self.assertFalse(es5.can_be_relative(link, url))


if __name__ == "__main__":
    unittest.main()

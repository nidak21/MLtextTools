#!/usr/bin/env python3

import unittest
from MLsciLitText import *

"""
These are tests for MLsciLitText.py

Usage:   python test_MLsciLitText.py [-v]
"""
######################################

class Paragraphs_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_paragraphsNullTest(self):
        paraBnd = '\n\n'
        # paragraphs w/ ending paraBnd
        text = paraBnd.join(['Para one. ', 'Para two.', ]) + paraBnd
        paras = list(paragraphs(text))
        #print()
        #print("'%s'" % text)
        #print(paras)
        self.assertEqual(len(paras), 2)
        self.assertEqual(paras[0], 'Para one.')
        self.assertEqual(paras[1], 'Para two.')

        # paragraphs w/o ending paraBnd
        text = paraBnd.join(['Para one. ', 'Para two.', ])
        paras = list(paragraphs(text))
        self.assertEqual(len(paras), 2)
        self.assertEqual(paras[1], 'Para two.')

        # paragraphs w/ some empty paragraphs to skip
        text = paraBnd.join(['', ' ', 'Para one.', '\n', 'Para two.', '' ])
        paras = list(paragraphs(text))
        self.assertEqual(len(paras), 2)
        self.assertEqual(paras[1], 'Para two.')

        # single paragraph, no boundary
        text = 'Para one.'
        paras = list(paragraphs(text))
        self.assertEqual(len(paras), 1)
        self.assertEqual(paras[0], 'Para one.')

        # empty string
        text = ''
        paras = list(paragraphs(text))
        self.assertEqual(len(paras), 0)

        # empty paragraph
        text = paraBnd
        paras = list(paragraphs(text))
        self.assertEqual(len(paras), 0)

    def test_paragraphsWithAltParaBnd(self):
        paraBnd = r'\par;'
        # paragraphs w/ ending paraBnd
        text = paraBnd.join(['Para one.', '',  'Para two.', '' ]) + paraBnd
        paras = list(paragraphs(text, paraBnd=paraBnd))
        self.assertEqual(len(paras), 2)
        self.assertEqual(paras[1], 'Para two.')


# end class Paragraphs_tests
######################################

if __name__ == '__main__':
    unittest.main()

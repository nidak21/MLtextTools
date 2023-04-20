#!/usr/bin/env python3

import unittest
from MLsciLitText import *

"""
These are tests for MLsciLitText.py

Usage:   python test_MLsciLitText.py [-v]
"""

class Paragraphs_tests(unittest.TestCase):
    def setUp(self):
        pass

    def test_paragraphs_NullTest(self):
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

    def test_paragraphs_WithAltParaBnd(self):
        paraBnd = r'\par;'
        # paragraphs w/ ending paraBnd
        text = paraBnd.join(['Para one.', '',  'Para two.', '' ]) + paraBnd
        paras = list(paragraphs(text, paraBnd=paraBnd))
        self.assertEqual(len(paras), 2)
        self.assertEqual(paras[1], 'Para two.')

# end class Paragraphs_tests ---------------------------------

class Legends_tests(unittest.TestCase):

    def test_legends_NullTest(self):
        paraBnd = '\n\n'
        text = paraBnd.join(['Figure 1 blah. ',
                            'Non figure paragraph',
                            'Non table legend paragraph',
                            '',
                            ' ',
                            paraBnd, 
                            'F i g u re 2 blah.\nSecond line.\n',
                            ]) + paraBnd
        legs = list(legends(text, paraBnd=paraBnd))
        self.assertEqual(len(legs), 2)
        self.assertTrue(legs[0].endswith('blah.'))
        self.assertTrue(legs[1].startswith('F i g u re 2'))

    def test_legends_ValidBeginnings(self):
        paraBnd = '\n\n'
        text = paraBnd.join(['Figure 1 blah. ',
                            'figure 2.',
                            'fig 3.',
                            'f i g. 4',
                            'table 5.',
                            'TABLE. 6.',
                            'TA Bl E: 7',
                            'Supp lem ental Data Figure 8.',
                            'On LINE table 9.',
                            ' Extended data FIG. 10.',
                            'Supplemental Info Figure 11.',
                            ])
        legs = list(legends(text, paraBnd=paraBnd))
        self.assertEqual(len(legs), 11)

# end class Legends_tests ----------------------------------

if __name__ == '__main__':
    unittest.main()

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

    def test_paragraphs_basic(self):
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

    def test_legends_basic(self):
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

class LegsAndFigParas_tests(unittest.TestCase):

    def test_legendsFigPara_basic(self):
        paraBnd = '\n\n'
        text = paraBnd.join(['Figure 1 blah. ',
                            'a figure paragraph 2.',
                            'a Figures paragraph 3.',
                            'a fig. paragraph 4',
                            'a figs, paragraph 5',
                            'a table legend paragraph 6',
                            'a tables legend paragraph 7',
                            'a non interesting paragraph',
                            '',         # should be ignored
                            ' ',        # should be ignored
                            paraBnd,    # should be ignored
                            'F i g u re 8 blah.\nSecond line.\n',
                            'Supp lem ental Data Figure 9.',
                            ]) + paraBnd
        legs = list(legendsAndFigParagraphs(text, paraBnd=paraBnd))
        self.assertEqual(len(legs), 9)
        self.assertTrue(legs[0].endswith('blah.'))
        self.assertTrue(legs[8].endswith('Figure 9.'))
# end class LegsAndFigParas_tests ----------------------------------

class LegsAndFigWords_tests(unittest.TestCase):

    def test_legendsFigWords_basic(self):
        paraBnd = '\n\n'
        text = paraBnd.join(['Figure 1 blah. take whole paragraph. ',
                            '',         # should be ignored
                            ' ',        # should be ignored
                            paraBnd,    # should be ignored
                            'a figure paragraph 2.',
                            'In Figures 2 and 3 paragraph 3.',
                            'At the end of the paragraph fig',
                            'a figs and more tables blurb paragraph 5',
                            'two blurbs: table b1.1 b1.2 para 6 b2.1 b2.2 fig',
                            'a tables legend paragraph 7',
                            'a non interesting paragraph',
                            'F i g u re 8 blah.\nSecond line.\n',
                            'Supp lem ental Data Figure 9.',
                            ]) + paraBnd
                                        # grab legends and blurbs w/ 2 words
        legs = list(legendsAndFigWords(text, paraBnd=paraBnd, numWords=2))
        self.assertEqual(len(legs), 9)
        self.assertEqual(legs[0], 'Figure 1 blah. take whole paragraph.')
        self.assertEqual(legs[1], 'a figure paragraph 2.')
        self.assertEqual(legs[2], 'In Figures 2 and')
        self.assertEqual(legs[3], 'the paragraph fig')
        self.assertEqual(legs[4], 'a figs and more tables blurb paragraph')
        self.assertEqual(legs[5], 'two blurbs: table b1.1 b1.2 b2.1 b2.2 fig')

                                        # grab legends and blurbs w/ 1 words
        legs = list(legendsAndFigWords(text, paraBnd=paraBnd, numWords=1))
        self.assertEqual(len(legs), 9)
        self.assertEqual(legs[0], 'Figure 1 blah. take whole paragraph.')
        self.assertEqual(legs[1], 'a figure paragraph')
        self.assertEqual(legs[2], 'In Figures 2')
        self.assertEqual(legs[3], 'paragraph fig')
        self.assertEqual(legs[4], 'a figs and more tables blurb')
        self.assertEqual(legs[5], 'blurbs: table b1.1 b2.2 fig')
# end class LegsAndFigWords_tests ----------------------------------

if __name__ == '__main__':
    unittest.main()

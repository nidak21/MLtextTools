#!/usr/bin/env python3

"""
#######################################################################
Author:  Jim
Routines for
  * iteratoring through the paragraphs of a piece of text,
  * iteratoring through the fig and tbl legend paragraphs
  * iteratoring through the fig & tbl legends and paragraphs that refer to
    legends
  * iteratoring through the fig & tbl legends and parts of paragraphs that
    mention figs or tbls (the surrounding n words)

Example Usage:
    for paragraph in paragraphs(text):
        ...

    for legend in legends(text):
        ...

    for figText in legendsAndFigParagraphs(text):
        ...

    for figText in legendsAndFigWords(text, numWords=75):
        ...

To run automated tests:   python test_figureText.py [-v]

#######################################################################
"""

import re
from MLtextUtils import spacedOutRegex

DEFAULT_PARA_BND = '\n\n'	# default paragraph boundary

def paragraphs(text,                     # string to search for paragraphs
               paraBnd=DEFAULT_PARA_BND, # paragraph boundary string
    ):
    """ iterate through the paragraphs in text.
        The paraBnd is removed, and the returned paragraphs are stripped().
        Any stripped() paragraph that is the empty string is skipped and not
        returned.
    """
    for par in text.split(paraBnd):
        p = par.strip()
        if p: yield(p)
#---------------------------------

# Regular expressions for matching figure/table text
# Nomenclature:
# 'regex' = the text of a regular expression (as a string)
# 're'    = a regular expression object from the re module

# match a word "figure" or "table" in various forms
#  i.e.,  "fig" or "figure" or "figures" or "table" or "tables"
figureRe = re.compile(r'\b(?:fig(?:ure)?|table)s?\b', re.IGNORECASE)

# match the words that can begin a figure or table legend.
#   i.e., "fig" or "figure" or "supp...figure" or "table"
#   Note no plurals
#   Allow arb spaces between the letters since sometimes pdftotext inserts
#     spaces in bold fonted text.
legendRe = re.compile(\
        r'\b(?:' +
            r'(?:' +  # words that sometimes preceed "Figure" "Table" in legend
                r'(?:' + r's[ ]*u[ ]*p[ ]*p[ ]*(?:\w|[ ])*' + r'|' +
                    spacedOutRegex('online')                + r'|' +
                    spacedOutRegex('extendeddata') + 
                r')\s+' +
            r')?' +
            r'(?:' +    # the base words that start a legend
                spacedOutRegex('figure') + r'|' +
                spacedOutRegex('fig') + r'|' +
                spacedOutRegex('table') +
            r')' +
        r')\b',
        re.IGNORECASE)
#---------------------------------

def text2FigText_Legend(text,
    ):
    """
    Return list of paragraphs in text that are figure or table legends
    (paragraph starts with "fig" or "table")
    """
    return [ p for p in paragraphs(text) if legendRe.match(p) ]
#---------------------------------

def text2FigText_LegendAndParagraph(text,):
    """
    Return list of paragraphs in text that talk about figures or tables
    (includes legends)
    """
    figParagraphs = []

    for p in paragraphs(text):
        if legendRe.match(p) or figureRe.search(p):
            figParagraphs.append(p)

    return figParagraphs
#---------------------------------

def text2FigText_LegendAndWords(text, numWords=50,):
    """
    Return list of (full) legends and parts of paragraphs that talk about
      figures or tables
    The "parts" are defined by 'numWords' words surrounding figure/table
      references
    """
    figParagraphs = []

    for p in paragraphs(text):
        if legendRe.match(p):		# have figure/table legend
            figParagraphs.append(p)
        else:				# not legend, get parts
            figParagraphs += getFigureBlurbs(p, numWords)

    return figParagraphs
#---------------------------------

def getFigureBlurbs(text, numWords=50,):
    """
    Search through text for references to figures/tables.
    Return a list of text blurbs consisting of numWords around those references
    """
    matches = list(figureRe.finditer(text))	# all matches of fig/tbl words

    if len(matches) == 0: return []

    blurbs = []				# text blurbs to return

    # 1st match, leading chunk before first fig/tbl word
    m = matches[0]
    textChunk = text[ : m.start() ]	# text before the fig/tbl word
    words = textChunk.split()		# the words

        # curBlurb is text so far of the numWords around the current
        #   match we are looking at
    curBlurb = ' '.join(words[-numWords:])	# Start w/ words before 1st m

    # for each match before last one,
    #   look at textChunks between fig word matches
    for i in range(len(matches)-1):
        textChunk = text[ matches[i].start() : matches[i+1].start() ]
        words = textChunk.split() 	# words incl 1st fig word but not 2nd

        # Have '...fig ... intervening text fig...',
        #   words[] are the words in   fig ...intervening text
        # Could have two blurbs:  words[:numWords] and words[-numWords:]
        # But if these two blurbs overlap, really only one blurb:
        #   the whole intervening text

        if numWords > (len(words)-1)/2:	# have overlap (-1: dont count fig word)
            curBlurb += ' ' + ' '.join(words)	# no blurb boundary yet

        else:				# have 2 blurbs & blurb boundary
            eoBlurbWords = ' '.join(words[:numWords+1]) # +1: incl 'fig' word
            curBlurb += ' ' + eoBlurbWords
            blurbs.append(curBlurb)			# save this blurb

            curBlurb = ' '.join(words[-numWords:]) 	# start new blurb

    # last match, trailing chunk after last fig/tbl word
    m = matches[len(matches) -1]
    textChunk = text[ m.start() : ]
    words = textChunk.split()
    curBlurb += ' ' + ' '.join(words[:numWords+1])	# +1: incl 'fig' word
    blurbs.append(curBlurb)

    return blurbs
#---------------------------------

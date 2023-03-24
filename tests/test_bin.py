#!/usr/bin/env python3

import sys
import unittest
import os
import os.path
import time
from miscPyUtils import runShCommand
#import MLbaseSample
from testSample import *

# global settings
REMOVETMPFILES = False          # should we delete the files below, after tests?
beVerbose = '-v' in sys.argv    # how much test output to write to stdout
SAMPLEDATALIB = './testSample.py'  # location of the test sampledata lib
SAMPLEDATALIBPARAM = '--sampledatalib %s' % SAMPLEDATALIB

# The global SampleSet used in most tests
sampleSet = None

def populateSampleSet():
    """ Populate the global sampleSet with some test samples.
    """
    global sampleSet
    rcds = [ \
    {'knownClassName':'yes', 'ID':'1', 'color': 'red',
                                'text': 'Mary had a little lamb\n'},
    {'knownClassName':'yes', 'ID':'2', 'color': 'green',
                                'text': 'I love lamb chops said the wolf\n'},
    {'knownClassName':'yes', 'ID':'3', 'color': 'green',
                                'text': 'lamb chops are good said the cat\n'},
    {'knownClassName':'yes', 'ID':'4', 'color': 'green',
                                'text': 'dogs eat lamb chops\n'},
    {'knownClassName':'yes', 'ID':'5', 'color': 'green',
                                'text': 'foxes eat lamb chops too\n'},
    {'knownClassName':'no', 'ID':'6', 'color': 'red',
                                'text': 'I like hamburgers said the fox\n'},
    {'knownClassName':'no', 'ID':'7', 'color': 'green',
                                'text': 'I eat vegetables said the horse\n'},
    {'knownClassName':'no', 'ID':'8', 'color': 'green',
                                'text': 'green grass said the cow\n'},
    {'knownClassName':'no', 'ID':'9', 'color': 'green',
                                'text': 'brussel sprouts said the vegan\n'},
    {'knownClassName':'no', 'ID':'10', 'color': 'green',
                                'text': 'carots are eaten by rabbits\n'},
    ]
    sampleSet = ClassifiedSampleSet(sampleObjType=ClassifiedTestSample)
    sampleSet.setMetaItem('time', time.ctime().replace(' ', '_'))

    for r in rcds:
        sample = ClassifiedTestSample().setFields(r)
        sampleSet.addSample(sample)
# end populateSampleSet()--------------------------------------------

def verbose(s):
    if beVerbose:
        sys.stdout.write(s)

def reportWhichExecutable(fileName):
    """ Write to stdout the name of the executable that will be run
    """
    retCode, stout, sterr = runShCommand('which %s' % fileName)
    print('\n-------- Running Tests For: ' + stout)

def reportCmdDetails(cmd, retCode, stout, sterr):
    """ if verbose, write out details of the cmd and its output to stdout
    """
    verbose("cmd: '%s'\n" % cmd)
    verbose("retCode: %d\n" % retCode)
    verbose('-------- Stdout: --------\n')
    verbose(stout)
    verbose('-------- Stderr: --------\n')
    verbose(sterr)
    verbose('--------\n')

# -------- TestCases: --------------------------------------------

class GetSamples_tests(unittest.TestCase):
    pgm = 'getSamples.py'
    @classmethod
    def setUpClass(cls):
        reportWhichExecutable(cls.pgm)
       
    def setUp(self):
        self.SAMPLEFILE = 'sampleFile.txt'
        populateSampleSet()
        sampleSet.write(self.SAMPLEFILE)

    def tearDown(self):
        # would be nice to know if any tests failed, and keep these files if
        # so. But I don't see how to do that yet.
        if REMOVETMPFILES:
            os.remove(self.SAMPLEFILE)
        
    def test_withSampleDataLib_find0(self):
        # ID that is not in the sampleSet - should return 0 samples
        cmd = '%s %s --oneline 64 < %s' \
        % (self.pgm, SAMPLEDATALIBPARAM, self.SAMPLEFILE, )

        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)

        numLines = stout.count('\n')
        self.assertEqual(numLines, 0)

    def test_withSampleDataLib_find2(self):
        # 2 IDs in the sampleSet
        cmd = '%s %s --oneline 3 7 < %s' \
        % (self.pgm, SAMPLEDATALIBPARAM, self.SAMPLEFILE, )

        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)

        # the two samples should be one line each in stout
        numLines = stout.count('\n')
        self.assertEqual(numLines, 2)
# end class GetSamples_tests --------------------------------------------

class PreprocessSamples_tests(unittest.TestCase):
    pgm = 'preprocessSamples.py'
    @classmethod
    def setUpClass(cls):
        reportWhichExecutable(cls.pgm)
       
    def setUp(self):
        self.SAMPLEFILE = 'sampleFile.txt'
        self.OUTPUTFILE = 'sampleFile.preprocessed.txt'
        populateSampleSet()
        sampleSet.write(self.SAMPLEFILE)

    def tearDown(self):
        # would be nice to know if any tests failed, and keep these files if
        # so. But I don't see how to do that yet.
        if REMOVETMPFILES:
            os.remove(self.SAMPLEFILE)
            os.remove(self.OUTPUTFILE)
        
    def test_withSampleDataLib(self):
        # just a simple preprocessing step
        cmd = '%s -p tokenPerLine %s %s > %s' \
        % (self.pgm, SAMPLEDATALIBPARAM, self.SAMPLEFILE, self.OUTPUTFILE)

        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)
# end class PreprocessSamples_tests --------------------------------------------

class SplitSamples_tests(unittest.TestCase):
    pgm = 'splitSamples.py'
    @classmethod
    def setUpClass(cls):
        reportWhichExecutable(cls.pgm)
       
    def setUp(self):
        self.SAMPLEFILE = 'sampleFile.txt'
        self.RETAINEDFILE = 'sampleFile.retained.txt'
        self.LEFTOVERFILE = 'sampleFile.leftover.txt'
        populateSampleSet()
        sampleSet.write(self.SAMPLEFILE)

    def tearDown(self):
        # would be nice to know if any tests failed, and keep these files if
        # so. But I don't see how to do that yet.
        if REMOVETMPFILES:
            os.remove(self.SAMPLEFILE)
            os.remove(self.RETAINEDFILE)
            os.remove(self.LEFTOVERFILE)
        
    def test_withSampleDataLib(self):
        # via a few tries, this seed splits into 3 retained, 7 leftovers
        cmd = '%s %s -f .25 --seed 1 --retainedfile %s --leftoverfile %s %s' \
        % (self.pgm, SAMPLEDATALIBPARAM, self.RETAINEDFILE, self.LEFTOVERFILE,
                                                            self.SAMPLEFILE)
        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)

        retainedSampleSet = ClassifiedSampleSet().read(self.RETAINEDFILE)
        self.assertEqual(retainedSampleSet.getNumSamples(), 3)

        leftoverSampleSet = ClassifiedSampleSet().read(self.LEFTOVERFILE)
        self.assertEqual(leftoverSampleSet.getNumSamples(), 7)
# end class SplitSamples_tests --------------------------------------------

if __name__ == '__main__':
    unittest.main()

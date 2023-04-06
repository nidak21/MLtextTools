#!/usr/bin/env python

# tests for the scripts in MLtextTools/bin and a test tuningScript.py
# to run:   python test_bin.py [-v]

import sys
import unittest
import os
import os.path
import time
from miscPyUtils import runShCommand
from testSample import *

"""
These tests run programs in MLtextTools/bin via runShCommand.

If you run with -v, the tests output each shell command run and its
stdout and stderr so you can see what is going on.

They use
    testSample.py   - a sampleDataLib, defines a ClassifiedTestSample Class.
    testPipeline.py - defines a Pipeline to train.
    tuningScript.py - an example tuning script
    tuning.cfg      - a config file for tuningScript.py

They generate sample files, trained model pkl files, and other output files
from trainModel.py, predict.py, and tuningScript.py.

All generated files get put in ./tmp/ - so you can delete these as needed.

At the moment, most of the tests just check the return code from running the
scripts and succeed if it is zero.
We don't yet do much validation of the generated files.
"""

# global settings
TMPDIR = './tmp'            # path to tmp directory for generated files
REMOVETMPFILES = False      # should we delete generated tmp files, after tests?
beVerbose = '-v' in sys.argv    # how much test output to write to stderr
SAMPLEDATALIB = './testSample.py'  # location of the test sampledata lib
SAMPLEDATALIBPARAM = '--sampledatalib %s' % SAMPLEDATALIB

# The global SampleSet used in most tests
sampleSet = None

def populateSampleSet():
    """ Populate the global sampleSet with some test samples.
        "color" is just an arbitrary extra info field.
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
        sys.stderr.write(s)

def reportCmdDetails(cmd, retCode, stout, sterr):
    """ if verbose, write out details of the cmd and its output to stderr
        so it is intermingled with UnitTest output.
    """
    # get pathName of executable that will be run
    fileName = cmd.split()[0]
    rcode, pathName, err = runShCommand('which %s' % fileName)
    if pathName == '':          # command not found in the shell PATH
        pathName = 'command not found on PATH'
    else:
        pathName = pathName[:-1]        # remove '\n' at the end
        pathName = os.path.abspath(pathName)

    verbose('\n')
    verbose("Cmd: '%s'\n" % cmd)
    verbose('Which: %s\n' % pathName)
    verbose("RetCode: %d\n" % retCode)
    verbose('\t-------- Stdout: --------\n')
    verbose(stout)
    verbose('--------\n')
    verbose('\t-------- Stderr: --------\n')
    verbose(sterr)
    verbose('--------\n')

def tmpFile(name):
    """ Return the pathname in the tmp directory for the specified filename
        Remove the file from the tmp directory if it already exists
    """
    if not os.path.isdir(TMPDIR):
        verbose("mkdir %s\n" % os.path.abspath(TMPDIR))
        os.mkdir(TMPDIR)

    pathName = os.path.join(TMPDIR, name)
    if os.path.exists(pathName):
        os.remove(pathName)
    return pathName

# -------- TestCases: --------------------------------------------

class GetSamples_tests(unittest.TestCase):
    pgm = 'getSamples.py'
       
    def setUp(self):
        self.SAMPLEFILE = tmpFile('sampleFile.txt')
        populateSampleSet()
        sampleSet.write(self.SAMPLEFILE)

    def tearDown(self):
        # would be nice to know if any tests failed, and keep these files if
        # so. But I don't see how to do that yet.
        if REMOVETMPFILES:
            os.remove(self.SAMPLEFILE)
        
    def test_withSampleDataLib_find0(self):
        """ Test getSamples.py w/ 0 matching IDs in the sampleSet
        """
        cmd = '%s %s --oneline 64 < %s' \
        % (self.pgm, SAMPLEDATALIBPARAM, self.SAMPLEFILE, )

        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)

        numLines = stout.count('\n')
        self.assertEqual(numLines, 0)

    def test_withSampleDataLib_find2(self):
        """ Test getSamples.py w/ 2 matching IDs in the sampleSet
        """
        cmd = '%s %s --oneline 3 7 < %s' \
        % (self.pgm, SAMPLEDATALIBPARAM, self.SAMPLEFILE, )

        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)

        # the two samples should be one line each in stout
        numLines = stout.count('\n')
        self.assertEqual(numLines, 2)
# end class GetSamples_tests --------------------------------------------

class Predict_tests(unittest.TestCase):
    pgm = 'predict.py'
       
    def setUp(self):
        self.PIPELINEFILE = 'testPipeline.py'
        self.SAMPLEFILE  = tmpFile('sampleFile.txt')
        self.MODELFILE   = tmpFile('modelForPredict.pkl')
        self.PREDICTIONS = tmpFile('testPipeline.predictions')
        self.PERFORMANCE = tmpFile('testPipeline.performance')
        populateSampleSet()
        sampleSet.write(self.SAMPLEFILE)

    def tearDown(self):
        if REMOVETMPFILES:
            os.remove(self.SAMPLEFILE)
            os.remove(self.MODELFILE)
            os.remove(self.PREDICTIONS)
            os.remove(self.PERFORMANCE)
        
    def trainModel(self):
        cmd = 'trainModel.py -m %s -o %s %s %s' \
        % (self.PIPELINEFILE, self.MODELFILE, SAMPLEDATALIBPARAM,
            self.SAMPLEFILE, )

        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)

    def test_withSampleDataLib(self):
        self.trainModel()

        # run predictions on the training set
        cmd = '%s -m %s --performance %s  %s %s > %s' \
        % (self.pgm, self.MODELFILE, self.PERFORMANCE, 
                    SAMPLEDATALIBPARAM, self.SAMPLEFILE, self.PREDICTIONS )

        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)
# end class Predict_tests --------------------------------------------

class PreprocessSamples_tests(unittest.TestCase):
    pgm = 'preprocessSamples.py'
       
    def setUp(self):
        self.SAMPLEFILE = tmpFile('sampleFile.txt')
        self.OUTPUTFILE = tmpFile('sampleFile.preprocessed.txt')
        populateSampleSet()
        sampleSet.write(self.SAMPLEFILE)

    def tearDown(self):
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
       
    def setUp(self):
        self.SAMPLEFILE   = tmpFile('sampleFile.txt')
        self.RETAINEDFILE = tmpFile('sampleFile.retained.txt')
        self.LEFTOVERFILE = tmpFile('sampleFile.leftover.txt')
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

class TrainModel_tests(unittest.TestCase):
    pgm = 'trainModel.py'
       
    def setUp(self):
        self.PIPELINEFILE  = 'testPipeline.py'
        self.SAMPLEFILE    = tmpFile('sampleFile.txt')
        self.OUTPUTPKLFILE = tmpFile('testPipeline.pkl')
        self.FEATUREFILE   = tmpFile('testPipeline.features')
        populateSampleSet()
        sampleSet.write(self.SAMPLEFILE)

    def tearDown(self):
        # would be nice to know if any tests failed, and keep these files if
        # so. But I don't see how to do that yet.
        if REMOVETMPFILES:
            os.remove(self.SAMPLEFILE)
            os.remove(self.OUTPUTPKLFILE)
            os.remove(self.FEATUREFILE)
        
    def test_withSampleDataLib(self):
        cmd = '%s -m %s -o %s -f %s %s %s' \
        % (self.pgm, self.PIPELINEFILE, self.OUTPUTPKLFILE, self.FEATUREFILE,
                    SAMPLEDATALIBPARAM, self.SAMPLEFILE, )

        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)
# end class TrainModel_tests --------------------------------------------

class TuningScript_tests(unittest.TestCase):
    pgm = './tuningScript.py'
       
    def setUp(self):
        self.TRAININGFILE   = tmpFile('trainingFile.txt')
        self.VALIDATIONFILE = tmpFile('validFile.txt')
        self.MODELFILE      = tmpFile('tuningScript.pkl')
        self.INDEXFILE      = tmpFile('index.out')
        self.OUTPUTPREFIX   = './tmp/tuningScript'
        populateSampleSet()
        sampleSet.write(self.TRAININGFILE)
        sampleSet.write(self.VALIDATIONFILE)

    def tearDown(self):
        if REMOVETMPFILES:
            os.remove(self.TRAININGFILE)
            os.remove(self.VALIDATIONFILE)
            os.remove(self.OUTPUTPKLFILE)
            os.remove(self.FEATUREFILE)
        
    def test_validationSet(self):
        """ Test using a validation set """
        cmd = ' '.join([
                    self.pgm,
                    '--trainpath %s' % self.TRAININGFILE,
                    '--valpath %s'   % self.VALIDATIONFILE,
                    '--indexfile %s' % self.INDEXFILE,
                    '--savemodel %s' % self.MODELFILE,
                    '--outprefix %s' % self.OUTPUTPREFIX,
                    '--verbose',
                    '--index',
                    '--predict',
                    '--features',
                    '--rclassifier 783',
                    '--rsplit 515',
                    ])
        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)
        
    def test_validationAndTestSet(self):
        """ Test using a validation and test set """
        cmd = ' '.join([
                    self.pgm,
                    '--trainpath %s' % self.TRAININGFILE,
                    '--valpath %s'   % self.VALIDATIONFILE,
                    '--testpath %s'  % self.VALIDATIONFILE, # use validation set
                    '--indexfile %s' % self.INDEXFILE,
                    '--savemodel %s' % self.MODELFILE,
                    '--outprefix %s' % self.OUTPUTPREFIX,
                    '--verbose',
                    '--index',
                    '--predict',
                    '--features',
                    '--rclassifier 783',
                    '--rsplit 515',
                    ])
        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)
        
    def test_noValidationSet(self):
        """ Test using cross validation """
        cmd = ' '.join([
                    self.pgm,
                    '--trainpath %s' % self.TRAININGFILE,
                    '--valpath %s'   % 'None',
                    '--indexfile %s' % self.INDEXFILE,
                    '--savemodel %s' % self.MODELFILE,
                    '--outprefix %s' % self.OUTPUTPREFIX,
                    '--verbose',
                    '--index',
                    '--predict',
                    '--features',
                    '--rclassifier 783',
                    '--rsplit 515',
                    ])
        retCode, stout, sterr = runShCommand(cmd)
        reportCmdDetails(cmd, retCode, stout, sterr)
        self.assertEqual(retCode, 0)
# end class TuningScript_tests --------------------------------------------

if __name__ == '__main__':
    unittest.main()

#
# Define TestSample and TestClassifiedSample classes for automated tests

from MLbaseSample import *

class ClassifiedTestSample (ClassifiedSample):
    fieldNames = [ 'knownClassName', 'ID', 'color', 'text']
    extraInfoFieldNames = ['color']


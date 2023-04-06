#!/usr/bin/env python
import MLtuning as tl
import MLsklearnHelper as skHelper
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import GradientBoostingClassifier
#-----------------------
args = tl.args
randomSeeds = tl.getRandomSeeds( { 	# None means generate a random seed
                'randForSplit'      : args.randForSplit,
                'randForClassifier' : args.randForClassifier,
                } )
pipeline = Pipeline( [
('vectorizer', CountVectorizer(
                strip_accents=None,
                decode_error='strict',
                lowercase=True,
                stop_words='english',
                binary=True,
                #token_pattern=r'\b([a-z_]\w+)\b', Use default for now
                ),),
('classifier', GradientBoostingClassifier(verbose=0, random_state=0) ),
] )
parameters={'vectorizer__ngram_range':[(1,1),(1,2)],
        'vectorizer__min_df':[0.01],
        'vectorizer__max_df':[.75],
        }
note='\n'.join(["test tuning script", ]) + '\n'
p = tl.TextPipelineTuningHelper(pipeline, parameters, randomSeeds=randomSeeds,
                                note=note,).fit()
print(p.getReports())

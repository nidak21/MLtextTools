
# a simple test Pipeline definition that we can train and use to predict
import sys
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import GradientBoostingClassifier
#-----------------------
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
#parameters={'vectorizer__ngram_range':[(1,2)],
#	'vectorizer__min_df':[0.01],
#	'vectorizer__max_df':[.75],
#	'classifier__alpha':[1],
#	'classifier__eta0':[ .01],
#	'classifier__learning_rate':['optimal'],
#	'classifier__loss':[ 'log' ],
#	'classifier__penalty':['l2'],
#	}

#!/usr/bin/env python3
"""Creates a model for task 2 prediction.
    The model uses the data acquired from 4 files to generate a prediction file:
        1.testing_features.tsv
        2.testing_target.tsv
        3.training_features.tsv
        4.training_target.tsv

"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer


training_features = pd.read_table('/input/training_features.tsv')
testing_features = pd.read_table('/input/testing_features.tsv')
testing_target = pd.read_table('/input/testing_target.tsv')
training_target = pd.read_table('/input/training_target.tsv')

# training pipeline exported from TPOT:

# add/remove features
# impute missing values
# apply other transforms

imputer = SimpleImputer(strategy="median")
imputer.fit(training_features)
training_featuresx = imputer.transform(training_features)
testing_featuresx = imputer.transform(testing_features)


exported_pipeline = RandomForestClassifier(bootstrap=False, criterion="gini", max_features=0.2, min_samples_leaf=5, min_samples_split=4, n_estimators=100)
# Fix random state in exported estimator
if hasattr(exported_pipeline, 'random_state'):
    setattr(exported_pipeline, 'random_state', 42)

exported_pipeline.fit(training_featuresx, np.ravel(training_target))
results = exported_pipeline.predict(testing_featuresx)
resultsdf = pd.DataFrame({'Participant_ID':testing_features['Participant_ID'].values,'Disease Name':results}) 
resultsdf.to_csv('/output/predictions.tsv',sep='\t',index=False)

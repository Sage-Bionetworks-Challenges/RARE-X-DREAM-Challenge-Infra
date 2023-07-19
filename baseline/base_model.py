#!/usr/bin/env python3
"""Creates a model for task 2 prediction."""

import os
import glob

import typer
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer


def parse_series(X, col):
    # Concatenate all strings in the series into a single string
    series = X[col]
    string = (','.join(series.dropna().tolist())
              .replace('[', '')
              .replace(']', '')
              .replace('"', ''))

    # Split the string into individual values and keep the unique values
    unique_values = set(string.split(','))

    # Create an empty dictionary to store indicator column values
    indicator_columns = {}

    # Create indicator columns for each unique value
    for value in unique_values:
        if value:
            indicator_columns[col + ':' + value] = [
                1 if value in str(v)
                else np.nan if pd.isna(v) else 0
                for v in series
            ]

    # Create a pandas DataFrame from the indicator columns
    df = pd.DataFrame(indicator_columns)
    return df


def process_raw_data(input_dir):
    """Clean and parse for specific data from raw data."""

    # Concatenate all files into single dataframe.
    dfs = {}
    gen = {}
    for tsv in glob.glob(os.path.join(input_dir, "*")):
        df = pd.read_table(tsv)
        if (os.path.basename(tsv) == 'Disease_ID.tsv'):
            gen[os.path.basename(tsv)] = df
        else:
            dfs[os.path.basename(tsv)] = df
        if df.Participant_ID.isna().any():
            print(tsv, df.shape,)
    X = pd.concat(dfs, axis=0, ignore_index=True)

    # Drop unneeded/irrelevant columns.
    X.drop(columns=['Last_Updated_Date_UTC',
                    'Last_Updated_Time_UTC',
                    'Racial_Heritages',
                    'Participant_Country',
                    'Racial_Heritages_AmIndianAlaskaNative',
                    'Racial_Heritages_Asian',
                    'Racial_Heritages_BlackAfricanAmerican',
                    'Racial_Heritages_NativeHawaiian_PacIsland',
                    'Racial_Heritages_White',
                    'Racial_Heritages_Specific',
                    'Racial_Heritages_African',
                    'Racial_Heritages_Polynesian',
                    'Racial_Heritages_European',
                    'Racial_Heritages_MiddleEast_NorthAfrica',
                    'Ethnic_Heritage',
                    'Ethnic_Heritage_Hispanic_Latino',
                    'Physician_Tests',
                    'Genetic_Testing_Reason'],
           inplace=True)
    X.drop(columns=X.filter(regex='comment_Curated').columns, inplace=True)

    # Additionally drop columns with low-variance.
    het_cols = []
    low_var = []
    for xc in X.columns:
        if X[xc].nunique() == 1:
            low_var.append(xc)
        elif X[xc].apply(type).nunique() > 1:
            het_cols.append(xc)
    X.drop(columns=low_var, inplace=True)

    # Expand columns with stringlist values to one-hot encoded columns.
    ohx = []
    for ht in het_cols:
        ohx.append(parse_series(X, ht))
    XX = pd.concat([X, *ohx], axis=1)
    XX.drop(columns=het_cols, inplace=True)

    pass_through_nos = {}
    L2_surveys = {
        'Issue_Skin': 'Skin.tsv',
        'Issue_Teeth_Mouth': 'Oral_Health.tsv',
        'Issue_Muscles': 'Muscles.tsv',
        'Issue_LandD': 'Mothers_Pregnancy.tsv',
        'Issue_Lungs_Breathing': 'Lungs_Breathing.tsv',
        'Issue_Kidneys_Bladder_Genitals': 'Kidney_Bladder_Genitals.tsv',
        'Issue_Immune': 'Immune_System.tsv',
        'Issue_Heart_BV': 'Heart_Blood_Vessels.tsv',
        'Issue_HFN': 'Head_Face_Neck.tsv',
        'Issue_Growth': 'Growth.tsv',
        'Issue_Eyes_Vision': 'Eyes_And_Vision.tsv',
        'Issue_Endocrine': 'Endocrine_System.tsv',
        'Issue_ENT': 'Ears_And_Hearing.tsv',
        'Issue_Digestive_System': 'Digestive_System.tsv',
        'Issue_Cancer_NCTumor_PG': 'Cancer.tsv',
        'Issue_Brain_Nervous': 'Brain_And_Nervous_System.tsv',
        'Issue_Bones': 'Bone_Cartilage_Connective_Tissue.tsv',
        'Issue_Blood': 'Blood_Bleeding.tsv',
        'Issue_Behavior_Psych': 'Behavior.tsv'}
    for k, s in L2_surveys.items():
        pass_through_nos[k] = dfs[s].filter(
            like='_Symptom_Present').columns.values.tolist()

    # Pass through "no" values from L1 Health and Development survey to L2 fields
    for bp in pass_through_nos:
        temp = XX.groupby('Participant_ID')[bp].mean()
        for pid in temp.items():
            if pid[1] == 0:
                XX.loc[XX.Participant_ID == pid[0], pass_through_nos[bp]] = 0
    return XX, gen


def train(df):
    """Train model by using TPOT pipeline.

    Pipeline:
        - add/remove features
        - impute missing values
        - apply other transforms
    """
    # NOTE: Make sure that the outcome column is labeled 'target' in the data file
    features = df.drop('Disease_Name', axis=1)
    training_features, training_target = features, df['Disease_Name']

    imputer = SimpleImputer(strategy="median")
    imputer.fit(training_features)
    training_featuresx = imputer.transform(training_features)
    testing_featuresx = imputer.transform(testing_features)

    exported_pipeline = RandomForestClassifier(
        bootstrap=False, criterion="gini", max_features=0.2,
        min_samples_leaf=5, min_samples_split=4, n_estimators=100)
    # Fix random state in exported estimator
    if hasattr(exported_pipeline, 'random_state'):
        setattr(exported_pipeline, 'random_state', 42)

    exported_pipeline.fit(training_featuresx, np.ravel(training_target))
    
    return imputer, exported_pipeline


def main(input_dir: str = '/input',
         test_dir: str = '/test',
         output_dir: str = '/output'):
    """Main function."""
    select_diseases = [
        'Wiedemann-Steiner Syndrome (WSS)',
        'STXBP1 related Disorders',
        'FOXP1 Syndrome',
        'Kleefstra syndrome',
        'CHD2 related disorders',
        'CACNA1A related disorders',
        'Malan Syndrome',
        'SYNGAP1 related disorders',
        'CASK-Related Disorders',
        'HUWE1-related disorders',
        'AHC (Alternating Hemiplegia of Childhood)',
        'Classic homocystinuria',
        '8p-related disorders',
        'CHAMP1 related disorders',
        'DYRK1A Syndrome',
        '4H Leukodystrophy']

    # Preprocess training data, then train model.
    input_data, gen = process_raw_data(input_dir)
    input_data_df = (
        input_data.groupby('Participant_ID')
        .mean()
        .reset_index()
        .merge(
            gen['Disease_ID.tsv'].loc[gen['Disease_ID.tsv']['Disease_Name']
                                      .isin(select_diseases), :]))
    imputer, model = train(input_data_df)

    # Using trained model, run inference.
    test_data, *_ = process_raw_data(test_dir)
    testing_features = (
        test_data.reindex(columns=input_data.columns)
        .groupby('Participant_ID')
        .mean()
        .reset_index())
    testing_featuresx = imputer.transform(testing_features)
    results = model.predict(testing_featuresx)
    resultsdf = pd.DataFrame({
        'Participant_ID': testing_features['Participant_ID'].values,
        'Disease_Name': results})
    resultsdf.to_csv(
        os.path.join(output_dir, "predictions.tsv"),
        sep='\t', index=False)


if __name__ == "__main__":
    typer.run(main)

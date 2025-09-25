# ai_engine/utils/data_preprocessing.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def fill_missing(df, fill_value=None):
    """
    Fill missing values in DataFrame.
    If fill_value=None, fill with column mean for numerics, '' for strings.
    """
    for col in df.columns:
        if fill_value is not None:
            df[col].fillna(fill_value, inplace=True)
        elif df[col].dtype in [np.float64, np.int64]:
            df[col].fillna(df[col].mean(), inplace=True)
        else:
            df[col].fillna('', inplace=True)
    return df

def scale_features(df, scaler=None):
    """
    Scale features using StandardScaler (fit if not provided).
    Returns scaled df and the scaler object.
    """
    if scaler is None:
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df)
    else:
        df_scaled = scaler.transform(df)
    df_out = pd.DataFrame(df_scaled, columns=df.columns)
    return df_out, scaler

def select_features(df, feature_names):
    """
    Selects and returns only given feature columns from DataFrame.
    """
    return df[feature_names].copy()


import csv
import numpy as np
import pandas as pd
from numpy import ndarray

def create_features_vector_file() -> None:
    pass

def read_collection(csv_file: str) -> ndarray:
    df = pd.read_csv(csv_file)
    collection = df.iloc[:, 1:].values

    return collection

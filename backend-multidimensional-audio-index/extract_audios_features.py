import os
import librosa
import numpy as np

from glob import glob

from numpy import ndarray

audio_index = {}

def get_audio_files() -> list:
    audio_files = glob('/media/cristalino/USB/wavs/*.wav')

    return audio_files

def normalize_mfcc(mfcc: ndarray, num_features: int = 20) -> ndarray:
    num_features = min(mfcc.shape[1], num_features)

    normalized_features = []

    for i in range(num_features):
        coef_features = mfcc[:, i]
        min_val = np.min(coef_features)
        max_val = np.max(coef_features)
        mean_val = np.mean(coef_features)
        std_val = np.std(coef_features)

        normalized_features.extend([min_val, max_val, mean_val, std_val])

    return np.array(normalized_features)

def get_normalized_mfcc(audio_file: str) -> ndarray:
    y, _ = librosa.load(audio_file, sr=None)
    mfcc = librosa.feature.mfcc(y=y)

    return normalize_mfcc(mfcc)

def get_mfccs(audio_files: list[str]) -> list[ndarray]:
    audios_feat = []
    i = 1
    for file in audio_files:
        print(f'Saving {file}')
        mfcc = get_normalized_mfcc(file)
        file_name = os.path.splitext(os.path.basename(file))[0]
        audios_feat.append((file_name, mfcc))
        print(f'Creating mfcc {i}')
        i += 1

    return audios_feat

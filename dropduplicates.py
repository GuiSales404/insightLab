# -*- coding: utf-8 -*-
"""dropDuplicates.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15tL0qmlmVjezWCyBfs_26piQPxSk0ejQ
"""

import pandas as pd

from google.colab import drive
drive.mount('/content/drive')

df_transcription = pd.read_csv('/content/drive/MyDrive/treatTranscriptions/Transcriptions/Azure/azureTranscription.csv')

df_mozilla = pd.read_csv('/content/drive/MyDrive/treatTranscriptions/normalizedDS.csv')

df_transcription.columns

df_transcriptionClean = df_transcription.drop(columns=['client_id', 'up_votes', 'down_votes', 'age',
       'gender', 'accent', 'locale', 'segment', 'translation',
       'cos_sim_word2vec_cbow_s50', 'cos_sim_word2vec_skip_s50', 'bleu',
       'meteor', 'wer'])

df_transcriptionClean.head()

df_mozilla.columns

df_mozillaClean = df_mozilla.drop(columns='Unnamed: 0')

df_mozillaClean.head()

df = set(df_transcriptionClean['file']).intersection(set(df_mozillaClean['file']))

df_list = list(df)

df_metrics = pd.DataFrame(df_list, columns=['file'])

df_metrics.count()

df_merged = pd.merge(df_transcription, df_metrics, how = 'inner', on = "file")

df_merged.count()

df_merged.to_csv('/content/drive/MyDrive/treatTranscriptions/Transcriptions/Azure/azureNormalizedMetrics.csv')
# -*- coding: utf-8 -*-
"""allMetricsResults_allApis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xSohN0dcVU2nwsv1azxtnGDKmjtAV_l8

# Apply metrics to results
"""

!pip install jiwer
!pip install gensim
!pip install -U nltk
!pip install pandas

from google.colab import drive
drive.mount('/content/drive')

# Todas as ações relacionadas ao VoxForge estão comentadas pois só sera refeito para o ds do mozilla
# Adaptar para o local em que os resultados estão
results_path = "/content/drive/MyDrive/JIDM/Results/"

# Estes devem ser o nome das pastas dentro do result_path. Uma pasta para cada API/Model
models_apis = ["Wit", "Azure", "Google", "Wav2Vec", "AWS", "Jasper"]

# Estes são os nomes dos arquivos com os resultados das trancrições para computar as métricas
results_mozilla = ["mozilla_wit_api.tsv", "mozilla_azure_api.tsv", "mozilla_gcloud_api.tsv",
                   "transcribed_w2v2_metrics_mozilla.tsv", "generation_mozilla.tsv", "mozilla_result.tsv"]

# results_voxforge = ["voxforge_wit_api.tsv.tsv", "voxforge_azure_api.tsv", "voxforge_gcloud_api.tsv",
#                     "transcribed_w2v2_metrics_voxforge.tsv", "generation_voxforge.tsv", "voxforge_result.tsv"]

# As métricas computadas ficarão na pasta results_path dentro de cada pasta de models_api.
# O nome do arquivo será results_mozilla[i] + "_metrics.tsv", para mozilla
# O nome do arquivo será results_voxforge[i] + "_metrics.tsv", para voforge

from gensim.models import KeyedVectors

emb_models = {
    'word2vec_cbow_s50': KeyedVectors.load_word2vec_format('/content/drive/MyDrive/JIDM/embeddings/cbow_s50.txt'),
    'word2vec_skip_s50': KeyedVectors.load_word2vec_format('/content/drive/MyDrive/JIDM/embeddings/skip_s50.txt')
}

import re
from gensim import corpora
from gensim.matutils import softcossim
import nltk
nltk.download('rslp')
nltk.download('wordnet')
nltk.download('omw-1.4')
from nltk.translate import bleu_score, meteor_score
import pandas as pd
from jiwer import wer

def clean_str(x):
    try:
        return re.sub('\W', ' ', x).lower()
    except:
        # print(x)
        return ""


def cosine_similarity(reference, hypothesis, model):
    reference = reference.split()
    hypotesis = hypothesis.split()
    documents = [hypotesis, reference]
    dictionary = corpora.Dictionary(documents)

    similarity_matrix = emb_models[model].similarity_matrix(dictionary)

    hypotesis = dictionary.doc2bow(hypotesis)
    reference = dictionary.doc2bow(reference)

    return softcossim(hypotesis, reference, similarity_matrix)


def bleu(reference, hypothesis):
    references = [reference.split()]
    hypothesis = hypothesis.split()

    if len(references[0]) == 1:
        weights = (1.0, 0.0, 0.0, 0.0)
    elif len(references[0]) == 2:
        weights = (0.5, 0.5, 0.0, 0.0)
    elif len(references[0]) == 3:
        weights = (0.4, 0.3, 0.3, 0.0)
    else:
        weights = (0.4, 0.3, 0.2, 0.1)

    return bleu_score.sentence_bleu(references, hypothesis, weights=weights)


pt_stemmer = nltk.stem.RSLPStemmer()


def meteor(reference, hypothesis):
    references = [reference.split()]
    hypothesis = hypothesis.split()
    return meteor_score.meteor_score(references, hypothesis, stemmer=pt_stemmer)


def compute_wer(result, result_column_name="translation"):
    originals = result["sentence"]
    sentences = result["sentence"].apply(clean_str)
    translations = result[result_column_name].apply(clean_str)
    
    for original, sentence, translation in zip(originals, sentences, translations):
        result.loc[result["sentence"] == original,"wer"] = wer(sentence, translation)
    
    return result


def compute_cossine_metrics(result, save=True, output_to_save=None, name_dataset=None, result_column_name="translation"):
    originals = result["sentence"]
    sentences = result["sentence"].apply(clean_str)
    translations = result[result_column_name].apply(clean_str)

    # Cossine metrics
    for model in emb_models:
        print(f"Applying for {model}")
        for original, sentence, translation in zip(originals, sentences, translations):
            sentence = clean_str(sentence)
            translation = clean_str(translation)
            result.loc[result["sentence"] == original, f"cos_sim_{model}"] = cosine_similarity(
                sentence, translation, model)
    
    return result


def compute_wer_bleu_meteor_metrics(result, save=True, output_to_save=None, name_dataset=None, result_column_name="translation"):
    originals = result["sentence"]
    sentences = result["sentence"].apply(clean_str)
    translations = result[result_column_name].apply(clean_str)
    
    for original, sentence, translation in zip(originals, sentences, translations):
        print(f"Applying for bleu")
        result.loc[result["sentence"] == original,
                   "bleu"] = bleu(sentence, translation)
        print(f"Applying for meteor")
        result.loc[result["sentence"] == original,
                   "meteor"] = meteor(sentence, translation)
        print(f"Applying for wer")
        result.loc[result["sentence"] == original,
                   "wer"] = wer(sentence, translation)
        
    return result


def get_metrics(result, save=True, output_to_save=None, name_dataset=None, result_column_name="translation"):
    originals = result["sentence"]
    sentences = result["sentence"].apply(clean_str)
    translations = result[result_column_name].apply(clean_str)

    # Cossine metrics
    for model in emb_models:
        print(f"Applying for {model}")
        for original, sentence, translation in zip(originals, sentences, translations):
            sentence = clean_str(sentence)
            translation = clean_str(translation)
            result.loc[result["sentence"] == original, f"cos_sim_{model}"] = cosine_similarity(
                sentence, translation, model)

    for original, sentence, translation in zip(originals, sentences, translations):
        result.loc[result["sentence"] == original,
                   "bleu"] = bleu(sentence, translation)
        result.loc[result["sentence"] == original,
                   "meteor"] = meteor(sentence, translation)
        result.loc[result["sentence"] == original,
                   "wer"] = wer(sentence, translation)

    print(f"WER: {result['wer'].mean()}")
    print(f"bleu: {result['bleu'].mean()}")
    print(f"meteor: {result['meteor'].mean()}")
    for model in emb_models:
        print(f'{model}: {result[f"cos_sim_{model}"].mean()}')

    if save:
        result.to_csv(output_to_save +
                      f"/{name_dataset}_metrics.tsv", sep="\t", index=False)
        
    return result

# Mozilla
for idx in range(0, len(models_apis)):
    result_path = f"{results_path}{models_apis[idx]}/"
    result_file = f"{result_path}{results_mozilla[idx]}"
    
    print(f"Calculating for: {result_file}")
    result_df = pd.read_csv(result_file, sep='\t')
    result_df = get_metrics(result_df, output_to_save=result_path, name_dataset="mozilla")
    
# Voxforge
# for idx in range(0, len(models_apis)):
#     result_path = f"{results_path}{models_apis[idx]}/"
#     result_file = f"{result_path}{results_voxforge[idx]}"
    
#     print(f"Calculating for: {result_file}")
#     result_df = pd.read_csv(result_file, sep='\t')
#     result_df = get_metrics(result_df, output_to_save=result_path, name_dataset="voxforge")

"""# Metrics from all models ans API's

### Given that we have all the results we can conpute the summary of the translations in the following order:

#### Mozilla
        | WER | BLEU | METEOR | Word2Vec CBOW | Word2Vec SKIP
* Wit
* Azure
* Google Cloud      
* Wav2Vec2.0        
* AWS               
* Jasper            

#### Voxforge
        | WER | BLEU | METEOR | Word2Vec CBOW | Word2Vec SKIP
* Wit
* Azure             
* Google Cloud      
* Wav2Vec2.0        
* AWS               
* Jasper
"""

# Mozilla
res_wit = f"{results_path}Wit/mozilla_metrics.tsv"
res_azure = f"{results_path}Azure/mozilla_metrics.tsv"
res_gcloud = f"{results_path}Google/mozilla_metrics.tsv"
res_wav2vec = f"{results_path}Wav2Vec/mozilla_metrics.tsv"
res_aws = f"{results_path}AWS/mozilla_metrics.tsv"
res_jasper = f"{results_path}Jasper/mozilla_metrics.tsv"

wit = pd.read_csv(res_wit, sep="\t")
azure = pd.read_csv(res_azure, sep="\t")
gcloud = pd.read_csv(res_gcloud, sep="\t")
w2v = pd.read_csv(res_wav2vec, sep="\t")
aws = pd.read_csv(res_aws, sep="\t")
jasper = pd.read_csv(res_jasper, sep="\t")

print("#################### MOZILLA #####################")
print(f"API | WER | BLEU | METEOR | W2V CBOW | W2V SKIP")
print(f"Wit | {round(wit.wer.mean(),7)} | {round(wit.bleu.mean(),7)} | {round(wit.meteor.mean(),7)} | {round(wit.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(wit.cos_sim_word2vec_skip_s50.mean(),7)}")
print(f"Azure | {round(azure.wer.mean(),7)} | {round(azure.bleu.mean(),7)} | {round(azure.meteor.mean(),7)} | {round(azure.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(azure.cos_sim_word2vec_skip_s50.mean(),7)}")
print(f"Google | {round(gcloud.wer.mean(),7)} | {round(gcloud.bleu.mean(),7)} | {round(gcloud.meteor.mean(),7)} | {round(gcloud.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(gcloud.cos_sim_word2vec_skip_s50.mean(),7)}")
print(f"Wav2Vec | {round(w2v.wer.mean(),7)} | {round(w2v.bleu.mean(),7)} | {round(w2v.meteor.mean(),7)} | {round(w2v.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(w2v.cos_sim_word2vec_skip_s50.mean(),7)}")
print(f"AWS | {round(aws.wer.mean(),7)} | {round(aws.bleu.mean(),7)} | {round(aws.meteor.mean(),7)} | {round(aws.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(aws.cos_sim_word2vec_skip_s50.mean(),7)}")
print(f"Jasper | {round(jasper.wer.mean(),7)} | {round(jasper.bleu.mean(),7)} | {round(jasper.meteor.mean(),7)} | {round(jasper.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(jasper.cos_sim_word2vec_skip_s50.mean(),7)}")

# # Voxforge
# res_wit = f"{results_path}Wit/voxforge_metrics.tsv"
# res_azure = f"{results_path}Azure/voxforge_metrics.tsv"
# res_gcloud = f"{results_path}Google/voxforge_metrics.tsv"
# res_wav2vec = f"{results_path}Wav2Vec/voxforge_metrics.tsv"
# res_aws = f"{results_path}AWS/voxforge_metrics.tsv"
# res_jasper = f"{results_path}Jasper/voxforge_metrics.tsv"

# wit = pd.read_csv(res_wit, sep="\t")
# azure = pd.read_csv(res_azure, sep="\t")
# gcloud = pd.read_csv(res_gcloud, sep="\t")
# w2v = pd.read_csv(res_wav2vec, sep="\t")
# aws = pd.read_csv(res_aws, sep="\t")
# jasper = pd.read_csv(res_jasper, sep="\t")

# print("#################### VOXFORGE #####################")
# print(f"API | WER | BLEU | METEOR | W2V CBOW | W2V SKIP")
# print(f"Wit | {round(wit.wer.mean(),7)} | {round(wit.bleu.mean(),7)} | {round(wit.meteor.mean(),7)} | {round(wit.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(wit.cos_sim_word2vec_skip_s50.mean(),7)}")
# print(f"Azure | {round(azure.wer.mean(),7)} | {round(azure.bleu.mean(),7)} | {round(azure.meteor.mean(),7)} | {round(azure.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(azure.cos_sim_word2vec_skip_s50.mean(),7)}")
# print(f"Google | {round(gcloud.wer.mean(),7)} | {round(gcloud.bleu.mean(),7)} | {round(gcloud.meteor.mean(),7)} | {round(gcloud.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(gcloud.cos_sim_word2vec_skip_s50.mean(),7)}")
# print(f"Wav2Vec | {round(w2v.wer.mean(),7)} | {round(w2v.bleu.mean(),7)} | {round(w2v.meteor.mean(),7)} | {round(w2v.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(w2v.cos_sim_word2vec_skip_s50.mean(),7)}")
# print(f"AWS | {round(aws.wer.mean(),7)} | {round(aws.bleu.mean(),7)} | {round(aws.meteor.mean(),7)} | {round(aws.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(aws.cos_sim_word2vec_skip_s50.mean(),7)}")
# print(f"Jasper | {round(jasper.wer.mean(),7)} | {round(jasper.bleu.mean(),7)} | {round(jasper.meteor.mean(),7)} | {round(jasper.cos_sim_word2vec_cbow_s50.mean(),7)} | {round(jasper.cos_sim_word2vec_skip_s50.mean(),7)}")
from sentence_transformers import SentenceTransformer, util
import torch


BERT_MODEL_NAME = 'all-mpnet-base-v2'
bert_model = SentenceTransformer(BERT_MODEL_NAME)

def encode_bert(input):
    embedding = bert_model.encode(input)
    embedding = torch.tensor(embedding).unsqueeze(0)
    res = torch.nn.functional.normalize(embedding, p=2, dim=1)
    l = res.tolist()
    return l


def sim(vec1, vec2):
    cos_sim = util.pytorch_cos_sim(vec1, vec2)
    return cos_sim.item()
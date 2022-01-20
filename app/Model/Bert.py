from transformers import BertTokenizer, BertModel
from .BaseModel import BaseModel
import spacy
import numpy as np
import torch
class Bert(BaseModel):
  remove_stopwords = True

  def encode(self, text):
    # Source: https://mccormickml.com/2019/05/14/BERT-word-embeddings-tutorial/
    marked_text = "[CLS] " + text + " [SEP]"
    tokenized_text = self.tokenizer.tokenize(marked_text)
    segments_ids = [1] * len(tokenized_text)
    indexed_tokens = self.tokenizer.convert_tokens_to_ids(tokenized_text)
    segments_tensors = torch.tensor([segments_ids])
    tokens_tensor = torch.tensor([indexed_tokens])

    self.model.eval()
    with torch.no_grad():
      outputs = self.model(tokens_tensor, segments_tensors)
      hidden_states = outputs[2]
    
    token_embeddings = torch.stack(hidden_states, dim=0)
    token_embeddings = torch.squeeze(token_embeddings, dim=1)
    token_embeddings = token_embeddings.permute(1,0,2)

    token_vecs = hidden_states[-2][0]
    return torch.mean(token_vecs, dim=0)

  def download(self, path, name):
    tokenizer = BertTokenizer.from_pretrained(name, cache_dir=path)
    model = BertModel.from_pretrained(name, cache_dir=path, output_hidden_states = True)
    self.tokenizer = tokenizer
    return model

  def load(self, path, name):
    return self.download(path, name)
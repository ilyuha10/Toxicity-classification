
from keras.preprocessing.text import Tokenizer
import pickle
from keras.utils import pad_sequences
from abc import ABC, abstractmethod
from tqdm import tqdm
import numpy as np
from tokenizers import BertWordPieceTokenizer
import transformers

class ITokenWrapper(ABC):
    
    @classmethod
    @abstractmethod
    def get_features(self):
        pass

    @classmethod
    @abstractmethod
    def load(self):
        pass
    
    


    

class TokenSimple(ITokenWrapper):
    def __init__(self, xtrain, xvalid, max_len_sequence, load_mode=False):
        self.max_len_sequence = max_len_sequence
        self.xtrain = xtrain
        self.xvalid = xvalid
        if load_mode:
            self.load()
        else:
            self.save()

    def load(self):
        with open('data/tokenizer.pickle', 'rb') as handle:
            self.token = pickle.load(handle)
    
    def save(self):
        self.token = Tokenizer(num_words=None)
        self.token.fit_on_texts(list(self.xtrain) + list(self.xvalid))  
        with open('data/tokenizer.pickle', 'wb') as handle:
            pickle.dump(self.token, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def get_features(self, data):
        return pad_sequences(self.token.texts_to_sequences(data),maxlen=self.max_len_sequence)

    def get_word_index(self):
        return self.token.word_index

    

class BertToken(ITokenWrapper):
    def __init__(self, load_mode=False):
        if load_mode:
            self.load()
        else:
            self.save()    


    def fast_encode(self, texts, chunk_size=256, maxlen=512):
        """
        Encoder for encoding the text into sequence of integers for BERT Input
        """
        self.fast_tokenizer.enable_truncation(max_length=maxlen)
        self.fast_tokenizer.enable_padding(length=maxlen)
        all_ids = []
        
        for i in tqdm(range(0, len(texts), chunk_size)):
            text_chunk = texts[i:i+chunk_size].tolist()
            encs = self.fast_tokenizer.encode_batch(text_chunk)
            all_ids.extend([enc.ids for enc in encs])
        return np.array(all_ids)

    def load(self):
        self.fast_tokenizer = BertWordPieceTokenizer('data/vocab.txt', lowercase=False)
    
    def save(self):
        tokenizer = transformers.DistilBertTokenizer.from_pretrained('distilbert-base-multilingual-cased')
        tokenizer.save_pretrained('data/')
        self.load()
        

    def get_features(self, data):
        return self.fast_encode(data) 
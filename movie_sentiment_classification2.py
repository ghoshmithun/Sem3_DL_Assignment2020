# -*- coding: utf-8 -*-
"""Movie Sentiment Classification2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jvIaPkFnRDMNrkTlUQRu0U_rnS86eAHa
"""

!wget http://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz

!tar -xzf aclImdb_v1.tar.gz

ls -a

"""We have the data downloaded in the aclImdb folder. Lets explore the data

We are printing the readme which has the description fo the **data**
"""

!ls -a aclImdb/

!cat aclImdb/README

!head -10 aclImdb/train/pos/4298_10.txt

"""Each of the reviews are kept as a file , so we have to merge them"""

import glob
import os
def create_file(file_dir,final_file_name,label):
  os.chdir(file_dir)
  read_files = glob.glob("*.txt")
  with open(final_file_name, "w") as outfile:
      for f in read_files:
          with open(f, "r") as infile:
              outfile.write(str(infile.read()) + '||' + label + '\n')

os.getcwd()

create_file('/content/aclImdb/train/pos','all_pos_comments.txt','1')

create_file('/content/aclImdb/train/neg','all_neg_comments.txt','0')

"""Finally we have processed the data and uploaded here in csv format for easy experimentation."""

from google.colab import drive

drive.mount('/content/gdrive/')

ls

ls -al /content/gdrive/My\ Drive/Sem3/DL/project/

import pandas as pd

imdb_data = pd.read_csv('/content/gdrive/My Drive/Sem3/DL/project/IMDB Dataset.csv')
imdb_data.head()

"""Review column has html tags . We have to get rid of those"""

import re

def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

imdb_data['clean_review'] = imdb_data['review'].apply(cleanhtml)
imdb_data['label'] = imdb_data['sentiment'].apply(lambda x: 1 if x=='positive' else 0)

imdb_data.head()

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(imdb_data['clean_review'].values, imdb_data['label'].values, test_size=0.2)

X_train, X_cv, y_train, y_cv = train_test_split(X_train, y_train, test_size=0.4)

print("Shape of train data:", len(X_train))
print("Shape of CV data:", len(X_cv))
print("Shape of test data:", len(X_test))

from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.preprocessing import sequence
from keras.layers import Conv1D,MaxPooling1D
from keras.layers import Dense , Input, Dropout, Activation
from keras.layers import Bidirectional
from keras.layers.embeddings import Embedding
from keras.models import Model
from keras.preprocessing.text import Tokenizer
from tensorflow.keras.models import save_model
from tensorflow.keras.models import load_model
from keras.utils.vis_utils import plot_model
import pickle
import joblib
from sklearn.preprocessing import LabelEncoder

MAX_LEN=500
MAX_WORDS=5000
EMBEDDING_VECTOR_LENGTH = 128
EPOCH=6
TOKENIZER='/content/gdrive/My Drive/Sem3/DL/project/model_artifacts/word_cnn_lstm_tokenizer.pickle'
MODEL_PATH = '/content/gdrive/My Drive/Sem3/DL/project/model_artifacts/word_cnn_lstm_tokenizer.model'

le = LabelEncoder()

def word_cnn_lstm_model():
    embedding_vecor_length = EMBEDDING_VECTOR_LENGTH
    top_words = MAX_WORDS
    max_review_length = MAX_LEN
    model = Sequential()
    model.add(Embedding(top_words, embedding_vecor_length, input_length=max_review_length))  # vocab_len 270
    model.add(Conv1D(filters=32, kernel_size=4, padding='same', activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Conv1D(filters=32, kernel_size=2, padding='same', activation='tanh'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Bidirectional(LSTM(50, return_sequences=False)))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


# Only call the below function, It will define the model as above
def model_compile():
    model = word_cnn_lstm_model()
    model.summary()
    model.compile(loss='binary_crossentropy',optimizer='adam',metrics=['accuracy'])
    return model

def train_model(model,X,y,X_cv,y_cv, epoch =EPOCH, model_path=None):
    hist = model.fit(X, y, epochs=epoch, batch_size=16, verbose=1,validation_data=(X_cv, y_cv),
                     callbacks=[EarlyStopping(monitor='val_loss',min_delta=0.0001)])
    
    if model_path:
        path = model_path
    else:
        path =  MODEL_PATH
    save_model(
        model, filepath=path , overwrite=True, include_optimizer=True, save_format=None,
        signatures=None, options=None
    )
    return model,hist

def convert_y(y):
  return le.fit_transform(y)

import os

def save_pickle(path,object):
    with open(path, 'wb') as handle:
        pickle.dump(object, handle)

def read_pickle(path):
    with open(path, 'rb') as handle:
        object = pickle.load(handle)
    return object


def data_processing_model(X,train=False):
    """
    :param X: sentences in list format
    :param train: if train time then save
    :return: tokenized matrix for DL input
    """
    path = os.path.join(TOKENIZER)
    texts = [line.lower().split(" ") for line in X]
    if not train:
        tok = read_pickle(path)
    else:
      tok = Tokenizer(num_words=MAX_WORDS)
      tok.fit_on_texts(texts)
    text_tokenized = tok.texts_to_sequences(texts)
    if train:
        save_pickle(path, tok)
    text_sequence = sequence.pad_sequences(text_tokenized, maxlen=MAX_LEN)
    return text_sequence

X_train2=data_processing_model(X_train,train=True)
X_cv2 = data_processing_model(X_cv,train=False)

model=model_compile()
model, history=train_model(model,X=X_train2,y=y_train,X_cv=X_cv2,y_cv=y_cv)

from matplotlib import pyplot
def plot_history(history):
    pyplot.style.use('ggplot')
    acc = history.history['accuracy']
    val_acc = history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    x = range(1, len(acc) + 1)
    pyplot.figure(figsize=(12, 5))
    pyplot.subplot(1, 2, 1)
    pyplot.plot(x, acc, 'b', label='Training acc')
    pyplot.plot(x, val_acc, 'r', label='Validation acc')
    pyplot.title('Training and validation accuracy')
    pyplot.legend()
    pyplot.subplot(1, 2, 2)
    pyplot.plot(x, loss, 'b', label='Training loss')
    pyplot.plot(x, val_loss, 'r', label='Validation loss')
    pyplot.title('Training and validation loss')
    pyplot.legend()

plot_history(history)

def score_data(txt,tok,max_len=MAX_LEN):
    path = MODEL_PATH
    txts = data_processing_model(txt,train=False)
    model = load_model(path)
    preds = model.predict(txts)
    return preds

# Some random Example 

sample_texts = ["what an awesome movie","if this is good then nothing is bad"]
print(score_data(sample_texts,tok=read_pickle(TOKENIZER)))

y_pred_test = score_data(X_test,tok=read_pickle(TOKENIZER))

y_pred_test=y_pred_test.ravel()

from sklearn.metrics import classification_report
print(classification_report(y_pred=list(map(lambda x: int(x>0.5),y_pred_test)), y_true=y_test))

from sklearn.metrics import precision_recall_curve
def plot_pr_curve(test_y, model_probs):
    # calculate the no skill line as the proportion of the positive class
    no_skill = len(test_y[test_y==1]) / len(test_y)
    # plot the no skill precision-recall curve
    pyplot.plot([0, 1], [no_skill, no_skill], linestyle='--', label='No Skill')
    # plot model precision-recall curve
    precision, recall, _ = precision_recall_curve(test_y, model_probs)
    pyplot.plot(recall, precision, marker='.', label='Model')
    # axis labels
    pyplot.xlabel('Recall')
    pyplot.ylabel('Precision')
    # show the legend
    pyplot.legend()
    # show the plot
    pyplot.show()


plot_pr_curve(y_test,y_pred_test)

# plot no skill and model roc curves
from sklearn.metrics import roc_curve, roc_auc_score
def plot_roc_curve(test_y, model_probs,save=False):
    pyplot.plot([0, 1], [0, 1], linestyle='--', label='No Skill')
    # plot model roc curve
    fpr, tpr, _ = roc_curve(test_y, model_probs)
    pyplot.plot(fpr, tpr, marker='.', label='Model')
    auc = roc_auc_score(test_y, model_probs)
    pyplot.text(0.7,0.3,' ROC AUC=%.3f' % (auc))
    # axis labels
    pyplot.xlabel('False Positive Rate')
    pyplot.ylabel('True Positive Rate')
    # show the legend
    pyplot.legend()
    if save:
        return pyplot
    # show the plot
    pyplot.show()

plot_roc_curve(y_test,y_pred_test)
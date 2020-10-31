# Sem3_DL_Assignment2020

We have done lots of experiment to come up to this model architecture. For succintness of the submission we are not including all these experiments. Also, the data creation took a lot of effort. We have created the data in local and used the same for our modelling.

Also when we ran with full data (80% training) it has given better performance. This training is very time consuming , so we had to use only 50% data for training. As the code is working one can try these architecture any time

## Part C - Implementation 1

This is a bidirectional LSTM implementation. LSTM is a type of RNN architecture which accomodates the attention using memomry gates. That way it dispels the problem of vanishing gradient of LSTM
If we take attention from both direction of the input sequence (sentence) then its a bidirectional LSTM
Kindly refer 

* Movie Sentiment Classification1.ipynb 
* Movie Sentiment Classification1.py



## Part D - Implementation 2

This is hybrid model of CNN and Bi-LSTM. Bi-LSTM is explained above. CNN helps us to consider words as Bi-Gram. Then we are doing Max-pooling to do sampling

This hybrid architecture has performed better than the only Bi-LSTM. Please refer to the AUC-ROC curve and ROC value.

* Movie Sentiment Classification2.ipynb 
* Movie Sentiment Classification2.py

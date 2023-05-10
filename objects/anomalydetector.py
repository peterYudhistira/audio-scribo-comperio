import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nltk
import re
import string
import math
import gensim.downloader as api
import sklearn
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import inflect
import contractions
from sklearn.feature_extraction.text import TfidfVectorizer
import db
import gensim
from gensim import corpora, models
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN

# this is where everything we've experimented on will be implemented.


class AnomalyDetector():
    def __init__(self, df: pd.DataFrame) -> None:
        # turn into df and not excel dataset, like it.
        self.df = df
        self.model = api.load('word2vec-google-news-300') # might be better if i can save the file as bin then load it every time instead of downloading. 
        # print(self.df.head())
    # this function returns a list of tokens, cleaned and preprocessed.

    def preprocess_document(self, corpus, isLemma=False, isStopwords=False, isInflect=False, isNumberFiltered=True):

        inflector = inflect.engine()  # prepare inflector
        stop_words = set(stopwords.words("english"))
        lemmatizer = WordNetLemmatizer()
        punctuations = string.punctuation

        # if numbers are filtered, add that to the punctuation string
        if isNumberFiltered:
            punctuations += "1234567890"

        # case fold
        corpus = corpus.lower()

        # remove puncs
        corpus = "".join([char for char in corpus if char not in punctuations])

        # tokenize it.
        token_list = nltk.word_tokenize(corpus)

        for i in range(len(token_list)):
            # if inflect
            if isInflect:
                if token_list[i].isdigit():
                    token_list[i] = inflector.number_to_words(token_list[i])

            # if lemma
            if isLemma:
                tagged_word = nltk.pos_tag([token_list[i]])
                wordnet_pos = self.get_wordnet_pos(tagged_word[0][1])
                token_list[i] = lemmatizer.lemmatize(
                    tagged_word[0][0], pos=wordnet_pos)

            # if stopword
            if isStopwords:
                if token_list[i] in stop_words or token_list[i].isdigit():
                    token_list[i] = "#"  # mark as #

        # remove the marked strings
        token_list = [token for token in token_list if token != "#"]
        return token_list

    def get_wordnet_pos(self, tag):
        """Map POS tag to WordNet POS tag"""
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN  # solves as noun by default.

    def get_tfidf(self, documents, isPreprocessed=True):
        if not isPreprocessed:
            documents = [self.preprocess_document(
                doc, isLemma=True, isStopwords=True) for doc in documents]
        flattened_documents = [' '.join(doc) for doc in documents]
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(flattened_documents)
        tfidf_keys = vectorizer.get_feature_names_out()
        df_tfidf = pd.DataFrame(matrix.toarray(), columns=tfidf_keys)

        return df_tfidf, matrix

    # embed the individual words of a document. takes a list of tokens and a w2v model, returns a list of tuples(word, 300d vector).
    def word_embed(self, document, model):
        word_embed_pairs = []
        for word in document:
            if word in model:
                word_embed_pairs.append((word, model[word]))
        return word_embed_pairs

    def sentence_embed_unweighted_doc(self, word_embed_pair_list, aggregateMethod="avg"):
        wvs = []
        for pair in word_embed_pair_list:
            wvs.append(pair[1])
        if aggregateMethod == "avg":
            return np.mean(wvs, axis=0)
        else:
            return np.sum(wvs, axis=0)

    def sentence_embed_unweighted(self, word_embedded_docs, aggregateMethod="avg"):
        sentence_embedded_docs = []
        for i in range(len(word_embedded_docs)):
            sentence_embedded_docs.append(self.sentence_embed_unweighted_doc(
                word_embedded_docs[i], aggregateMethod))
        return sentence_embedded_docs

    # embed the words into sentences with a preferred method. takes a list of tuples (word, 300d vector), a tfidf matrix, and an index. returns a 300d vector aggregated sentence with the preferred method.
    def sentence_embed_weighted_doc(self, word_embed_pair_list, tfidf_matrix, index, aggregateMethod="avg"):
        weighted_wvs = []
        for pair in word_embed_pair_list:
            tfidf_weight = 0
            if pair[0] in tfidf_matrix:
                tfidf_weight = tfidf_matrix[pair[0]][index]
            weighted_wvs.append(pair[1] * tfidf_weight)

        weighted_wvs = np.array(weighted_wvs)
        if aggregateMethod == "avg":
            sentence_vector = np.mean(weighted_wvs, axis=0)
        else:
            sentence_vector = np.sum(weighted_wvs, axis=0)
        return sentence_vector

    def sentence_embed_weighted(self, word_embedded_docs, tfidf_matrix, aggregateMethod="avg"):
        sentence_embedded_docs = []
        for i in range(len(word_embedded_docs)):
            sentence_embedded_docs.append(self.sentence_embed_weighted_doc(
                word_embedded_docs[i], tfidf_matrix, i, aggregateMethod))
        return sentence_embedded_docs

    def LDA(self, docs, topic_prob):
        dictionary = corpora.Dictionary(docs)
        corpus = [dictionary.doc2bow(doc) for doc in docs]
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        lda_model = gensim.models.LdaModel(
            corpus_tfidf, num_topics=topic_prob, id2word=dictionary)
        doc_topic_distributions = lda_model[corpus]
        # view it...

        docFeatureList = []
        for doc_topic_dist in doc_topic_distributions:
            featureList = [0.0 for i in range(topic_prob)]
            for topic_dist in doc_topic_dist:
                featureList[topic_dist[0]] = topic_dist[1]
            docFeatureList.append(featureList)
        return docFeatureList

    # returns a tsne shrinkage also...
    def plot_documents(self, df):
        labels = np.array(df["No"])
        # don't forget to list it first, then np array it later.
        values = list(df["Document Embed"])

        # train model
        tsne_model = TSNE(perplexity=20, n_components=2,
                          init='pca', n_iter=2500, random_state=23)
        new_values = tsne_model.fit_transform(np.array(values))

        # plot
        x = []
        y = []
        for value in new_values:
            x.append(value[0])
            y.append(value[1])

        plt.figure(figsize=(20, 20))
        for i in range(len(x)):
            plt.scatter(x[i], y[i])
            plt.annotate(labels[i],
                         xy=(x[i], y[i]),
                         xytext=(5, 2),
                         textcoords='offset points',
                         ha='right',
                         va='bottom')
        plt.show()
        # use the thing to find new clusters.
        return new_values

    def dbscan_draw(self, vectors, epsilon, min):
        dbscan = DBSCAN(eps=epsilon, min_samples=min)
        clusters = dbscan.fit_predict(vectors)
        plt.title("to the depths of depravity {} and the cusp of blasphemy {}.".format(
            epsilon, min))
        plt.scatter(vectors[:, 0], vectors[:, 1], c=clusters)
        plt.show()
        print(clusters)

    def ExtractFeatures(self, method, model, isWeighted=True, aggregateMethod="avg", epsilon=0.01, minsamp=2, topics=5):
        # initialize components that need to be initialized.

        # extract the dataset in df
        df = pd.read_excel("Dataset.xlsx")

        # preprocess each document
        preprocessed_docs = [self.preprocess_document(
            doc, isLemma=True, isStopwords=True) for doc in df["Answer"]]

        # prepare a word-set
        # my_word_set = get_word_set(df)

        # prepare TF-IDF matrix for weighted embedding or weighted LDA
        if isWeighted:
            my_tfidf, my_matrix = self.get_tfidf(preprocessed_docs)

        # choose feature extraction (embed or LDA)
        doc_embeds = []
        if method == "embed":
            word_embedded_docs = [self.word_embed(
                doc, model) for doc in preprocessed_docs]  # word embedding
            # choose sentence embedding method here
            if isWeighted:
                doc_embeds = self.sentence_embed_weighted(
                    word_embedded_docs, my_tfidf, aggregateMethod)
            else:
                doc_embeds = self.sentence_embed_unweighted(
                    word_embedded_docs, aggregateMethod)
        elif method == "lda":
            doc_embeds = self.LDA(preprocessed_docs, topics)

        # append embedding to each document
        if doc_embeds:
            df["Document Embed"] = doc_embeds

        # get reduced values and draw the thang
        tsne_values = self.plot_documents(df)
        self.dbscan_draw(tsne_values, epsilon, minsamp)

        # # return the DF
        # return df


# dh = db.DatabaseHandler("database/testdb.db")
# myDF = dh.get_recordDataJoinedDF("event_id", 18)
# ad = AnomalyDetector(myDF)
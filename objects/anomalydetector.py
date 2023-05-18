# imports go here
import numpy as np
from objects import db
import pandas as pd
import inflect
import string
import nltk
import gensim
import contractions
import matplotlib.pyplot as plt
import gensim.downloader as api
from gensim import corpora, models
from nltk.test.gensim_fixt import setup_module
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE

# this is where everything we've experimented on will be implemented.


class AnomalyDetector():
    def __init__(self, dbName: str = "",  dh=None, model=None, modelName="glove-wiki-gigaword-300") -> None:
        if dh is None:
            self.dh = db.DatabaseHandler(dbName=dbName)
        else:
            self.dh = dh
        if model is None:
            if modelName != "":
                self.model = api.load(modelName)
        else:
            self.model = model

    '''
    inputs :
    - dh : DatabaseHandler --> to retrieve data from database
    - eventID : int --> we're doing this by event, so straight to the eventID
    - selector : str --> pretty much formality.
    - splitBySentences : bool --> Split each doc into sentences or not. Defaults to no.
    '''
    '''
    outputs:
    None, just setting
    '''

    def SetDFFromDB(self, dh: db.DatabaseHandler, eventID: int, selector: str = "event_id", splitBySentences: bool = False):
        self.df = self.dh.get_recordDataJoinedDF(selector=selector, ID=eventID)
        if splitBySentences:
            # df.set_index('id', inplace=True)
            self.df['answer'] = self.df['answer'].str.split('.')
            self.df = self.df.explode("answer", True)
            self.df.drop(self.df[self.df["answer"] == ""].index, inplace=True)
            self.df.reset_index(drop=True, inplace=True)

    # ditto above, but takes a pre-made DF instead.
    def SetDF(self, df:db.pd.DataFrame, splitBySentences:bool=False):
        self.df = df
        if splitBySentences:
            # df.set_index('id', inplace=True)
            self.df['answer'] = self.df['answer'].str.split('.')
            self.df = self.df.explode("answer", True)
            self.df.drop(self.df[self.df["answer"] == ""].index, inplace=True)
            self.df.reset_index(drop=True, inplace=True)

    def SetModel(self, modelName:str="glove-wiki-gigaword-300"):
        self.model = api.load(modelName)

    '''
    inputs :
    - dh : DatabaseHandler --> to retrieve data from database
    - eventID : int --> we're doing this by event, so straight to the eventID
    - selector : str --> pretty much formality.
    - splitBySentences : bool --> Split each doc into sentences or not. Defaults to no.
    '''
    '''
    outputs:
    - df : DataFrame --> dataframe containing the thing we're gonna be using.
    '''

    def GetDF(self, dh: db.DatabaseHandler, eventID: int, selector: str = "event_id", splitBySentences: bool = False):
        df = dh.get_recordDataJoinedDF(selector=selector, ID=eventID)
        if splitBySentences:
            # df.set_index('id', inplace=True)
            df['answer'] = df['answer'].str.split('.')
            df = df.explode("answer", True)
            df.drop(df[df["answer"] == ""].index, inplace=True)
            df.reset_index(drop=True, inplace=True)
        return df

    '''
    inputs:
    - doc : str --> a string representing a sentence/document.
    - isLemma : bool --> use lemmatizer or not? Defaults to not.
    - isStopWords : bool --> use stopwords or not? Defaults to not.
    - isInflect : bool --> use inflections (you're --> you are) or not? Defaults to not.
    - isNumberFiltered :  bool --> delete numbers in the string? Defaults to yes. 
    '''
    '''
    output : list<str> --> a list of word tokens (list<string>)
    '''

    def PreprocessDocument(self, doc: str, isLemma: bool = False, isStopWords: bool = False, isInflect: bool = False, isNumberFiltered: bool = True):
        inflector = inflect.engine()
        stopwordSet = set(stopwords.words("english"))
        lemmatizer = WordNetLemmatizer()
        punctuations = string.punctuation
        # if numbers are filtered, add that to the punctuation string
        if isNumberFiltered:
            punctuations += "1234567890"

        # case fold
        doc = doc.lower()

        # remove puncs
        doc = "".join([char for char in doc if char not in punctuations])

        # tokenize it.
        token_list = nltk.word_tokenize(doc)

        for i in range(len(token_list)):
            # if inflect
            if isInflect:
                if token_list[i].isdigit():
                    token_list[i] = inflector.number_to_words(token_list[i])

            # if lemma
            if isLemma:
                tagged_word = nltk.pos_tag([token_list[i]])
                wordnet_pos = self.getWordnetPos(tagged_word[0][1])
                token_list[i] = lemmatizer.lemmatize(
                    tagged_word[0][0], pos=wordnet_pos)

            # if stopword
            if isStopWords:
                if token_list[i] in stopwordSet or token_list[i].isdigit():
                    token_list[i] = "#"  # mark as #

        # remove the marked strings
        token_list = [token for token in token_list if token != "#"]

        if token_list:
            return token_list
        return [""]

    '''
    inputs:
    - tag : str --> the tag obtained from POS tagging.
    '''
    '''
    outputs:
    - str --> Wordnet POS tag.
    '''

    def getWordnetPos(self, tag):
        """Map POS tag to WordNet POS tag"""
        if tag.startswith('J'):
            return wordnet.ADJ
        elif tag.startswith('V'):
            return wordnet.VERB
        elif tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN  # solves as noun by default.

    '''
    inputs:
    - doclist : list<str> --> list of doc/sentences.
    - isProcessed : bool --> has it already been preprocessed? Defaults to True.
    '''
    '''
    outputs:
    - df_tfidf : Dataframe --> the TFIDF matrix in df form. 
    - matrix : matrix --> the TFIDF matrix purely. mainly for LDA purposes.
    '''

    def GetTFIDF(self, doclist: list, isPreprocessed=True):
        if not isPreprocessed:
            doclist = [self.PreprocessDocument(
                doc, isLemma=True, isStopWords=True) for doc in doclist]
        # else:
        #     # just tokenize the thing
        #     doclist = [nltk.word_tokenize(doc) for doc in doclist]
        # i think the thing has already been tokenized. That's the problem.
        flat_doclist = [' '.join(doc)
                        for doc in doclist]  # turn into one big corpus
        vectorizer = TfidfVectorizer()
        matrix = vectorizer.fit_transform(flat_doclist)
        tfidf_keys = vectorizer.get_feature_names_out()
        df_tfidf = db.pd.DataFrame(matrix.toarray(), columns=tfidf_keys)

        return df_tfidf, matrix

    # input : list<str> : tokens of one document/sentence
    # output : list<(str, list<int>[300])> : list of word-vector pair for each word available on the model
    def WordEmbed(self, document: list, model):
        word_embed_pairs = []
        for word in document:
            if word in model:
                word_embed_pairs.append((word, model[word]))
        return word_embed_pairs

    # input : list<(str, list<float>[300])>, str : word-vector pair list and preferred agg method.
    # output : list<float>[300] : 300-d vector that represents an aggregated value of the input words
    def SentenceEmbedUnweightedFunction(self, word_embed_pair_list: list, aggregateMethod: str = "avg"):
        wvs = []
        for pair in word_embed_pair_list:
            wvs.append(pair[1])
        if aggregateMethod == "avg":
            return np.mean(wvs, axis=0)
        else:
            return np.sum(wvs, axis=0)

    # input : list<list<(str, list<float>[300])>>, str : list containing word-vector pairs and preferred agg method
    # output : list<(str, list<int>[300])> : list containing sentence-vector pairs.
    def SentenceEmbedUnweighted(self, word_embedded_docs: list, aggregateMethod: str = "avg"):
        sentence_embedded_docs = []
        for i in range(len(word_embedded_docs)):
            sentence_embedded_docs.append(self.SentenceEmbedUnweightedFunction(
                word_embedded_docs[i], aggregateMethod))
        return sentence_embedded_docs

    '''
    input :
    list<list<(str, list<float>[300])>> : word-vector pair list
    matrix : tf-idf matrix for the corresponding doc
    int : the row we want
    str : preferred agg method
    '''
    # output : list<float>[300] : 300-d vector that represents an aggregated value of the input words

    def SentenceEmbedWeightedFunction(self, word_embed_pair_list: list, tfidf_matrix, index: int, aggregateMethod: str = "avg"):
        weighted_wvs = []
        # multiplies each word with its TF-IDF value in the corresponding row. Is 0 if word isn't found somehow.
        for pair in word_embed_pair_list:
            tfidf_weight = 0
            if pair[0] in tfidf_matrix:
                tfidf_weight = tfidf_matrix[pair[0]][index]
            weighted_wvs.append(pair[1] * tfidf_weight)
        # turn into array for fast aggregating
        weighted_wvs = np.array(weighted_wvs)
        if aggregateMethod == "avg":
            sentence_vector = np.mean(weighted_wvs, axis=0)
        else:
            sentence_vector = np.sum(weighted_wvs, axis=0)
        return sentence_vector

    # input : list<list<(str, list<float>[300])>>, str : list containing word-vector pairs, TF-IDF matrix of the corpus, and preferred agg method
    # output : list<(str, list<float>[300])> : list containing sentence-vector pairs.
    def SentenceEmbedWeighted(self, word_embedded_docs: list, tfidf_matrix, aggregateMethod="avg"):
        sentence_embedded_docs = []
        for i in range(len(word_embedded_docs)):
            sentence_embedded_docs.append(self.SentenceEmbedWeightedFunction(
                word_embedded_docs[i], tfidf_matrix, i, aggregateMethod))
        return sentence_embedded_docs

    '''
    input:
    - doclist : list<list<str>> --> list of tokenized sentences/docs
    - topics : int --> number of inferred topics.
    - use_tfidf : bool --> use TFIDF or not? defaults to yes.
    '''
    '''
    output:
    - docFeatureList : list<list<float>> --> topic distribution for each sentence/doc
    '''

    def GetLDADistribution(self, doclist: list, topics: int = 5, use_tfidf: bool = True):
        new_corpus = []

        if use_tfidf:
            for i in range(len(doclist)):
                doc = [(j, self.tfidf_matrix[i, j])
                       for j in self.tfidf_matrix[i].indices]
                new_corpus.append(doc)
                gensim_dict = corpora.Dictionary.from_corpus(new_corpus)
        else:
            gensim_dict = corpora.Dictionary(doclist)
            new_corpus = [gensim_dict.doc2bow(doc) for doc in doclist]

        lda_model = gensim.models.LdaModel(
            new_corpus, num_topics=topics, id2word=gensim_dict)
        goofy_ahh_doc_topic_distributions = lda_model[new_corpus]

        docFeatureList = []
        for doc_topic_dist in goofy_ahh_doc_topic_distributions:
            featureList = [0.0 for i in range(0, topics)]
            for topic_dist in doc_topic_dist:
                featureList[topic_dist[0]] = topic_dist[1]
            docFeatureList.append(featureList)

        return docFeatureList

    '''
    inputs:
    - vectors : list<list<float>> --> list of features corresponding to each doc/sentence
    - epsilon : float --> the radius within which points are considered connected.
    - min : int --> minimum amount of connected points for a point to be considered a core point of a cluster.
    '''
    '''
    output:
    clusters : list<int> --> a list of integers to assign each data point to a cluster. -1 means outlier.
    '''

    def GetDBSCANClusters(self, vectors, epsilon: float, min: int):
        dbscan = DBSCAN(eps=epsilon, min_samples=min)
        clusters = dbscan.fit_predict(vectors)
        # plt.title("to the depths of depravity {} and the cusp of blasphemy {}.".format(epsilon, min))
        # plt.scatter(vectors[:, 0], vectors[:, 1], c=clusters)
        # plt.show()
        # print(clusters)
        return clusters

    '''
    inputs :
    - clusters : list<int> --> a list of clusters assigned to each doc/sentence
    - df : DataFrame --> the dataframe in question
    '''
    '''
    outputs:
    - dfOutliers : DataFrame --> the dataframe whose answers have been marked as outliers.
    - dfGoods : DataFrame --> the dataframe whose answers have not been marked as outliers.
    '''

    def ReturnClusters(self, clusters: list, df: db.pd.DataFrame):
        df["Cluster Assignment"] = clusters
        dfGoods = df.loc[df["Cluster Assignment"] != -1]
        dfOutliers = df.loc[df["Cluster Assignment"] == -1]
        return dfOutliers, dfGoods

    def GetAnomalies_DBSCAN_Embedding(self, isWeighted: bool = True, aggregateMethod: str = "avg", epsilon: float = 0.01, minsamp: int = 2):
        # df and model are obtained by invoking a separate function, and it is assumed to be already available when invoking this function.

        # preprocess each doc/sentence
        self.preprocessedDocs = [self.PreprocessDocument(
            doc, isLemma=True, isStopWords=True) for doc in self.df["answer"]]

        # extract feature with embedding
        self.wordEmbeddedDocs = [self.WordEmbed(
            doc, self.model) for doc in self.preprocessedDocs]

        # if weighted, prepare TF-IDF and embed sentences with weight.
        if isWeighted:
            self.tfidf_df, self.tfidf_matrix = self.GetTFIDF(
                self.preprocessedDocs)
            self.doc_embeds = self.SentenceEmbedWeighted(
                self.wordEmbeddedDocs, self.tfidf_df, aggregateMethod)
        else:
            self.doc_embeds = self.SentenceEmbedUnweighted(
                self.wordEmbeddedDocs, aggregateMethod)

        # append embedding to each document
        if self.doc_embeds:
            self.df["Document Embed"] = self.doc_embeds
            self.df = self.df.dropna(subset=["Document Embed"]) # preventing NaN in the simplest fucking way in know.

        # apply DBSCAN
        self.clusters = self.GetDBSCANClusters(
            list(self.df["Document Embed"]), epsilon, minsamp)

        # return the dfs
        return self.ReturnClusters(self.clusters, self.df)

    def GetAnomalies_DBSCAN_LDA(self, isWeighted: bool = True, topics: int = 5, epsilon: float = 0.01, minsamp: int = 5):
        # df and model are obtained by invoking a separate function, and it is assumed to be already available when invoking this function.

        # preprocess each doc/sentence
        self.preprocessedDocs = [self.PreprocessDocument(
            doc, isLemma=True, isStopWords=True) for doc in self.df["answer"]]

        # if weighted, prepare tf-idf matrix.
        if isWeighted:
            self.tfidf_df, self.tfidf_matrix = self.GetTFIDF(
                self.preprocessedDocs)

        # use the in-house options for weighted or not.
        self.doc_embeds = self.GetLDADistribution(
            self.preprocessedDocs, topics=topics, use_tfidf=isWeighted)

        # append embedding to each document
        if self.doc_embeds:
            self.df["Document Embed"] = self.doc_embeds
            self.df = self.df.dropna(subset=["Document Embed"]) # preventing NaN in the simplest fucking way in know.

        # apply DBSCAN
        self.clusters = self.GetDBSCANClusters(
            list(self.df["Document Embed"]), epsilon, minsamp)

        # return the dfs
        return self.ReturnClusters(self.clusters, self.df)

    def GetAnomalies(self, method: str, model, isWeighted: bool = True, aggregateMethod: str = "avg", epsilon=0.01, minsamp=2, topics=5):
        # initialize
        # extract the dataset
        self.df = self.GetDF()

ad = AnomalyDetector("database/testdb.db")

ad.SetDFFromDB(ad.dh, 19, splitBySentences=False)

# df_outliers, df_goods = ad.GetAnomalies_DBSCAN_Embedding(isWeighted=True, aggregateMethod="avg", epsilon=0.6, minsamp=2)

# print(df_outliers)
# print(df_goods)

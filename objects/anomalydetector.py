# this is where everything experimented on will be implemented
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


class AnomalyDetector():
    def __init__(self, recordData) -> None:
        # turn into df and not excel dataset, like it.
        pass
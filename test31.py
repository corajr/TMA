#!/usr/bin/env python
import datetime,os
from src.backend.corpus import Corpus
import cPickle as pickle

corpus = pickle.load(open('corpus.obj'))
l =[]
for i in corpus.timeperiods:
	l.append(i[0].year)
print l
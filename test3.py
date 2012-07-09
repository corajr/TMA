#!/usr/bin/env python
import time,os
from src.backend.corpus import Corpus
from src.backend.dtmanalyzer import DTMAnalyzer
import cPickle as pickle

minwords = 25
doStem = True
remove_case = True

sw_file = '/Users/chrisjr/pm/mallet/mallet-2.0.7/stoplists/en.txt'
if not os.path.isfile('corpus.obj'):
	corpus = Corpus('/Users/chrisjr/pm/tma/work', stopwordfile=sw_file, remove_case = remove_case, dostem = doStem, minwords=minwords)
	basecorpusfile = getattr(corpus, 'corpusfile')
	corpus.setattr('corpusfile', basecorpusfile.replace('.dat','-mult.dat'))
	corpus.setattr('seqfile', basecorpusfile.replace('.dat','-seq.dat'))
	corpus.add_metadata('/Users/chrisjr/pm/tma/corpus.csv')
	corpus.add_data('/Users/chrisjr/pm/tma/txt', 'folder')
	pickle.dump(corpus, open('corpus.obj' ,'w'))
else:
	corpus = pickle.load(open('corpus.obj'))

corpusdir = corpus.get_work_dir()
corpusfile = corpus.get_corpus_file()
tmoutdir = corpusdir + '/' + 'dtm'
vocabfile = os.path.join(corpusdir,'vocab.txt')
titlesfile = os.path.join(corpusdir,'titles.txt')
corpus.write_vocab(vocabfile)
corpus.write_titles(titlesfile)

gblparams =  {'corpusfile':corpusfile,'vocabfile':vocabfile, 'titlesfile':titlesfile, 'outdir':tmoutdir, 'wordct':corpus.get_word_ct(), 'timelimit':100000}

# tfidf_cleanf = 0.7
# min_df = 5
# corpus.tfidf_clean(min(5000, int(corpus.get_vocab_ct()*tfidf_cleanf)), min_df=min_df)

dtmparams = {'dtmdir': '/Users/chrisjr/Dropbox/art/workspace/TMA/lib/dtm_release/dtm',
    'lda_max_em_iter': 10} #form.cleaned_data['dtm_lda_max_em_iter']}
dtmparams = dict(gblparams.items() + dtmparams.items())
analyzer = DTMAnalyzer(dtmparams)
analyzer.do_analysis()
pickle.dump(analyzer,open(os.path.join(analyzer.get_param('outdir'), 'analyzer.obj'),'w'))

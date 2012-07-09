#!/usr/bin/env python

from src.backend.dtmanalyzer import DTMAnalyzer
params = {'corpusfile': '/Users/chrisjr/Dropbox/art/workspace/TMA/tmaout/tmpY8j2xQ_formdata/corpus/corpus-mult.dat',
 'dtmdir': '/Users/chrisjr/Dropbox/art/workspace/TMA/lib/dtm_release/dtm',
 'lda_max_em_iter': 10,
 'outdir': u'/Users/chrisjr/Dropbox/art/workspace/TMA/tmaout/tmpY8j2xQ_formdata/dtm',
 'timelimit': 10000000,
 'titlesfile': '/Users/chrisjr/Dropbox/art/workspace/TMA/tmaout/tmpY8j2xQ_formdata/corpus/titles.txt',
 'vocabfile': '/Users/chrisjr/Dropbox/art/workspace/TMA/tmaout/tmpY8j2xQ_formdata/corpus/vocab.txt',
 'wordct': 471579}

dtm = DTMAnalyzer(params)

dtm.do_analysis()


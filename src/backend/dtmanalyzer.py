from math import exp
from tmanalyzer import TMAnalyzer
import os
from time import time
import pdb
import numpy as np

class DTMAnalyzer(TMAnalyzer):
    def __init__(self, params):
        """                                          
         ntopics [integer]: number of topics in DTM model (default=10)
         mode [fit OR time]: fit a new model or estimate times for heldout docs (default='fit')
         rng_seed [integer]: random seed or 0 to seed pseudo-randomly (default=0)
         initialize_lda [bool]: if true, initialize a new model; otherwise read model from 'initial-' files (default=true)
         corpus_prefix [file prefix]: prefix for '-mult.dat' and '-seq.dat' files (default './corpus')   
         outdir [folder]: output directory for DTM analysis (default = './dtmout')
         top_chain_var [float]: topic chain variance (default = 0.005)
         top_obs_var [float]: topic variational observation variance (default = 0.5)
         alpha [float]: initial alpha (default = 0.01)
         lda_sequence_min_iter [integer]: (default = 6)
         lda_sequence_max_iter [integer]: (default = 50)
         lda_max_em_iter [integer]: max number of EM iterations (default 10)
        """   
                                                               
        # replace default parameters with passed-in parameters
        dtmparams = {'ntopics': 10, 'mode': 'fit', 'rng_seed':0, 'initialize_lda':'true',
         'corpus_prefix': './corpus', 'outdir': './dtmout','top_chain_var':0.005,
         'top_obs_var': 0.5,'alpha': 0.01,'lda_sequence_min_iter': 6,'lda_sequence_max_iter': 50,        
         'lda_max_em_iter': 10, 'dtmdir': './',
         'timelimit': 10000000, 'corpusfile': './corpus-mult.dat',
         'titlesfile': './corpus/titles.txt',
         'vocabfile': './corpus/vocab.txt',
         'wordct': 0}
        for prm in params.keys():
            if dtmparams.has_key(prm):
                dtmparams[prm] = params[prm]
            else:
                raise Exception("unkown parameter value for DTMAnalyzer: %s" % prm)
        dtmparams['alg'] = 'dtm'       
        super(DTMAnalyzer, self).__init__(dtmparams)
    
    def do_analysis(self):
        if self.params['corpusfile']:
            self.params['corpus_prefix'] = self.params['corpusfile'].replace('-mult.dat', '')
        if self.params['mode'] == 'fit':
            cmd = 'ulimit -t %(timelimit)d; %(dtmdir)s/main ' + \
                '--ntopics=%(ntopics)d ' + \
                '--mode=%(mode)s ' + \
                '--rng_seed=%(rng_seed)d ' + \
                '--initialize_lda=%(initialize_lda)s ' + \
                '--corpus_prefix=%(corpus_prefix)s ' + \
                '--outname=%(outdir)s ' + \
                '--top_chain_var=%(top_chain_var)f ' + \
                '--alpha=%(alpha)f ' + \
                '--lda_sequence_min_iter=%(lda_sequence_min_iter)d ' + \
                '--lda_sequence_max_iter=%(lda_sequence_max_iter)d ' + \
                '--lda_max_em_iter=%(lda_max_em_iter)d'
            cmd = cmd % self.params
        elif self.params['mode'] == 'time':
            # TODO: figure out the output format for posterior estimation of times for heldout data
            pass

        print '\n' + cmd + '\n'
        stime = time()
        os.system(cmd)
        print 'finished DTM analysis in %f seconds' % (time()-stime)

    def createJSLikeData(self):
        # transform the likelihood data
        linfile = open('%s/em_log.dat' % self.params['outdir'], 'r')
        ldata = linfile.readlines()
        linfile.close()
        jsout = open('%s/js_likelihood.dat'% self.params['outdir'],'w')
        jsout.write('[')
        for i, line in enumerate(ldata):
            lik = line.strip().split()[0]
            jsout.write(lik)
            if not i == len(ldata)-1:
                jsout.write(',')
            else:
                jsout.write(']')
        jsout.close()

    def _read_matrix(self, filename, x, y):
        return np.loadtxt(filename).reshape(x, y)
    
    def init_rel_db(self):
        """
        Initialize the relationship (TMA) database by creating the appropriate tables
        """
        self.dbase = db(self.params['outdir'] + '/tma.sqlite')
        self.dbase.add_table("doc_doc (id INTEGER PRIMARY KEY, doc_a INTEGER, doc_b INTEGER, score FLOAT)")
        self.dbase.add_table("doc_topic (id INTEGER PRIMARY KEY, doc INTEGER, topic INTEGER, score FLOAT)")
        self.dbase.add_table("topics (id INTEGER PRIMARY KEY, title VARCHAR(100), score FLOAT)")
        self.dbase.add_table("topic_term (id INTEGER PRIMARY KEY, topic INTEGER, term INTEGER, score FLOAT)")
        self.dbase.add_table("topic_topic (id INTEGER PRIMARY KEY, topic_a INTEGER, topic_b INTEGER, score FLOAT)")
        self.dbase.add_table("doc_term (id INTEGER PRIMARY KEY, doc INTEGER, term INTEGER, score FLOAT)")
        self.dbase.add_table("terms (id INTEGER PRIMARY KEY, title VARCHAR(100), count INTEGER)")
        self.dbase.add_table("docs (id INTEGER PRIMARY KEY, title VARCHAR(100))")

    def create_relations(self):
        """
        This method uses the document termcounts, topics x terms matrix and documents x topics matrix to determine the following relationships:
        - term x term
        - topic x term
        - topic x topic
        - document x document
        - document x topic
        - document x term

        NOTE: this method should be called after 'do_analysis'
        """
        return
        self.init_rel_db()

        # doc-term (STD)
        wc_db = self.write_doc_term()

        # write the vocab to the database (STD)
        self.write_terms_table(wcs=wc_db)

        # write doc title to database (STD)
        self.write_docs_table()

        # write topics, i.e. top 3 terms (STD)

        # do one beta per time?
        # TODO figure out tbrowser
        
        beta = np.loadtxt(os.path.join(self.params['outdir'],'final.beta'))

        # topic_terms - NOTE should be negative valued
        self.write_topic_terms(beta)

        # topic_topic
        self.write_topic_topic(np.exp(beta)) 

        # term_term
        self.write_term_term(np.exp(beta))

        # doc_doc creation
        gamma = self._read_matrix(os.path.join(self.params['outdir'],'lda-seq/gam.dat'),0,0) # docs, topics
        theta = gamma / gamma.sum(1)[:,np.newaxis]
        self.write_doc_doc(theta**0.5)

        # doc_topic
        self.write_doc_topic(theta)

        # write topics
        self.write_topics_table(top_term_mat=beta, doc_top_mat=theta)

        # create indices for fast lookup
        self.create_db_indices()
from src.backend.db import db
from os import path  
import cPickle as pickle
import math
import urllib2
import sys   
import pdb
from src.backend.math_utils import hellinger_distance
from src.backend.tma_utils import slugify
import numpy as np
#template = None
#
#def import_template(template_name):
#    global template
#    sys.path.append("templates/" + template_name)
#    template = __import__(template_name)

class Document:
    def __init__(self, doc_id, title):
        self.id = doc_id
        self.title = unicode(str(title),errors='ignore')
   
    def __hash__(self):
        return hash((self.id, self.title))

    def __eq__(self, other):
        return (self.id, self.title) == (other.id, other.title)

    def get_safe_title(self):
        safe_title = slugify(self.title)
        return safe_title

#    def get_display(self):
#        return template.get_doc_display(self)

class Topic:
    def __init__(self, rel, topic_id, title):
        self.rel = rel
        self.topic_id = topic_id 
        self.id = topic_id 
        self.title = unicode(str(title),errors='ignore')
        self.terms = {}
        self.ranked_terms = []
        self.term_score_total = 0

    def __hash__(self):
        return hash((self.id, self.title))

    def __eq__(self, other):
        return (self.id, self.title) == (other.id, other.title)

    def get_term(self, rank): # this may be unneeded
        if self.terms == {}:
            self.terms = self.rel.get_topic_terms(self)
            self.ranked_terms = sorted(self.terms, key=self.terms.get, reverse=True)
        
        if rank >= len(self.ranked_terms):
            return None
        
        return self.ranked_terms[rank]

    def get_terms(self, cutoff=-1):
        if self.terms == {}:
            self.terms = self.rel.get_topic_terms(self, cutoff)
            self.ranked_terms = sorted(self.terms, key=self.terms.get, reverse=True)  
        
        return self.ranked_terms[:cutoff] 

    def get_safe_title(self):
        safe_title = slugify(self.title)
        return safe_title

    def get_terms_list(self, st=0, end = None):
        if self.terms == {}:
            print 'Call topics.get_terms(number) before calling get_terms_string'
        if end == None:
            end = len(self.ranked_terms)
        return map(lambda x: [x.title, x.id], self.ranked_terms[st:end])

    def get_relative_percent(self, term):
        self.get_terms(10)
        #rank = self.ranked_terms.index(term)
        if self.term_score_total == 0:
            for t in self.ranked_terms:
                self.term_score_total += math.exp(self.terms[t])
        percent = (math.exp(self.terms[term]) / self.term_score_total)


        if percent < .005:
            return 0
        else:
            return percent
        

class Term:
    all_terms = {}

    def __init__(self, term_id, title):
        self.id = term_id
        self.title = str(title)
        Term.all_terms[term_id] = self

    def __hash__(self):
        return hash((self.id, self.title))

    def __eq__(self, other):
        return (self.id, self.title) == (other.id, other.title)

    def get_safe_title(self):
        return self.title
        
    def set_title(self, title):
        self.title = str(title)
        

class relations:
    def __init__(self, mydb):
        self.mydb = mydb 
        self.term_topic_obj_loc = path.join(path.dirname(mydb.get_db_loc()), 'top_term_mat.obj')
        self.topics = [] # do we need these?
        self.docs = []
        self.terms = []
        self.term_score_range = (0, 0) 
        
         

    def get_term(self, term_id):
        if Term.all_terms.has_key(term_id):
            return Term.all_terms[term_id]
        else: 
            title_qry = self.mydb.get_term_title(term_id)
            if  title_qry == []:
                return None
            return Term(term_id, title_qry[0][0])

    def get_topics(self):
        if self.topics == []:
            topics_info = self.mydb.get_topics_info()  
            
            for topic_info in topics_info:
                topic_id = topic_info[0]
                title = topic_info[1]
                self.topics.append(Topic(self, topic_id, title))

        self.topics.sort(lambda x, y: -cmp(self.get_overall_score(x), self.get_overall_score(y)))  
        

        return self.topics

    def get_terms(self, cutoff = -1):
        if self.terms == []:
            terms_info = self.mydb.get_term_info(cutoff)
            for term_info in terms_info:
                term_id = term_info[0]
                self.terms.append(self.get_term(term_id))
            self.terms.sort(lambda x, y: -cmp(self.get_term_count(x), self.get_term_count(y)))
            self.term_score_range = (self.get_term_count(self.terms[-1]), self.get_term_count(self.terms[0]))
        return self.terms

    def get_topic(self, topic_id):
        topic_info = self.mydb.get_topic_info(topic_id )
        if topic_info == []:
            return None
        title = topic_info[0][1]
        return Topic(self, topic_id, title)

    def get_docs(self):
        if self.docs == []:
            docs_info = self.mydb.get_docs_info()
            for doc_info in docs_info:
                doc_id = doc_info[0]
                title = doc_info[1]
                self.docs.append(Document(doc_id, title))

        return self.docs

    def get_doc(self, doc_id):
        doc_info = self.mydb.get_doc_info(doc_id )
        title = doc_info[0][1]
        return Document(self, doc_id, title)
    
        
    def get_topic_terms(self, topic, cutoff=-1):
        topic_terms_info = self.mydb.get_topic_terms(topic.topic_id, cutoff)
        topic_terms = {}
        for info in topic_terms_info:
            term_id = info[2]
            score = info[3]
            term =self.get_term(term_id)
            if term != None:
                topic_terms[term] = score
        return topic_terms

    def get_related_docs(self, token):
        token_doc_info = []
        if isinstance(token, Topic):
            token_doc_info = self.mydb.get_top_topic_docs(token.id)
        elif isinstance(token, Document):
            token_doc_info = self.mydb.get_top_doc_docs(token.id) #TODO: id vs doc_id: make docs, topics, etc more consistent
        elif isinstance(token, Term):
            token_doc_info = self.mydb.get_top_term_docs(token.id)
        
        token_docs = {}
        for info in token_doc_info:
            doc_id = info[1]
            if isinstance(token, Document) and info[1] == int(token.id):
                doc_id = info[2]
            score = info[3]
            if score != 0: #TODO: is there better way to do this?
                doc_info = self.mydb.get_doc_info(doc_id)
                if doc_info != []:
                    title = doc_info[0][1]
                    token_docs[Document(doc_id, title)] = score
                #if len(token_docs.keys()) > 30:
                    #break
        
        return token_docs 
        
    def get_top_related_docs(self, token, num=2):  # TODO: phase out other technique
        token_doc_info = []
        if isinstance(token, Topic):
            token_doc_info = self.mydb.get_top_topic_docs(token.id,num)
        elif isinstance(token, Document):
            token_doc_info = self.mydb.get_top_doc_docs(token.id,num) #TODO: id vs doc_id: make docs, topics, etc more consistent
        elif isinstance(token, Term):
            token_doc_info = self.mydb.get_top_term_docs(token.id,num)

        token_docs = {}
        for info in token_doc_info:
            doc_id = info[1]
            if isinstance(token, Document) and info[1] == int(token.id):
                doc_id = info[2]
            score = info[3]
            if score != 0: #TODO: is there better way to do this?
                doc_info = self.mydb.get_doc_info(doc_id)
                if doc_info != []:
                    title = doc_info[0][1]
                    token_docs[Document(doc_id, title)] = score
                #if len(token_docs.keys()) > 30:
                    #break

        return token_docs 
            
    def get_top_related_topics(self, token, num=1): # TODO this should replace the get_related_topics function eventually
        token_topic_info = []
        if isinstance(token, Topic):
            token_topic_info = self.mydb.get_top_topic_topics(token.topic_id, num)
        elif isinstance(token, Document):
            token_topic_info = self.mydb.get_top_doc_topics(token.id, num)
        elif isinstance(token, Term):
            token_topic_info = self.mydb.get_top_term_topics(token.id, num)

        topics = {}
        for info in token_topic_info:
            score = info[3]
            if score != 0: #check for reverse pairs in topic-topic search
                if (isinstance(token, Topic) and info[2] == int(token.topic_id)) or isinstance(token, Term):
                    t = self.get_topic(info[1])
                    if t != None:
                        topics[t] = score #TODO: topic init needs work
                else:
                    t = self.get_topic(info[2])
                    if t != None:
                        topics[t] = score 
        return topics
    
    def get_related_topics(self, token):
        token_topic_info = []
        if isinstance(token, Topic):
            token_topic_info = self.mydb.get_top_topic_topics(token.topic_id)
        elif isinstance(token, Document):
            token_topic_info = self.mydb.get_top_doc_topics(token.id)
        elif isinstance(token, Term):
            token_topic_info = self.mydb.get_top_term_topics(token.id)
        
        topics = {}
        for info in token_topic_info:
            score = info[3]
            if score != 0 and not (isinstance(token, Document) and score < 1): #check for reverse pairs in topic-topic search
                if (isinstance(token, Topic) and info[2] == int(token.topic_id)) or isinstance(token, Term):
                    t = self.get_topic(info[1])
                    if t != None:
                        topics[t] = score #TODO: topic init needs work
                else:
                    t = self.get_topic(info[2])
                    if t != None:
                        topics[t] = score

        
        return topics
    
    
    def get_related_terms(self, term, top_n = 10): 
        # terms_info = self.mydb.get_top_term_terms(term.id)
        term_id = term.id
        top_term_mat = pickle.load(open(self.term_topic_obj_loc,'rb'))
        max_score = 100000000

        # compute the inverse Hellinger distance using the topic distributions for each term  (lower is better)
        term = top_term_mat[term_id,:]
        scores = hellinger_distance(term, top_term_mat)
        scores[term_id] = max_score
        scores = 1/scores
        top_term_ids = np.argsort(scores)[::-1][:top_n]
        top_terms = []
        for ttid in top_term_ids:
            top_terms.append(Term(int(ttid), self.mydb.get_term_title(int(ttid))[0][0]))
#        top_terms = map(lambda ttid: Term(ttid, self.mydb.get_term_title(ttid)[0][0]), top_term_ids) # TODO better way to get titles?
        #Term.all_terms = {}

        return top_terms

#        for term_comp_id in xrange(len(top_term_mat)):
#            if term_id == term_comp_id:
#                continue
#            score = 0
#            for i in xrange(len(top_term_mat[term_id])):
#                score += math.pow(top_term_mat[term_id][i] - top_term_mat[term_comp_id][i], 2)
#            if score > 0:
#                if len(top_terms) < top_n or score < max_score:
#                    newterm = Term(term_comp_id,'frogtoes') # titles do not matter TODO this is inefficient
#                    newterm.score = score
#                    top_terms.append(newterm)
#                    top_terms.sort(key=lambda x: x.score)
#                    if not len(top_terms) < top_n:
#                        del(top_terms[-1])
#                    max_score = top_terms[-1].score
#
#        for i in xrange(len(top_terms)):
#            top_terms[i].set_title(self.mydb.get_term_title(top_terms[i].id)[0][0])
#
#        # to maintain data consistency when accessing terms in other context (since the Title isn't set here)

    def get_relative_percent(self, topic, term):
        topics = self.get_related_topics(term)
        score = 0
        topica = ''#topics should be universal instead
        for t in topics.keys():
            score += topics[t];
            if int(t.topic_id) == int(topic.topic_id):
                topica = t
        return topics[topica] / score
    
    def get_term_count(self, term):
        total = 0;
        for doc_info in self.mydb.get_top_term_docs(term.id):
            total += doc_info[3]
        return total

    def get_overall_score(self, topic):
        total = 0;
        for doc_info in self.mydb.get_top_topic_docs(topic.topic_id):
            total += doc_info[3]
        return total
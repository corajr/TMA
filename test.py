#!/usr/bin/python

from src.backend.corpus import *
import tempfile, glob, shutil

mydir = tempfile.mkdtemp()
c = Corpus(mydir)
c.add_metadata(glob.glob("/Users/chrisjr/Downloads/dtm*.csv")[-1])
for doc in c.metadata.keys():
	c._add_doc_to_time_period(doc)

print [[x.year for x in y] for y in c.timeperiods]
print c.docsbytimeperiod
shutil.rmtree(mydir)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 13:14:29 2021

@author: jenniferjasperse
"""


import math
import sys
import time

import metapy
import pytoml

#import scipy
#from scipy import stats
#import numpy as np


def clean_document(doc):
    
    #Write a token stream that tokenizes with ICUTokenizer (use the argument "suppress_tags=True"), 
    #lowercases, removes words with less than 2 and more than 5  characters
    #performs stemming and creates trigrams (name the final call to ana.analyze as "trigrams")


    #suppress tags
    tok = metapy.analyzers.ICUTokenizer(suppress_tags=True)
    tok.set_content(doc.content())
    #tokens = [token for token in tok]
    #print(tokens)
    
    #remove punctuation???
    tok = metapy.analyzers.AlphaFilter(tok)
    tok.set_content(doc.content())
    #tokens = [token for token in tok]
    #print(tokens)
    
    #convert to lowercase
    tok = metapy.analyzers.LowercaseFilter(tok)
    tok.set_content(doc.content())
    #tokens = [token for token in tok]
    #print(tokens)
    
    
    #tok = metapy.analyzers.ListFilter(tok, "lemur-stopwords.txt", metapy.analyzers.ListFilter.Type.Reject)
    #tok.set_content(doc.content())
    #tokens = [token for token in tok]
    #print(tokens)
    
    
    #stemming
    tok = metapy.analyzers.Porter2Filter(tok)
    tok.set_content(doc.content())
    #tokens = [token for token in tok]
    #print(tokens)
    
    tokens = [token for token in tok]
    doc_cleaned = ' '.join(tokens)
    #print(doc_cleaned)
    return doc_cleaned


def load_ranker(cfg_d):
    """
    Use this function to return the Ranker object to evaluate, 
    The parameter to this function, cfg_file, is the path to a
    configuration file used to load the index.
    """
    
    if('ranker' in cfg_d):
        return metapy.index.OkapiBM25(k1=cfg_d['ranker']['k1'],
                                      b=cfg_d['ranker']['b'],
                                      k3=cfg_d['ranker']['k3'])
    return metapy.index.OkapiBM25()
    #return metapy.index.OkapiBM25(1.1,0.7,500)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: {} config_file.toml".format(sys.argv[0]))
        sys.exit(1)

    cfg = sys.argv[1]
    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)
    print('Building or loading index...')
    idx = metapy.index.make_inverted_index(cfg)
    ranker = load_ranker(cfg_d)
    ev = metapy.index.IREval(cfg)
    

    full_docs = []
    if cfg_d['duplicates']=='True':   
        full_doc_filename = "book_titles_full.txt"
        with open(full_doc_filename, 'r') as fin:
            full_docs = fin.readlines()
    else:
        full_doc_filename = "book_titles_full_no_duplicates.txt"
        with open(full_doc_filename, 'r') as fin:
            full_docs = fin.readlines()
        

    query_cfg = cfg_d['query-runner']
    if query_cfg is None:
        print("query-runner table needed in {}".format(cfg))
        sys.exit(1)
    
    start_time = time.time()
    top_k = 10
    query_path = query_cfg.get('query-path', 'goodreads_book_series_queries.txt')#'queries.txt')
    query_start = query_cfg.get('query-id-start', 0)
    
    
    results = []
    query = metapy.index.Document()
    print('Running queries')
    c=0
    with open(query_path) as query_file:
        for query_num, line in enumerate(query_file):
            if c < 2000:#==32:#< 200:
                doc = metapy.index.Document()
                doc.content(str(line.strip()))
                clean_line = clean_document(doc)
                #print(line)
                query.content(clean_line)
                #print(clean_line)
                result = ranker.score(idx, query, top_k)
                #for res in result:
                #    print('\tname: %i: %s'%(res[0],full_docs[int(res[0])]))
                #    clean_doc = metapy.index.Document()
                #    clean_doc.content(str(full_docs[int(res[0])]).strip())
                #    clean_doc_line = clean_document(clean_doc)
                #    print('\tclean name: %i: %s'%(res[0],clean_doc_line))
                #    print('\tscore: %.4f'%(float(res[1])))
                results.append(result)
                avg_p = ev.avg_p(result, query_start + query_num, top_k)
                #print("Query {} average precision: {}".format(query_num + 1, avg_p))
            c+=1
    print("Mean average precision: {}".format(ev.map()))
    print("Elapsed: {} seconds".format(round(time.time() - start_time, 4)))
        
    
    #list(np.array(result)[:,0].astype(int).astype(str))
    

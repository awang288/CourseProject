#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: jenniferjasperse
"""
###interactive search engine###

import math
import sys
import time

import metapy
import pytoml




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

if __name__ == '__main__':
    #if len(sys.argv) != 2:
        #print("Usage: {} config_file.toml".format(sys.argv[0]))
        #sys.exit(1)

    print('Welcome to the search engine!')
    cfg = ''
    if len(sys.argv) > 1:
        cfg = sys.argv[1]
    else:
        
        valid_search_type = False
        while valid_search_type == False:
            print('Please select an engine to search:')
            print('\t[1] Title Search')
            print('\t[2] Keyword Search')
            search_type = input('Enter 1 for title search or 2 for keyword search: ')
            search_type = int(search_type.strip())
            if search_type == 1:
                cfg = 'config_titles_no_duplicates.toml'
                print('Selected title search!')
                valid_search_type=True
            elif search_type == 2:
                cfg = 'config_titles_desc_no_duplicates.toml'
                print('Selected keyword search!')
                valid_search_type = True
            else:
                print('Error: please select a valid option.')
    
    
    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)    
    
    print('Loading search engine...')
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
    top_k = 1000
    
    status = 'run'
    while status =='run':
        
        line = input('Enter search query (or q to quit): ')
        if line == 'q':
            status = 'quit'
        else:
            doc = metapy.index.Document()
            doc.content(str(line.strip()))
            clean_line = clean_document(doc)
            query = metapy.index.Document()
            query.content(clean_line )
            result = ranker.score(idx, query, top_k)
            result_index = 1
            i = 0
            load_more = 'y'
            while ((i+1)*10 < top_k) and (load_more == 'y'):
                for res in result[10*i:10*(i+1)]:
                    print('\t%i. %s'%(result_index,full_docs[int(res[0])]))
                    result_index += 1
                    #print('\tscore: %.4f'%(float(res[1])))
                
                load_more = input('Load more results? (Y/N): ').lower()
                i += 1
        
            print('Search complete!')
    
    print('Exiting search engine....')
                
                

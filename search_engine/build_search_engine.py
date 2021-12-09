#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
runs backend prep for search engine:
    creates corpus 
    creates queries and evals
    cleans data as necessary
@author: jenniferjasperse
"""
import metapy
import gzip
import json
import sys
import pytoml

import pandas as pd



def clean_document(doc):

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
    
    return doc_cleaned


def build_corpus(books_filename,include_duplicates=False):
    
    c=0
    
    
    corpus_title = []
    corpus_desc = []
    
    corpus_desc_present = []
    
    data_lan = []
    with gzip.GzipFile(books_filename, 'r',) as fin:
        while c < 2360000:#
            #for line in fin:
            try:
                line = fin.readline()
                if c%1000==0:
                    print(c)
                info=json.loads(line.decode('utf-8'))
                data_lan.append(info)
                
                
                doc = metapy.index.Document()
                doc.content(info['title'])
                corpus_title.append(clean_document(doc))
                
                doc = metapy.index.Document()
                doc.content(info['title'] + ' ' + info['description'])
                corpus_desc.append(clean_document(doc))
                if (len(info['description']) > 0):
                    corpus_desc_present.append(1)
                else:
                    corpus_desc_present.append(0)
                    
            except:
                pass
            
            c+=1
    
    if(include_duplicates):
        printing_corpusfile = open("book_titles_full.txt","w")
        for info in data_lan:
            printing_corpusfile.write(info['title'] + ' (' + info['publication_year'] + ')\n')
        printing_corpusfile.close()
    else:
        printing_corpusfile = open("book_titles_full_no_duplicates.txt","w")
        for info in data_lan:
            printing_corpusfile.write(info['title'] + ' (' + info['publication_year'] + ')\n')
        printing_corpusfile.close()
        
    
    #write corpus file  for book titles without descriptions
    if(include_duplicates):
        title_corpusfile = open("book_titles/book_titles.dat", "w")
        for title in corpus_title:
            title_corpusfile.write(title + " .\n")
        title_corpusfile.close()
    else:
        title_corpusfile = open("book_titles_no_duplicates/book_titles_no_duplicates.dat", "w")
        for title in corpus_title:
            title_corpusfile.write(title + " .\n")
        title_corpusfile.close()
    
    #write corpus file for book titles with descriptions
    if(include_duplicates):
        desc_corpusfile = open("book_titles_desc/book_titles_desc.dat", "w")
        for entry in corpus_desc:
            desc_corpusfile.write(entry + " .\n")
        desc_corpusfile.close()
    else:
        desc_corpusfile = open("book_titles_desc_no_duplicates/book_titles_desc_no_duplicates.dat", "w")
        for entry in corpus_desc:
            desc_corpusfile.write(entry + " .\n")
        desc_corpusfile.close()
        
        

def make_queries(query_input_file,query_output_file):
    
    df = pd.read_csv(query_input_file)
    series_titles = df[['series_title']].drop_duplicates()
    series_titles.to_csv(query_output_file,header=False,index=False)
    
    return series_titles





if __name__=="__main__":
            

    if len(sys.argv) != 2:
        print("Usage: {} config_file.toml".format(sys.argv[0]))
        sys.exit(1)

    cfg = sys.argv[1]
    
    #load config file
    with open(cfg, 'r') as fin:
        cfg_d = pytoml.load(fin)
    
    books_filename = ''
    
    #build corpus
    if(cfg_d['duplicates'] == 'True'):
        books_filename = "../data/goodreads_books_cleaned.json.gz"
        build_corpus(books_filename,include_duplicates=True)
    else:
        books_filename = "../data/goodreads_books_cleaned_no_duplicates.json.gz"
        build_corpus(books_filename,include_duplicates=False)
        
        
    
    query_output_filename="goodreads_book_series_queries.txt"
    series_filename = "../data/goodreads_book_series_cleaned.csv"

    #make queries to get indexed queries
    series_index_list = make_queries(series_filename,query_output_filename)
    series_index_list.reset_index(inplace=True,drop=True)
    series_index_list.reset_index(inplace=True)
    series_index_list.rename(columns={'index':'series_index'},inplace=True)
    
    
    #make eval file    
    eval_output_filename=""
    if(cfg_d['duplicates'] == 'True'):
        eval_output_filename="book_title_qrels.txt"
    else:
        eval_output_filename="book_title_qrels_no_duplicates.txt"
    
    
    #now, get evaluation for queries from series assignments
    valid_series_list = pd.read_csv(series_filename)
    valid_series_list['series_id']= valid_series_list['series_id'].astype(str)
    
    valid_series_list = valid_series_list.merge(series_index_list,
                                                how = 'right',
                                                on='series_title')
    
    #allocate df to store books
    books_df = pd.DataFrame([['','','']]*2360000,columns=['book_id','book_title','series_id'])
    
    c=0
    
    popular_shelves = {}
    author_roles = {}
    
    book_series_list = {}
    with gzip.GzipFile(books_filename, 'r',) as fin:
        while c < len(books_df) - 1:
            try:
                line = fin.readline()
                if c%1000==0:
                    print(c)
                info=json.loads(line.decode('utf-8'))
                #data_lan.append(info)
                
                books_df.iloc[c]['book_id'] = info['book_id']
                books_df.iloc[c]['series_id'] = ' '.join(info['series'])
                books_df.iloc[c]['book_title'] = info['title']
                
                     
            except:
                pass
                       
            c+=1
    
    
    books_df = books_df.loc[books_df['book_id'] != '']
    books_df.reset_index(inplace=True,drop=True)
    books_df.reset_index(inplace=True)
    books_df.rename(columns={'index':'book_index'},inplace=True)
    
    
    series_split_df = books_df['series_id'].str.split(' ',expand=True)
    
    books_df = books_df.merge(series_split_df,
                             left_index=True,
                             right_index=True,
                             how='inner')
    
    
    series_df = pd.melt(books_df, id_vars=['book_id','book_index','book_title'], 
                        value_vars=series_split_df.columns.values,
                        value_name='series_id')
    
    series_df['series_id'] = series_df['series_id'].replace({None:''})
    
    
    series_df = series_df.loc[series_df['series_id'] != '']
    
    
    
    series_df = series_df.merge(valid_series_list,on='series_id',how='inner')
    series_df.sort_values(['series_index','book_index'],inplace=True)
    series_df['relevance'] = 1
    
    
    series_df[['series_index','book_index','relevance']].drop_duplicates().to_csv(eval_output_filename,
             header=False,index=False,sep=' ')

    #series_df.to_csv('full_book_series_table.csv',index=False)
    

        
    
    

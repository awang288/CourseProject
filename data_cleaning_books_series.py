#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import gzip
import json
from langdetect import detect
import metapy
import pandas as pd
import csv

###cleans books and series data###
###saves all cleaned book data and another version without duplicate book titles###

def clean_series(input_filename,output_filename):
    
    print('cleaning series data')
    c=0
    with gzip.GzipFile(input_filename, 'r',) as fin:
        data_lan = []
        for line in fin:
            
            c+=1
            #line = fin.readline()
            
            if c%1000==0:
                print(c/1000)
            info=json.loads(line.decode('utf-8'))
            try: 
                #print(info)
                if detect(info['title'])=='en':
                    data_lan.append([info['title'],
                                     info['series_works_count'],
                                     info['series_id']
                                    ])
            except: 
                pass    

    
    with open(output_filename, 'w') as f:
      
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow(['series_title','series_works_count','series_id'])
        write.writerows(data_lan)

    
    
def clean_book_metadata(input_filename,output_filename,output_filename_no_duplicates):
    

    print('cleaning book data')
    c=0

    popular_shelves = {}
    author_roles = {}
    
    data_lan = []
    book_titles = []
    with gzip.GzipFile(input_filename, 'r',) as fin:
        #with gzip.open(output_filename, 'w') as f:
        while c < 2360000:
            #for line in fin:
            line = fin.readline()
            c+=1
            if c%1000==0:
                print(c)
            info=json.loads(line.decode('utf-8'))
            try:
                if ((info['language_code']=='eng') |(info['country_code'] == 'US') ):
                    if detect(info['title'])=='en':
                        #print(info)
                        new_info={}
                        new_info['title']=info['title']
                        new_info['book_id']=info['book_id']
                        new_info['authors']=info['authors']
                        new_info['series'] = info['series']
                        new_info['similar_books']=info['similar_books']
                        new_info['popular_shelves'] = info['popular_shelves']
                        new_info['description'] = info['description'].lower().replace(',','')
                        new_info['publication_year'] = info['publication_year']
                        new_info['rating']=info['average_rating']
                        new_info['ratings_count']=info['average_rating']
                        new_info['text_reviews_count']=info['text_reviews_count']
                        new_info['num_pages'] = info['num_pages']
                        #print((json.dumps(new_info)+'\n').encode('utf-8'))
                        data_lan.append(new_info)
                        book_titles.append(new_info['title'])
                        
                        if(new_info['authors']):
                            for author_item in new_info['authors']:
                                if author_item['role'] in author_roles:
                                    #print('role %s exists!'%author_item['role'])
                                    author_roles[author_item['role']] += 1
                                else:
                                    #print('role %s added!'%author_item['role'])
                                    author_roles[author_item['role']] = 1
                        if(new_info['popular_shelves']):
                            for shelf_item in new_info['popular_shelves']:
                                if shelf_item['name'] in popular_shelves:
                                    #print('shelf %s exists!'%shelf_item['name'])
                                    popular_shelves[shelf_item['name']] += 1
                                else:
                                    #print('shelf %s added!'%shelf_item['name'])
                                    popular_shelves[shelf_item['name']] = 1
            except:
                pass
            

    
    with gzip.open(output_filename, 'w') as f:
        content=[]
        for data in data_lan:
            content.append((json.dumps(data)+'\n').encode('utf-8'))
        f.writelines(content)
        
        
    #identify which entries are duplicates
    df = pd.DataFrame(book_titles,columns=['book_title'])
    first_df = df.groupby('book_title').agg(first_index=('index',min))
    
    df = df.merge(first_df,how='left',on='book_title')
    df['unique'] = df['index'] == df['first_index']
    
    unique_booktitle = df['unique'].to_numpy()

    with gzip.open(output_filename_no_duplicates, 'w') as f:
        content=[]
        for i in range(len(data_lan)):
            data = data_lan[i]
            if unique_booktitle[i]:
                content.append((json.dumps(data)+'\n').encode('utf-8'))
        f.writelines(content)
        
    
    
    print(author_roles)
    print(popular_shelves)

    with open('author_roles.txt', 'w') as f:
        for role in author_roles:
            f.write(role)
            f.write('/n')    

    with open('popular_shelves.txt', 'w') as f:
        for shelf in popular_shelves:
            f.write(shelf)
            f.write('/n')


if __name__=="__main__":

    clean_book_metadata("data/goodreads_books.json.gz",
                        "data/goodreads_books_cleaned.json.gz",
                        "data/goodreads_books_cleaned_no_duplicates.json.gz")
    
    clean_series("data/goodreads_book_series.json.gz","data/goodreads_book_series_cleaned.csv")
    
    
    
    
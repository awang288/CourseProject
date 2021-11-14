#adapted from data_cleaning.ipynb
import gzip
import json
from langdetect import detect
import csv
import os

RANGE = 5000000


def write_file(output_filename, data_lan):

    with open(output_filename, 'w') as f:
      
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow(['user_id','book_id','review_id','review_text','rating','date'])
        write.writerows(data_lan)

if __name__=="__main__":
    input_filename="goodreads_reviews_dedup.json.gz"#"goodreads_reviews_poetry.json.gz"
    output_filename="reviews_cleaned/goodreads_reviews_dedup_cleaned_%s.csv"#"goodreads_reviews_poetry_cleaned.json.gz"


    c=0

    with gzip.GzipFile(input_filename, 'r',) as fin:
        data_lan = []
        print(RANGE)
        while c < RANGE+6000000:
            c+=1
            line = fin.readline()
            if ((c > RANGE) & (c <= RANGE+6000000) & 
                (((not os.path.exists(output_filename%(1+int(c/1000)))) & (c%1000!=0)) |
                 ((not os.path.exists(output_filename%(int(c/1000)))) & (c%1000==0)) )):
                
                if c%1000==0:
                    #write by each 1000 reviews
                    if (not os.path.exists(output_filename%(int(c/1000)))):
                        write_file(output_filename%(int(c/1000)),data_lan)
                        print(c/1000)
                        data_lan=[]
                info=json.loads(line.decode('utf-8'))
                try: 
                    if detect(info['review_text'][:50])=='en':
                        #print(info)
                        data_lan.append([info['user_id'],
                                         info['book_id'],
                                         info['review_id'],
                                         info['review_text'].lower().replace(',',''),#removes all commas
                                         info['rating'],
                                         info['date_updated']
                                        ])
                
                except: 
                    pass    


import gzip
import json
import csv


def write_file(output_filename, data_lan):

    with open(output_filename, 'w') as f:
      
        # using csv.writer method from CSV package
        write = csv.writer(f)
        write.writerow(['series_title','series_works_count','series_id'])
        write.writerows(data_lan)

if __name__=="__main__":
    input_filename="goodreads_book_series.json.gz"#"goodreads_reviews_poetry.json.gz"
    output_filename="goodreads_book_series_cleaned.csv"#"goodreads_reviews_poetry_cleaned.json.gz"


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
                data_lan.append([info['title'],
                                 info['series_works_count'],
                                 info['series_id']
                                ])
            except: 
                pass    

    write_file(output_filename,data_lan)
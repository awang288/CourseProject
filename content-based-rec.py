import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# import data
books = pd.read_json("poetry_data/goodreads_books_poetry.json", lines = True)
reviews = pd.read_json("poetry_data/goodreads_reviews_poetry.json", lines = True)

# merge both books and reviews based on book_id
books_and_reviews = pd.merge(reviews, books, on=['book_id'])

# filter out only the english books
books_and_reviews = books_and_reviews.loc[books_and_reviews['language_code'].isin(['en-US', 'eng', 'en-GB', 'en-CA'])]
# make one entry per book
books_and_reviews = books_and_reviews.groupby(['book_id', 'title'], as_index=False).agg(' '.join)
# add extra column of only text (title, description, and review text)
books_and_reviews['text_data'] = books_and_reviews['title'] + books_and_reviews['description'] + books_and_reviews['review_text'] 

# initialize vectorizer from sklearn and remove stopwords
tf_idf = TfidfVectorizer(stop_words='english')
# generate vectors for text data
vectors = tf_idf.fit_transform(books_and_reviews['text_data'])
# calculate cosine similarities (matrix)
cosine_sim_matrix = linear_kernel(vectors, vectors)

# decision module
indices = pd.Series(books_and_reviews.index, index=books_and_reviews['book_id']).drop_duplicates()
#function to get recommendation based on a book_id
def recommend_book(book_id):
    # get the index of the book we're referencing/comparing to for recommendations
    index = indices[book_id]
    
    # get pairwise cosine similarities
    cosine_sim = list(enumerate(cosine_sim_matrix[index]))
    
    # sort on cosine similarity scores (descending order)
    cosine_sim = sorted(cosine_sim, key=lambda x: x[1], reverse=True)
    
    # get the top 10 books
    cosine_sim = cosine_sim[1:11]
    top_10 = [score[0] for score in cosine_sim]
    return top_10

#select a random book to use and generate recommendations on
random_book = books_and_reviews.sample()
book_selected = random_book['book_id'].values[0]
print('=================book selected=================')
print(random_book['title'].values[0])

print('=================testing - generating recommendations=================')
# pass the book_id to recommend_book to get the top 10 book recommendations
top_10 = recommend_book(book_selected)
for book_index in top_10:
    book = books_and_reviews.iloc[book_index]
    id = book.book_id
    print(book.title)
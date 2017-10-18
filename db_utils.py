import psycopg2


def clean_db(db_params):

    conn = None

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        cur.execute('DELETE FROM words; DELETE FROM article;')

        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError):
        raise

    finally:
        if conn is not None:
            conn.close()


def write_articles_to_db(db_params, article_params):
    insert_article_sql = '''INSERT INTO article(url, date, number_of_words, number_of_paragraphs) 
                            VALUES(%s, %s, %s, %s) RETURNING id;'''
    insert_words_sql = 'INSERT INTO words(words, article_id) VALUES(%s, %s);'
    conn = None

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # rewrite data in the table
        cur.execute(insert_article_sql, (
            article_params['url'],
            article_params['date'],
            article_params['number_of_words'],
            article_params['number_of_paragraphs']
        ))

        article_id = cur.fetchone()[0]

        cur.execute(insert_words_sql, (
            article_params['words'],
            article_id
        ))

        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError):
        raise

    finally:
        if conn is not None:
            conn.close()


def fetch_articles_from_db(db_params, filter_params):

    filter_num_words = filter_params['number_of_words_interval']
    filter_words = filter_params['should_contain_words']
    filter_num_paragraphs = filter_params['number_of_paragraphs_interval']

    filter_articles_sql = \
        '''SELECT article, ARRAY(SELECT UNNEST(words) INTERSECT SELECT UNNEST(%s))
           FROM article INNER JOIN words ON article.id=words.article_id 
           WHERE (number_of_words BETWEEN %s AND %s) 
           AND (%s && words)
           AND (number_of_paragraphs BETWEEN %s AND %s);'''
    conn = None

    try:
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        cur.execute(filter_articles_sql, (
            filter_words,
            filter_num_words[0], filter_num_words[1],
            filter_words,
            filter_num_paragraphs[0], filter_num_paragraphs[1]
        ))

        article_items = cur.fetchall()

        conn.commit()
        cur.close()

    except (Exception, psycopg2.DatabaseError):
        raise

    finally:
        if conn is not None:
            conn.close()

    return article_items

import json
import requests

from bs4 import BeautifulSoup


def get_criteria(criteria_file_name):
    with open(criteria_file_name) as criteria_file:
        return json.load(criteria_file)


def write_report(data, report_file_name):
    with open(report_file_name, 'w') as report_file:
        json.dump(data, report_file)


def fetch_articles_from_site(article_to_parse):

    article_url = article_to_parse.find('a', attrs={'class': 'fusion-read-more'})['href']

    article_details_response = requests.get(article_url)

    parsed_article_html = BeautifulSoup(article_details_response.text, 'html.parser')
    post_content = parsed_article_html.find('div', attrs={'class': 'post-content'})

    words_list = post_content.text.lower().split()
    num_words = len(words_list)
    num_paragraphs = len(post_content.find_all('p'))

    return {
        'url': article_url,
        'words': words_list,
        'number_of_words': num_words,
        'number_of_paragraphs': num_paragraphs
    }


def serialize_article_from_db_row(row_article):

    row_article = row_article.strip('(').strip(')').split(',')

    return {
        'url': row_article[1].strip('"').strip(),
        'date': row_article[2].split()[0].strip('"'),
        'number_of_words': int(row_article[3]),
        'number_of_paragraphs': int(row_article[4])
    }

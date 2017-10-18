import argparse
import itertools
import requests

import db_utils
import settings
import utils

from bs4 import BeautifulSoup
from dateutil import parser as dt_parser


def main():

    parser = argparse.ArgumentParser(description='Process input information for web scrapping.')
    parser.add_argument('action', type=str, choices=['scrape', 'report'], help='define the scrapping action')
    parser.add_argument('-c', default='criteria.json', help='criteria file to scrapping against')
    parser.add_argument('-o', default='report.json', help='report file generated against specified criteria')
    parser.add_argument('--url', default=settings.ROOT_URL, help='url to scrape information from')

    args = parser.parse_args()

    criteria_data = utils.get_criteria(args.c)

    if args.action == 'scrape':

        criteria_cut_off_date = dt_parser.parse(criteria_data['cut_off_date'])

        response = requests.get(args.url)

        parsed_html = BeautifulSoup(response.text, 'html.parser')
        articles = parsed_html.body.find_all('div', attrs={'class': 'post'})

        db_utils.clean_db(settings.DATABASE)

        for article in articles:
            article_publish_date_str = article.find('p', attrs={'class': 'fusion-single-line-meta'}).contents[4].text
            article_publish_date = dt_parser.parse(article_publish_date_str)

            if article_publish_date < criteria_cut_off_date:
                continue
            else:
                article_data = utils.fetch_articles_from_site(article)
                article_data['date'] = article_publish_date

                db_utils.write_articles_to_db(settings.DATABASE, article_data)

    if args.action == 'report':

        fetched_db_data = db_utils.fetch_articles_from_db(settings.DATABASE, criteria_data)

        serialized_data = {
            'criteria': criteria_data,
            'common_words': list(itertools.chain(*(row[1] for row in fetched_db_data))),
            'articles': [utils.serialize_article_from_db_row(row[0]) for row in fetched_db_data]
        }

        utils.write_report(serialized_data, args.o)


if __name__ == "__main__":
    main()

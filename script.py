import json
import time
from re import compile, sub

from pydantic import ValidationError
from requests import get
from models import HeaderSection, TitleSection, LeadSection, TextSection, ImageSection, MediaSection, Article


def download_from_api():
    while True:
        LIST_URL = 'https://mapping-test.fra1.digitaloceanspaces.com/data/list.json'

        response = get(LIST_URL)
        response = response.json()

        for item in response:
            article_id = item['id']
            DETAILS_URL = f'https://mapping-test.fra1.digitaloceanspaces.com/data/articles/{article_id}.json'
            MEDIA_URL = f'https://mapping-test.fra1.digitaloceanspaces.com/data/media/{article_id}.json'
            try:
                details_response = get(DETAILS_URL).json()

                details_response['pub_date'] = details_response['pub_date'].replace(";", ":")
                details_response['pub_date'] = list(details_response['pub_date'])
                details_response['pub_date'][10] = " "
                details_response['pub_date'] = ''.join(details_response['pub_date'])

                article = Article(id=details_response['id'], original_language=details_response['original_language'],
                                  publication_date=details_response['pub_date'], sections=[], url=DETAILS_URL)

                article.thumbnail = details_response['thumbnail']
                article.categories = details_response['category']
                article.tags = details_response['tags']
                article.author = details_response['author']
                article.modification_date = details_response['mod_date']

                print(article.id)
                print(article.url)
                print(article.thumbnail)
                print(article.categories)
                print(article.tags)
                print(article.author)
                print(article.publication_date)
                print(article.modification_date)

                html_tags = compile('<.*?>')

                for section in details_response['sections']:
                    section['text'] = sub(html_tags, '', section['text'])
                    if section['type'] == 'title':
                        model_section = TitleSection(text=section['text'], type='title')
                        article.sections.append(model_section)
                        print(model_section.text)
                    elif section['type'] == 'text':
                        model_section = TextSection(type='text', text=section['text'])
                        print(model_section.text)
                        article.sections.append(model_section)
                    elif section['type'] == 'header':
                        model_section = HeaderSection(type='header', text=section['text'], level=section['level'])
                        print(model_section.text)
                        article.sections.append(model_section)
                    elif section['type'] == 'lead':
                        model_section = LeadSection(type='lead', text=section['text'])
                        print(model_section.text)
                        article.sections.append(model_section)
                    elif section['type'] == 'image':
                        pass
                    elif section['type'] == 'media':
                        pass
                    else:
                        print('unknown type of section!')
            except json.decoder.JSONDecodeError as e:
                print("Error!!!:", e)
            except KeyError as e:
                print(e)
            except ValidationError as e:
                print(e)
            try:
                media_response = get(MEDIA_URL).json()
                for section in media_response:
                    if section['type'] == 'image':
                        model_section = ImageSection(type='image', url=section['url'], alt=section['alt'],
                                                     caption=section['caption'], source=section['source'])
                        article.sections.append(model_section)
                        print(model_section.alt)
                    elif section['type'] == 'media':
                        model_section = MediaSection(type='media', id=section['id'], url=section['url'],
                                                     thumbnail=section['thumbnail'], caption=section['caption'],
                                                     author=section['author'], publication_date=section['pub_date'],
                                                     modification_date=section['mod_date'],
                                                     duration=section['duration'])
                        article.sections.append(model_section)
                        print(model_section.thumbnail)
                    else:
                        print('unknown type of media!')
            except json.decoder.JSONDecodeError as e:
                print(e)
            except KeyError as e:
                print(e)
            except ValidationError as e:
                print(e)
            print(article.sections)
        time.sleep(300)


download_from_api()

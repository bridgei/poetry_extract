from bs4 import BeautifulSoup
from requests_html import HTMLSession
from dataclasses import dataclass
import re

IS_VERBOSE = False
BASEURL = 'https://suchness1.wordpress.com/'
URL = f'{BASEURL}2023/10/29/toadstools-on-a-beech-stump/'
CAT_POETRY_URL = f'{BASEURL}category/poetry/'
DATALIB='../data/'
ALPHANUMERIC = r'[^A-Za-z0-9_]+'
ELLIPSIS_ESCAPE = '\u2026'


@dataclass
class Poem_Data:
    poem_title: str
    poem_verses: str = ''
    poem_context: str = ''
    poem_url: str = ''
    poem_file: str = ''


def get_poem_context(par_verses: list):
    '''collates contextual text that may or may not accompany a given poem'''
    this_verses = par_verses[0].fetchPreviousSiblings()
    this_context=''
    for this_item in this_verses:
        this_context= f'{this_context}{this_item.getText()}\n'
    return this_context

def collate_poem(par_session, par_url):
    '''Returns the poem_page title and body as a Poem_Data dataclas object'''

    this_poem = ''
    poem_data = Poem_Data
    this_title = ''
    this_context = ''
    this_session = par_session

    # get web page
    this_page = this_session.get(par_url)
    soup = BeautifulSoup(this_page.content, 'html.parser')
    for br in soup.select("br"):
        br.replace_with("\n")

    # get all poem_page verses from page
    these_verses = soup.find_all('pre')

    # Collate text from all verse elements
    if len(these_verses)>0:
        for v in these_verses:
            this_poem = f'{this_poem}{v.getText()}'

    # Get any none verse content such as poem_page context and-or preambles
    this_context = get_poem_context(these_verses)

    # Get poem title text
    this_title = soup.find_all('title')[0].getText().strip()
    this_title = str(this_title.replace(' – Suchness1',''))

    # Set Poem_Data object
    poem_data.poem_verses = this_poem
    poem_data.poem_context = this_context
    poem_data.poem_title = this_title.strip()
    # Replace any elipsis characters, remove lead/trail spaces and then replace remaining spaces with underscores
    poem_data.poem_file = (this_title.replace(ELLIPSIS_ESCAPE,'').strip().replace(' ','_')).strip()
    # Remove any non-alphanumeric characters (excluding underscores)
    poem_data.poem_file =    re.sub(ALPHANUMERIC, '', poem_data.poem_file).strip()
    poem_data.poem_url = par_url

    return poem_data


def collate_poem_list(par_session, par_url):
    this_list = []
    session = par_session
    r = session.get(par_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    poem_list_pages = soup.find_all( 'div', {"class": 'wp-block-query-pagination-numbers'})
    x=poem_list_pages[0].text.split('\n')
    print(len(x))
    num_poem_pages = int(x[len(x)-1])

    print(f'Poem pages = {num_poem_pages}')

    for i in range(num_poem_pages):
        if i>0:
            # get next url
            r = session.get(f'{par_url}page/{str(i + 1)}')
            soup = BeautifulSoup(r.content, 'html.parser')
        poem_titles = soup.find_all('h2', {"class": "wp-block-post-title"})
        for t in poem_titles:
            this_list.append(t.find("a").get('href'))

    print(f'There are {len(this_list)} poems to process')
    return(this_list)


def write_poem_files(par_poem_data_list, par_type : str = 'txt'):
    num_files_written = 0

    for this_poem in par_poem_data_list:
        if len(f'{this_poem.poem_verses}') > 0:
            print(f'Processing = {this_poem.poem_title}')
            with open(f'{DATALIB}poems/{this_poem.poem_file}.{par_type}','w') as of:
                of.write(f'{this_poem.poem_title}\n\n')
                of.write(f'{this_poem.poem_context}\n\n')
                of.write(f'{this_poem.poem_verses}\n\n')
                of.write(f'\n\n{this_poem.poem_url}')
            of.close()
            num_files_written = num_files_written + 1
        else:
            print(f'Empty File = {poem_data.poem_title} page = {this_link}')

    print(f'Process stopped. Wrote {num_files_written} files')


def main (url):
    """For each poem in the index pages, extract its link,
    then collate the poem and write to a txt file"""

    this_session = HTMLSession()

    poem_links = collate_poem_list(par_session = this_session, par_url=CAT_POETRY_URL)
    num_files_written = 0
    par_type  = 'txt'
    poem_data_list = []
    for this_link in poem_links:
        #my_poem_data = Poem_Data
        poem_data_list.append(collate_poem(par_session=this_session, par_url=this_link))
#        if len(f'{poem_data.poem_verses}')>0:
#            print(f'Processing = {poem_data.poem_title}')
#            with open(f'{DATALIB}poems/{poem_data.poem_file}.{par_type}','w') as of:
#                of.write(f'{poem_data.poem_title}\n\n')
#                of.write(f'{poem_data.poem_context}\n\n')
#                of.write(f'{poem_data.poem_verses}\n\n')
#                of.write(f'\n\n{poem_data.poem_url}')
#            of.close()
#            num_files_written = num_files_written + 1
#        else:
#            print(f'Empty File = {poem_data.poem_title} page = {this_link}')
    if len(poem_data_list)>0:
        write_poem_files(poem_data_list, par_type)
#    print(f'Process stopped. Wrote {num_files_written} files')
    print('Stopped')

if __name__ ==  "__main__":
  main(URL)

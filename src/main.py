from bs4 import BeautifulSoup
from requests_html import HTMLSession
from dataclasses import dataclass
from typing import Optional
import re

IS_VERBOSE = False
BASEURL = 'https://suchness1.wordpress.com/'
URL = f'{BASEURL}2023/10/29/toadstools-on-a-beech-stump/'
CAT_POETRY_URL = f'{BASEURL}category/poetry/'
DATALIB='../data/'
ALPHANUMERIC = r'[^A-Za-z0-9_]+'
ELLIPSIS_ESCAPE = '\u2026'


@dataclass(order=True)
class Poem_Verse:
    Poem_Lines: list = None


@dataclass(order=True)
class Poem_Data:
    poem_title: str
    poem_context: Optional[list] = None
    poem_verses: list = None
    poem_url: str = ''
    poem_file: str = ''

    def as_markdown(self):
        newline = '  \n'
        response = f'# {self.poem_title}{newline}'
        for c in self.poem_context:
            if len(c.strip())>0:
                response = f'{response}> {c}{newline}'
        response = response + '\n'
        for v in self.poem_verses:
            response = f'{response}{newline.join(v)}{newline}{newline}'
        return response

    def as_text(self):
        newline = '\n'
        response = f'{self.poem_title}{newline}'
        for c in self.poem_context:
            if len(c.strip())>0:
                response = f'{response}> {c}{newline}'
        response = response + '\n'
        for v in self.poem_verses:
            response = f'{response}{newline.join(v)}{newline}{newline}'
        return response

def sanitise_filename(par_text) -> str:
    # Get sanitised file name
    # Replace any elipsis characters, remove lead/trail spaces and then replace remaining spaces with underscores
    this_filename=''
    if len(par_text)>0:
        this_filename = (par_text.replace(ELLIPSIS_ESCAPE, '').strip().replace(' ', '_')).strip()
        # Remove any non-alphanumeric characters (excluding underscores)
        this_filename = re.sub(ALPHANUMERIC, '', this_filename).strip()
    return this_filename

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


    verses = this_poem.split('\n\n')
    verse_lines = []
    for v in verses:
        verse_lines.append(v.split('\n'))

    # Get any none verse content such as poem_page context and-or preambles
    this_context = get_poem_context(these_verses)

    # Get poem title text
    this_title = soup.find_all('title')[0].getText().strip()
    this_title = str(this_title.replace(' – Suchness1',''))

    # Set Poem_Data object
    poem_data = Poem_Data(poem_verses = verse_lines,
                          poem_context = this_context.split('\n'),
                          poem_title = this_title.strip(),
                          poem_file = sanitise_filename(this_title),
                          poem_url = par_url)
    #print(poem_data.as_markdown())
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


def write_poem_file(par_poem_data:Poem_Data, par_type):

    file_suffix = {'txt': 'txt', 'md': 'md'}

    this_poem = par_poem_data
    this_filename = f'{this_poem.poem_file}.{file_suffix[par_type]}'
    result = f'Created -{this_filename}'
    if len(f'{this_poem.poem_verses}') > 0:
        print(f'Processing = {this_poem.poem_title}')

        with open(f'{DATALIB}poems/{this_filename}','w') as of:

            match par_type:
                case 'md':
                    of.write(this_poem.as_markdown())
                case 'txt':
                    of.write(this_poem.as_text())
                case _:
                    result = f'Unknown type {par_type} for {this_filename}'

        of.close()
        #
        #num_files_written = num_files_written + 1
    else:
        result = f'Empty File = {this_poem.poem_title} page = {this_poem.poem_url}'

    return result

def main(par_url, par_file_type):
    """For each poem in the index pages, extract its link,
    then collate the poem and write to a txt file"""

    this_session = HTMLSession()
    this_file_type = par_file_type

    my_poems = []

    poem_links = collate_poem_list(par_session = this_session, par_url=par_url)

    for t in poem_links:
        my_poems.append(collate_poem(par_session=this_session, par_url=t))

    for p in my_poems:
        print(write_poem_file(p, par_type=par_file_type))

    print('Stopped')


if __name__ ==  "__main__":


  main(CAT_POETRY_URL, 'txt')
  main(CAT_POETRY_URL, 'md')

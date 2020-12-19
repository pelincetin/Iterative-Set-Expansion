import requests
from bs4 import BeautifulSoup

black_list = [
	'[document]',
	'noscript',
    'style',
	'header',
	'html',
	'meta',
	'head',
	'input',
	'script',
    'footer'
]

def extract(url):
    result = requests.get(url)
    html_page = result.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)
    output=""

    print("Fetching text from url ...")
    for t in text:
        if t.parent.name not in black_list:
            output += '{} '.format(t)

    # TODO: this isn't viable for local development,
    # TODO: but truncate to 20,000 once we move to cloud VM. for now we will truncate to 8000 so our macbooks don't crash
    if len(output) > 20000:
        print("Truncating webpage text from size (num characters) " + str(len(output)) + " to 20000 ...")
    output = output[:20000]

    print("Webpage length (num characters): " + str(len(output)))
    print("Annotating the webpage using[tokenize, ssplit, pos, lemma, ner] annotators...")
    return output
from gazpacho import get, Soup
from bs4 import BeautifulSoup
from pathlib import Path
import requests
import pypandoc

novel_url = "https://truyenyy.vip/truyen/dinh-cap-khi-van-lang-le-tu-luyen-ngan-nam/"
resp_html = get(novel_url)
html = Soup(resp_html)

end_chapter_url = html.find("a", {'class': 'flex-primary'}, partial=False, mode='first').attrs["href"]
total_chapter = int(end_chapter_url[end_chapter_url.rfind("-")+1:].split('.html')[0])
prefix_url = "https://truyenyy.vip/truyen/"
novel_name = end_chapter_url.split("/")[-2]
novel_name_url = novel_name + '/'

def get_title_html(soup):
    return soup.find('h2', {'class': 'heading-font mt-2'})

def get_content_html(url, chapter):
    resp = get(url)
    bf_content_html = BeautifulSoup(resp, features="lxml").find("div", {"id": "inner_chap_content_1"})
    bf_title_html = get_title_html(BeautifulSoup(resp, features="lxml")).getText()
    chapter_title = f'Chương {chapter}: {bf_title_html}'
    return (chapter_title, str(bf_content_html))

def get_metadata(url):
    resp = get(url)
    soup = BeautifulSoup(resp, features="lxml")
    title = soup.find("h1", {"class": "name"}).getText()
    author = soup.find("div", {"class": "author mb-3"}).find("a").getText()
    description = soup.find("section", {"id": "id_novel_summary"}).getText()
    cover_img_url = soup.find("a", {"class": "cover position-relative"}).img['data-src']
    cover_img_path = './' + url.split("/")[-2] + '.png'
    cover_img = requests.get(cover_img_url)
    with open(cover_img_path, 'wb') as f:
        for chunk in cover_img:
            f.write(chunk)
    return (title, author, description, cover_img_path)

def get_chapter_title(url):
    resp = get(url)
    soup = BeautifulSoup(resp, features="lxml")
    return soup.find("h1", {"class": "name"}).getText()

chapter_file_list = []
(title, author, description, cover_img_path) = get_metadata(novel_url)

for chapter in range(1, 15):
    chapter_url = prefix_url + novel_name_url + f'chuong-{chapter}.html'
    (chapter_title, chapter_content) = get_content_html(chapter_url, chapter)
    pypandoc.convert_text(chapter_content, 'epub', 'html', extra_args=[f'--metadata=title:{chapter_title}'], outputfile=f"./output/{str(chapter).zfill(6)}.epub")
    chapter_file_list.insert(0, f"./output/{str(chapter).zfill(6)}.epub")

print(chapter_file_list)

pypandoc.convert_file(chapter_file_list, 'epub', 'epub', extra_args=[f'--metadata=title:{title}', f'--metadata=author:{author}', f'--metadata=description:{description}'], outputfile=f"{novel_name}.epub")
from gazpacho import get, Soup
from bs4 import BeautifulSoup
from tqdm import tqdm
from colorama import init

import requests, subprocess, argparse
init()

def get_title(soup):
    return soup.find('h2', {'class': 'heading-font mt-2'})

def get_content_html(url, chapter):
    try:
        resp = get(url)
    except Exception:
        return ("fail", None, None)
    soup = BeautifulSoup(resp, features="lxml")
    bf_content_html = soup.find("div", {"id": "inner_chap_content_1"})
    bf_title_html = get_title(soup).getText() if get_title(soup) is not None else ""
    chapter_title = f'Chương {chapter}: {bf_title_html}'
    return ("success", f'<h1>{chapter_title}</h1>\n' + str(bf_content_html))

def get_metadata(url):
    resp = get(url)
    soup = BeautifulSoup(resp, features="lxml")
    title = soup.find("h1", {"class": "name"}).getText()
    author = soup.find("div", {"class": "author mb-3"}).find("a").getText()
    description = soup.find("section", {"id": "id_novel_summary"})
    cover_img_url = soup.find("a", {"class": "cover position-relative"}).img['data-src']
    cover_img_path = url.split("/")[-2] + '.png'
    cover_img = requests.get(cover_img_url)
    with open(cover_img_path, 'wb') as f:
        for chunk in cover_img:
            f.write(chunk)
    return (title, author, description, f'<h1>Giới thiệu</h1>\n<p>Tác giả: <i>{author}</i><p>\n' + str(description) + '\n', cover_img_path)

def get_chapter_title(url):
    resp = get(url)
    soup = BeautifulSoup(resp, features="lxml")
    return soup.find("h1", {"class": "name"}).getText()

def append_chapter_content_to_html(content, file_path):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(f"{content}\n")
    f.close()

def get_all_chapter_content(novel_url, start_chapter, end_chapter):
    resp_html = get(novel_url)
    html = Soup(resp_html)

    end_chapter_url = html.find("a", {'class': 'flex-primary'}, partial=False, mode='first').attrs["href"]
    total_chapter = int(end_chapter_url[end_chapter_url.rfind("-")+1:].split('.html')[0])
    if end_chapter > total_chapter:
        end_chapter = total_chapter
    prefix_url = "https://truyenyy.vip/truyen/"
    novel_name = end_chapter_url.split("/")[-2]
    novel_name_url = novel_name + '/'

    (title, author, description, metadata, cover_img_path) = get_metadata(novel_url)

    # delete content before append
    open(f'./{novel_name}.html', 'w').close()
    append_chapter_content_to_html(metadata, f'./{novel_name}.html')

    print(f"Downloading... \n\033[95mTotal chapter: {total_chapter}\tStart from chapter: {start_chapter}\tto chapter: {end_chapter}")

    pbar = tqdm( unit="chapter", total=(end_chapter - start_chapter + 1), ascii=True, desc=f'\033[93mProgress', colour="green" )

    for chapter in range(start_chapter, end_chapter + 1):
        chapter_url = prefix_url + novel_name_url + f'chuong-{chapter}.html'
        (status, chapter_content) = get_content_html(chapter_url, chapter)
        if status is "success":
            append_chapter_content_to_html(chapter_content, f'./{novel_name}.html')
            pbar.update(1)
        else:
            print(f"\033[91mAn error occur while getting chapter: {chapter}.")
            continue
    pbar.close()
    print('Converting...')
    subprocess.run(['pandoc', '--from=html', '--to=epub', f'{novel_name}.html', f'--metadata=title:{title}', f'--metadata=author:{author}', f'--metadata=description:{description}', f'--metadata=language:vi', f'--epub-cover-image={cover_img_path}', f'-o{novel_name}.epub'])

if(__name__ == "__main__"):
    # argparse
    parser = argparse.ArgumentParser(description="Truyenyy downloader")
    parser.add_argument("url", help="truyenyy url")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("--start", "-s", type=int, default=1, help="Start download from chapter")
    parser.add_argument("--end", "-e", type=int, default=1000000, help="End download until chapter")
    args = parser.parse_args()
 
    get_all_chapter_content(args.url, args.start, args.end)
    print("\033[92mAll completed!")
    
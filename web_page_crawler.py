import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re


# 定义一个函数来获取页面内容
def get_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 确保响应成功
        return response.text
    except Exception as e:
        print("Error fetching page:", e)
        return None


# 定义一个函数来解析页面内容并收集链接
def parse_page(page_content, base_url):
    if page_content is None:
        return set(), set(), set()

    soup = BeautifulSoup(page_content, 'lxml')
    links = set()
    external_resources = set()
    file_links = set()

    # 收集链接
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            full_url = urljoin(base_url, href)
            links.add(full_url)

            # 收集外部资源（脚本、样式表、图片等）
    for script in soup.find_all('script'):
        src = script.get('src')
        if src:
            full_url = urljoin(base_url, src)
            external_resources.add(full_url)

    for link in soup.find_all('link'):
        href = link.get('href')
        if href:
            full_url = urljoin(base_url, href)
            external_resources.add(full_url)

    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            full_url = urljoin(base_url, src)
            external_resources.add(full_url)

            # 收集文件链接
    for a in soup.find_all('a', href=True):
        link = a['href']
        if re.search(r'\.(doc|docx|pdf)$', link):
            full_url = urljoin(base_url, link)
            file_links.add(full_url)

    return links, external_resources, file_links


def web_crawler(start_url, internal_pages_visited_max, internal_links_filename='internal_links.txt',
                external_links_filename='external_links.txt'):
    visited_count = 0
    to_visit = {start_url}
    internal_domain = urlparse(start_url).netloc
    all_links_count = 0
    external_resources_count = 0
    file_links_count = 0
    internal_pages_count = 0
    internal_links_written = set()  # 用于记录已经写入文件的内部链接

    internal_links_file = open(internal_links_filename, 'w', encoding='utf-8')
    external_links_file = open(external_links_filename, 'w', encoding='utf-8')

    while to_visit and visited_count < internal_pages_visited_max:
        url = to_visit.pop()

        print("Visiting:", url, "  ", visited_count + 1)
        page_content = get_page(url)

        if page_content:
            visited_count += 1
            links, ext_res, files = parse_page(page_content, url)

            all_links_count += len(links)
            external_resources_count += len(ext_res)
            file_links_count += len(files)

            for link in links:
                link_domain = urlparse(link).netloc
                is_page_link = not bool(re.search(
                    r'\.(jpg|jpeg|png|gif|bmp|ico|svg|css|js|pdf|doc|docx|ppt|pptx|xls|xlsx|zip|rar|7z)(\?.*)?(#.*)?$',
                    link))

                if (link_domain == internal_domain and is_page_link and link not in to_visit
                        and link not in internal_links_written):
                    to_visit.add(link)
                    internal_links_file.write(link + '\n')  # 将内部页面链接写入文件
                    internal_links_written.add(link)  # 记录已写入的链接
                    internal_pages_count += 1

                elif link_domain != internal_domain:
                    external_links_file.write(link + '\n')  # 将外部链接写入文件

    internal_links_file.close()
    external_links_file.close()

    print("Website Statistics:")
    print("Total Pages Visited:", visited_count)
    print("Internal Pages:", internal_pages_count)
    print("Total Links Collected:", all_links_count)
    print("External Resources:", external_resources_count)
    print("Unique doc/docx/pdf files:", file_links_count)

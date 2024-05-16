from bs4 import BeautifulSoup as bs
import requests

link = 'https://www.ptt.cc/bbs/hotboards.html'
link2 = 'https://www.ptt.cc/'
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'

header = {'User-Agent':userAgent}

response = requests.get(link, headers=header)
soup = bs(response.content, 'html.parser')
element = soup.find_all('a', class_='board')
for i in element:
    t1 = i.find('div', class_='board-name').text
    t2 = i.get('href')
    print(t1, link2+t2, sep='\n', end='\n')

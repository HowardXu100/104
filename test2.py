from datetime import datetime
import csv, os, re
from bs4 import BeautifulSoup as bs
import requests

link = 'https://www.ptt.cc/bbs/Gossiping/index.html'
userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'
cookies = {'over18':'1'}
header = {'User-Agent':userAgent}
url = 'https://www.ptt.cc'
month = {'Jun':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':9, 'Oct':10, 'Nov':11, 'Dec':12}
extend = '<span class="article-meta-value">Gossiping</span>'

def getLink(num, lin):
    #取得列表的網址
    t1 = requests.get(lin, cookies=cookies, headers=header)
    t2 = bs(t1.content, 'html.parser')
    t3 = t2.find_all('a', class_='btn wide')
    return url + t3[num].get('href')

def getPage(lin):
    #取得網頁中所有標題的資訊
    response = requests.get(lin, cookies=cookies, headers=header)
    soup = bs(response.content, 'html.parser')
    container = soup.find_all('div', class_='title')
    return container

def getTitle(page):
    #取得此page的所有標題網址
    li = []
    for i in range(len(page)-1, -1, -1):
        try:
            t1 = page[i].find('a').get('href')
            li.append(url+t1)
        except:
            continue
            #可能有漏抓
    return li

def removeSpecial(Str):
    pattern = r'[\\/:\*\?"<>\|]'
    afterString = re.sub(pattern, '', Str)
    return afterString

def FixAuthor(author):
    t1 = str(author[0]) + extend +str(author[1])+str(author[2])
    t1 = bs(t1, 'html.parser').find_all('span', class_='article-meta-value')
    return t1

def getData(url):
    #取得文章的所有資訊
    response = requests.get(url, cookies=cookies, headers=header)
    soup = bs(response.content, 'html.parser')
    author = soup.find_all('span', class_='article-meta-value') #[作者, 分類, 標題, 時間]
    if len(author)==0:
        return False
    if len(author)!= 4:
        author = FixAuthor(author)
    article = soup.find('div', id='main-content') #
    s1 = article.text.split('--')
    s2 = s1[0].split('\n')
    st = [] #st為文章本體
    for i in range(1, len(s2)):
        st.append(s2[i])
    push = getPush(soup)

    succ = saveData(author, st, push)
    return succ

def getPush(soup):
    #收集所有的推
    t1 = soup.find_all('div', class_='push')
    li=[]
    for i in t1:
        a1 = i.find('span', class_='f3 hl push-userid')
        a2 = i.find('span', class_='f3 push-content')
        a3 = i.find('span', class_='push-ipdatetime')
        try:
            a3 = a3.text.split()
        except:
            continue
        try:
            a3 = a3[1]+' '+a3[2]
        except:
            print(a3)
            if a3 ==[]:
                continue
            elif len(a3)==1 and '.' in a3[0]:
                a3 = ''
            else:
                a3 = a3[0]+' '+a3[1]
            continue
        li.append([a1.text, a2.text, a3])
    return li

def checkTime(now, pub):
    t1 = pub[3].split(':')
    t2 = datetime(int(pub[4]), month[pub[1]], int(pub[2]), int(t1[0]), int(t1[1]), int(t1[2]))
    t2 = t2.timestamp()
    time = 7*24*60*60
    if now - t2 > time:
        print('大於七天')
        return False
    return True

def saveData(author, st, push):
    time = author[3].text.split()
    if checkTime(now, time):
        date = time[4]+' '+time[1]+' '+time[2]
        folder = 'ptt article/' + date
        if not os.path.exists(folder):
            os.mkdir(folder)
        artName = removeSpecial(author[2].text)
        fullName = artName + ' ' + author[0].text.split()[0]
        with open(folder + '/' + fullName + '.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
    
            writer.writerow(['作者', author[0].text])
            writer.writerow(['標題', author[2].text])
            writer.writerow(['時間', author[3].text])
            writer.writerow(['分類', author[1].text])
            writer.writerow([''])
            for i in st:
                writer.writerow([i])
                
            writer.writerow([''])       
            for i in push:
                writer.writerow([i[2], i[0], i[1]])
            print(artName)
        return True
    return False

if __name__ == '__main__':
    if not os.path.exists('ptt article'):
        os.mkdir('ptt article')
    nowdate = datetime.now()
    now = nowdate.timestamp()
    firLink = getLink(1, link)
    firLink = getLink(2, firLink)
    temp = getPage(firLink)
    tit = getTitle(temp)
    print(firLink)
    for i in tit:
        getData(i)
    LoopLink = getLink(1, firLink)
    print(LoopLink)
    conti = True
    count = 0
    while count<3:
        temp = getPage(LoopLink)
        tit = getTitle(temp)
        for i in tit:
            conti = getData(i)
            if conti == False:
                count+=1
                conti= True
                continue
        LoopLink = getLink(1, LoopLink)
        print(LoopLink)
    print('開始時間', nowdate)
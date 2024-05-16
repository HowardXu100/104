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

def getSoup(link):
    t1 = requests.get(link, headers=header, cookies=cookies)
    t1 = bs(t1.content, 'html.parser')
    return t1

def getBtnLink(num, link): #取得按鈕網址 {0:'最舊', 1:'上一頁", 2:'下一頁', 3:'最新'}
    t1 = getSoup(link)
    t2 = t1.find_all('a', class_='btn wide')
    return url +t2[num].get('href')

def getTitleLink(soup): #接收 sopu，回傳網址
    t1 = soup.find_all('div', class_='title')
    t2 = []
    for i in range(len(t1)-1, -1, -1):
        try:
            t3 = t1[i].find('a').get('href')
            t2.append(url + t3)
        except:
            print('Loss Link')
            continue
    return t2

def removeSpecial(Str):
    pattern = r'[\\/:\*\?"<>\|]'
    t1 = re.sub(pattern, '', Str)
    return t1

def FixAuthor(author):
    t1 = str(author[0]) + extend +str(author[1])+str(author[2])
    t1 = bs(t1, 'html.parser').find_all('span', class_='article-meta-value')
    return t1

def checkTime(now, pub): # now: timestamp, pub: ['Wed', 'Apr', '17', '23:39:22', '2024']
    t1 = pub[3].split(':')
    t2 = datetime(int(pub[4]), month[pub[1]], int(pub[2]), int(t1[0]), int(t1[1]), int(t1[2]))
    t2 = t2.timestamp()
    time = 7*24*60*60
    if now - t2 > time:
        print('大於七天，故不儲存')
        return False
    return True

def getArtInf(link):
    soup = getSoup(link)
    t1 = soup.find_all('span', class_='article-meta-value') #t1 = [作者, 分類, 標題, 時間]
    if len(t1) == 3:
        t1 = FixAuthor(t1)
    elif len(t1) == 0:
        return False
    time = t1[3].text.split()
    if checkTime(now, time):
        article = soup.find('div', id='main-content')
        t2 = article.text.split('--')
        t2 = ''.join(t2[:-1]) #t2 為文章本體
        t2 = t2.split('\n')
        t2 = '\n'.join(t2[1:])
        t3 = getPush(soup) #t3 為推的集合
        return [t1, t2, t3]            
    return False

def saveData(info):
    author = info[0]
    time = author[3].text.split()
    date = time[4] + '_' + time[1] + '_' + time[2]
    folder = 'ptt_article/' + date
    if not os.path.exists(folder):
        os.mkdir(folder)
    artName = removeSpecial(author[2].text)
    fullName = artName + '_' + author[0].text.split()[0]
    with open(folder + '/' + fullName + '.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['作者', author[0].text])
        writer.writerow(['標題', author[2].text])
        writer.writerow(['時間', author[3].text])
        writer.writerow(['分類', author[1].text])
        writer.writerow([''])

        writer.writerow([info[1]])            
        writer.writerow([''])       
        for i in info[2]:
            writer.writerow([i[2], i[0], i[1]])
        print(fullName)

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
            if a3 == []:
                li.append([a1.text, a2.text, ''])
                continue
        except:
            try:
                li.append([a1.text, a2.text, ''])
                continue
            except: 
                continue
        if '.' in a3[0]:
            a3 = ' '.join(a3[1:])
        else:
            a3 = ' '.join(a3)       
        li.append([a1.text, a2.text, a3])
    return li

if __name__ == '__main__':
    if not os.path.exists('ptt_article'):
        os.mkdir('ptt_article')
    now = datetime.now().timestamp()
    
    firLink = getBtnLink(1, link)
    firLink = getBtnLink(2, firLink)
    temp = getSoup(firLink)
    tit = getTitleLink(temp)
    print(firLink)
    for i in tit:
        t = getArtInf(i)
        if t == False:
            continue
        else:
            saveData(t)

    loopLink = getBtnLink(1, firLink)
    print(loopLink)
    count = 0
    while count < 3:
        temp = getSoup(loopLink)
        tit = getTitleLink(temp)
        for i in tit:
            t = getArtInf(i)
            if t == False:
                count += 1
                if count == 3:
                    break
                continue
            saveData(t)
        loopLink = getBtnLink(1, loopLink)
        print(loopLink)
    print('tarted time: ', datetime.fromtimestamp(now))

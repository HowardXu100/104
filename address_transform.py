import requests
from bs4 import BeautifulSoup as bs
import time

def clean_string(input_string):
    # 删除字符串开头的数字和尾部的换行符
    cleaned_string = input_string.lstrip('0123456789').rstrip('\n')
    return cleaned_string

url = 'https://zip5.5432.tw/zip/'
path = 'addr.csv'

with open(path, encoding='utf8') as f:
    file = f.readlines()

for i, j in enumerate(file):
    file[i] = clean_string(j)

newlist = []

for i in file:
    add = url + i
    r1 = requests.get(add)
    b1 = bs(r1.content, 'html.parser')
    s1 = b1.find('span', id='new-adrs6')
    s2 = s1.text
    print(s2)
    try:
        newlist.append(s2)
    except:
        newlist.append(i)
    time.sleep(3)
    
with open('newlist.csv', 'w', newline='\n', encoding='utf-8') as f:
    f.writelines(newlist)
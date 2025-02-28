import time
from lxml import etree
from selenium import webdriver
# 这个是浏览器自带的 不需要我们再做额外的操作
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def share_browser():
    # 初始化
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('‐‐disable‐gpu')
    # 这个路径是你谷歌浏览器的路径
    path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    chrome_options.binary_location = path
    browser = webdriver.Chrome(options=chrome_options)
    return browser


browser = share_browser()
timestampst = time.time()
local_time = time.localtime(timestampst)
browser.get('https://101.qq.com/#/hero-rank-fight')
time.sleep(1)
a = browser.find_element(By.XPATH, '//th/a[contains(text(),"胜率")]')
a.click()
text = browser.page_source
html = etree.HTML(text)
top3 = html.xpath('//*[@id="app"]//div[@class="item"]/img/@alt')
rank = html.xpath('//tbody[@class="table-body"]/tr/td[@class="hero"]/a/span/text()')
ls = top3 + rank[:7] + rank[-10:]
msg = f'*****分奴小助手******\n【胜率最高】:' \
      f'*{ls[0]}、*{ls[1]}、*{ls[2]}、*{ls[3]}、*{ls[4]}、*{ls[5]}、*{ls[6]}、*{ls[7]}、*{ls[8]}、*{ls[9]}\n-更新时间:' \
      f'{time.strftime("%m月%d日", local_time)}\n' \
      f'【胜率最低】:*{ls[10]}、*{ls[11]}、*{ls[12]}、*{ls[13]}、*{ls[14]}、*{ls[15]}、*{ls[16]}、*{ls[17]}、*{ls[18]}、*{ls[19]}' \
      f'(均低于45%)'

with open('rank.txt', 'w', encoding='utf-8') as file:
    file.write(msg)
print('完成')
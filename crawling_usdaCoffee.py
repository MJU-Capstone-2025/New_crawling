from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import time
import pandas as pd

options = Options()
# options.add_argument('--headless')  # 디버깅 시 끄기
options.add_argument('--start-maximized')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

driver = webdriver.Chrome(options=options)

all_data = []

for page in range(12):  
    url = f'https://www.usda.gov/search?query=coffee&commit=Search&page={page}'
    print(f"[페이지 {page}] 크롤링 중: {url}")
    driver.get(url)
    time.sleep(8)  

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    articles = soup.select("div.views-row")

    if not articles:
        print(f"⚠ 페이지 {page}에서 기사 항목을 찾을 수 없습니다. 건너뜁니다.")
        continue

    for article in articles:
        title_tag = article.select_one('div.node-teaser__content h2 a')
        date_tag = article.select_one('span.date.text-bold')

        if title_tag and date_tag:
            title = title_tag.get_text(strip=True)
            link = title_tag['href']
            full_url = f"https://www.usda.gov{link}" if link.startswith("/") else link

            raw_date = date_tag.get_text(strip=True)

            # 날짜 변환
            try:
                date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
            except ValueError:
                try:
                    date = datetime.strptime(raw_date, "%b %d, %Y").strftime("%Y-%m-%d")
                except:
                    date = raw_date

            all_data.append({
                "date": date,
                "title": title,
                "url": full_url
            })

driver.quit()

df = pd.DataFrame(all_data)

# 날짜 기준 내림차순 정렬 (최신순)
df = df.sort_values(by='date', ascending=False)
df.to_csv("usda_coffee_articles.csv", index=False, encoding='utf-8-sig')

print(f"수집 완료: 총 {len(df)}개 기사 → 'usda_coffee_articles.csv' 저장됨")


# In[ ]:





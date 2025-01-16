from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import requests
import datetime
import time
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from itertools import repeat

def get_genre(song_id) :
    url = 'https://www.melon.com/song/detail.htm?songId='+str(song_id)
    
    # 차단 방지
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
    req = requests.get(url, headers=headers)
    source = BeautifulSoup(req.text, 'lxml')
    
    # 장르 가져오기
    genre = source.select_one('#downloadfrm > div > div > div.entry > div.meta > dl > dd:nth-child(6)').get_text()
    return genre

def select_chart(driver, period, year, count, result_df):
        # 차트파인더 클릭
        driver.find_element(By.XPATH, '//*[@id="gnb_menu"]/ul[1]/li[1]/div/div/button/span').click()
        time.sleep(0.5)
        # 연간차트  클릭
        driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/h4[3]/a').click()
        time.sleep(0.5)
        #연대 선택
        driver.find_element(By.XPATH, f'//*[@id="d_chart_search"]/div/div/div[1]/div[1]/ul/li[{period}]/span/label').click()
        time.sleep(0.5)
        # 연도 선택
        driver.find_element(By.XPATH, f'//*[@id="d_chart_search"]/div/div/div[2]/div[1]/ul/li[{year}]/span/label').click()
        time.sleep(0.5)
        # 장르 선택
        driver.find_element(By.XPATH, '//*[@id="d_chart_search"]/div/div/div[5]/div[1]/ul/li[2]/span/label').click()
        time.sleep(0.5)
        # 검색버튼 클릭
        driver.find_element(By.XPATH, '//*[@id="d_srch_form"]/div[2]/button/span/span').click()
        time.sleep(0.5)

        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        # 노래 제목 가져오기
        song_list = [title.find('a').get_text(strip=True) for title in soup.find_all('div', attrs={'class': 'ellipsis rank01'})]
        # 가수 가져오기
        singer_list = [singer.get_text(strip=True) for singer in soup.find_all('span', attrs={'class': 'checkEllipsis'})]

        #노래 id 가져오기
        song_id_list=[]

        for id in soup.find_all('input',{'name':'input_check'}):
            song_id_list.append(id.get('value'))

        #장르 가져오기
        genre_list=[]
            
        for id in song_id_list:
            genre = get_genre(id)
            genre_list.append(genre)
        
        # 데이터프레임 생성
        df_year = 2024 - count
        rank_list = list(range(1, len(song_list) + 1))
        year_list = list(repeat(df_year, len(song_list)))

        df = pd.DataFrame({
            '연도': year_list,
            '순위': rank_list,
            '곡명': song_list,
            '가수명': singer_list,
            '장르':genre_list
        })
        result_df = pd.concat([result_df, df], ignore_index=True)

        print(df_year)
        
        return result_df
        
def main():
    period = 1
    year = 1
    count = 1
    result_df = pd.DataFrame()

    while count < 9:
        try:
            if(count == 5):
                year = 1
                period = 2
            
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            driver = wd.Chrome(options=chrome_options)

            url = 'https://www.melon.com/chart/index.htm'
            driver.get(url)
            time.sleep(1)

            result_df = select_chart(driver, period, year, count, result_df)
            year += 1
            count += 1

            driver.close()
        
        except Exception as e:
            print(f"Error: {e}")
            break
        
    result_df.to_csv('멜론차트크롤링.csv', encoding='utf-8-sig', index=False)

if __name__ =='__main__':
    main()

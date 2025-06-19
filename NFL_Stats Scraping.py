import requests
import pandas as pd
import csv
from bs4 import BeautifulSoup
def safe_float(text):
    try:
        return float(text)
    except (ValueError, TypeError):
        return 0.0
def safe_int(text):
    try:
        return int(text)
    except (ValueError, TypeError):
        return 0
#RB
WR_24 = []
url = requests.get("https://www.pro-football-reference.com/years/2020/receiving.htm")
soup = BeautifulSoup(url.text, 'html.parser')
player_24_table = soup.find('div', attrs={'id': 'div_receiving'}).find('table')
player_24_row = player_24_table.find('tbody').find_all('tr')
for row in player_24_row:
    col = row.find_all('td')
    name = col[0].text.strip()
    team = col[2].text.strip()
    pos = col[3].text.strip()
    if pos == "WR" or "RB" or "TE":
        rec = safe_int(col[7].text)
        yds = safe_int(col[8].text)
        td = safe_int(col[10].text)
        y_per_a = safe_float(col[9].text)
        y_per_g = safe_float(col[15].text)
        rec_fp = (6*td + (yds/10)+ rec)
        WR_24.append([2020, name, team, rec, yds, td, y_per_a, y_per_g, rec_fp])

csv_filename = "2020 WR_etc stats"
with open(csv_filename, mode = 'w', newline = '', encoding = 'utf-8') as file:
    writer = csv.writer(file)
    headers = [2020, "Name", "Team", "REC", "YDS", "TD", "Y/A", "Y/G", "FP"] 
    writer.writerow(headers)
    writer.writerows(WR_24)

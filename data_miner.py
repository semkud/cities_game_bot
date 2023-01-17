from bs4 import BeautifulSoup
import requests
import pandas as pd

#parsing table with cities

url = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8'
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")
allCities = soup.findAll('tr')
s = []

# Интересующая нас таблица начинается с третьего тэга 'tr'
for city in range(2,1119):
  c = allCities[city].findAll('td')
  if city % 10 == 0:
    print(city*100/1119)
  try:
    #Дополнительно извлечем заглавный текст из статьи про город по реферальной ссылке, если она есть
    href = "https://ru.wikipedia.org"+c[2].find('a').get('href')
    page = requests.get(href)
    soup = BeautifulSoup(page.text, "html.parser")
    short = soup.findAll('p')
    sh = short[0].text
  except:
    sh = 'Простите, про этот город у нас нет подробной информации!'
  zx = c[2].text
  z = c[2].text.lower()
  if zx.endswith('не призн.'): #Для городов Крыма
    zx = zx[:-9]
    z = z[:-9]
  f_letter = z[0]
  if z.endswith('ый'):
    l_letter = z[-3]
  elif z[-1] not in ['ь', 'ы', 'й']:
    l_letter = z[-1]
  else:
    l_letter = z[-2]
  #соберем все в большой список списков, который затем положим в датафрейм
  s.append([int(c[0].text), z, zx, c[3].text, int(c[5].text.replace(" ", "")), sh, f_letter, l_letter])

mydf = pd.DataFrame(s, columns = ['number', 'city', 'City', 'region', 'population', 'description', 'first_letter', 'last_letter'])

mydf.to_csv('cities.csv', sep = '\t')

import requests
from bs4 import BeautifulSoup
import csv
import json

url = 'https://mediakit.iportal.ru/our-team'
headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
}

req = requests.get(url, headers=headers)
req.encoding = 'UTF-8'
src = req.text

"""We save the page so as not to load the site with requests."""
with open('index.html', 'w', encoding='utf-8') as file:
    file.write(src)

with open('index.html', encoding='utf-8') as file:
    src = file.read()

with open('table.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(
        (
            'Город',
            'Имя',
            'Должность',
            'Email',
        )
    )

soup = BeautifulSoup(src, 'lxml')
all_blocks = soup.find_all(class_='t396')
list_info = []
count = 0
for block in all_blocks:
    all_text = block.find_all(class_='t396__elem')

    cities = {
        '1': '',
        '2': ''
    }
    names = {
        '1': '',
        '2': ''
    }
    positions = {
        '1': '',
        '2': ''
    }
    emails = {
        '1': '',
        '2': ''
    }
    for item in all_text:

        row = item.text
        horizontal_position = item.get('data-field-left-res-320-value')
        vertical_position = item.get('data-field-left-res-480-value')
        if row.strip() == 'Андрей Затирко':
            continue
        if len(item.text) >= 1:
            if (horizontal_position.isdigit() and int(horizontal_position) <= 12) or (
                    horizontal_position[-2:] == 'px' and 'Почта' in row):
                """read data from the left block"""
                p = '1'
                if '@' not in row and row and not row[0].isdigit():
                    if vertical_position.isdigit() and int(vertical_position) <= 12:
                        cities[p] = row
                    elif vertical_position[:3].isdigit() and int(vertical_position[:3]) >= 250:
                        if all([i.istitle() for i in row.strip().split(' ')]):
                            names[p] = row

                if len(item.find_all('a')) > 0:
                    emails[p] = item.find('a').get('href')
                    positions[p] = row
                    if '@' in row:
                        positions[p] = item.find('a').previous_element.previous_element

            elif horizontal_position[:3].isdigit() and int(horizontal_position[:3]) >= 168 or (
                    horizontal_position[-2:] == 'px' and 'редактор' in row):
                """read data from the right block"""
                p = '2'
                if '@' not in row and row and not row[0].isdigit():
                    if vertical_position.isdigit() and int(vertical_position) <= 12:
                        cities[p] = row
                    elif vertical_position[:3].isdigit() and int(vertical_position[:3]) in range(250, 290):
                        if all([i.istitle() for i in row.strip().split(' ')]):
                            names[p] = row

                if len(item.find_all('a')) > 0:
                    if 'Почта' in row:
                        p = '1'
                    emails[p] = item.find('a').get('href')
                    positions[p] = item.text
                    if '@' in row:
                        positions[p] = item.find('br').previous_element

    if len(cities['1']) > 0:
        for i in range(1, 3):
            if names[str(i)] == '':
                names[str(i)] = '-'
        for i in range(1, 3):
            num = str(i)
            list_info.append(
                {
                    'Город': cities[num],
                    'Имя': names[num],
                    'Должность': positions[num],
                    'Email': emails[num],
                }
            )


            with open('table.csv', 'a', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        cities[num],
                        names[num],
                        positions[num],
                        emails[num],
                    )
                )

    count += 1
    if count == 16:
        break

with open('table.json', 'a', encoding='utf-8') as file:
    json.dump(list_info, file, indent=4, ensure_ascii=False)

print('Работа закончена!')

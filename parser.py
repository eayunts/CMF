# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 00:29:28 2016

@author: Edward
"""
import requests
import re
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd



def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text))

#функции для каждого признака квартиры
def getPrice(flat_page): 
    price = flat_page.find('div', attrs={'class':'object_descr_price'})
    price = re.split('<div>|руб|\W', str(price))
    price = "".join([i for i in price if i.isdigit()][-3:])
    return price
    
def getCoords(flat_page):
    coords = flat_page.find('div', attrs={'class':'map_info_button_extend'}).contents[1]
    coords = re.split('&amp|center=|%2C', str(coords))
    coords_list = []
    for item in coords:
        if item[0].isdigit():
            coords_list.append(item)
    lat = float(coords_list[0])
    lon = float(coords_list[1])
    return lat, lon
    
    
def getRoom(flat_page):
    rooms = flat_page.find('div', attrs={'class':'object_descr_title'})
    rooms = html_stripper(rooms)
    room_number = ''
    for i in re.split('-|\n', rooms):
        if 'комн' in i:
            break
        else:
            room_number += i
    room_number = "".join(room_number.split())
    return room_number


def getFloor(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    table = re.split('Этаж:|Тип дома:|Общая площадь:', table)[1]
    table = re.split('/', table)[0]
    floor = "".join([i for i in table if i.isdigit()])
    return floor

def getNFloor(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    table = re.split('Этаж:|Тип дома:|Общая площадь:', table)[1]
    if len(re.split('/', table))>1:
        table = re.split('/', table)[1]
        floor = "".join([i for i in table if i.isdigit()])
        return floor

def getArea(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    table = re.split('Общая площадь', table)[1]
    data=re.split('\xa0м2|:\n\n', table)
    return data[1]

def getKitchen(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    table = re.split('Площадь кухни:',table)[1]
    table = re.split('Совмещенных санузлов:|Балкон:|Раздельных санузлов:|Санузел:',table)[0]
    if table != re.split('м2',table)[0]:
        table = re.split('м2',table)[0]
        time = "".join([i for i in table if i.isdigit() or i==',' and i != '\n'])
        return time

def getLiveSP(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    table = re.split('Жилая площадь:|Площадь кухни:|Совмещенных санузлов:|Балкон:|Раздельных санузлов:|Санузел:', table)[1]  
    if table != re.split('м2',table)[0]:
        table = re.split('м2',table)[0]
        time = "".join([i for i in table if i.isdigit() or i==',' and i != '\n'])
        return time

def getMetro(flat_page):
    metro_min = flat_page.find('div', attrs={'class':"object_descr_metro"})
    metro_min = html_stripper(metro_min)
    if len(re.split(',|мин.', metro_min))>1:
        table = re.split(',|мин.', metro_min)[1]
        time = "".join([i for i in table if i.isdigit()])
        return time

def getWalk(flat_page):
    walk = flat_page.find('div', attrs={'class':"object_descr_metro"})
    walk = html_stripper(walk)
    if re.split('пешком', walk)[0] == walk: return 0
    else: return 1

def getBrick(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if re.split('кирпичный', table)[0] == table and re.split('панельный', table)[0] == table and re.split('монолитный', table)[0] == table  and re.split('монолитно-кирпичный', table)[0] == table: return 0
    else: return 1


def getTel(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if len(re.split('Телефон', table)) == 1: return 0
    else:
        table = re.split('Телефон:|Вид из окна:|Ремонт:',table)[1]
        if re.split('да', table)[0] == table:
            return 0
        else: return 1 


def getNew(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if re.split('Тип дома', table)[0] == table: return 0
    else:
        table =  re.split('Тип дома:|Тип продажи:|Общая площадь:', table)[1]
        if re.split('вторичка', table)[0] == table:
            return(1)
        else: return(0)         

def getBal(flat_page):
    table = flat_page.find('table', attrs = {'class':'object_descr_props'})
    table = html_stripper(table)
    if re.split('Балкон', table)[0] == table: return 0
    else:
        table =  re.split('Балкон', table)[1]
        table =  re.split('Лифт', table)[0]
        if re.split('нет', table)[0] == table and re.split('-', table)[0] == table:
            return(1)
        else: return(0) 

import urllib.request  # получил доступ к Googla Maps API, код корректно работает, ему необходимо  только задать ключ, который нужно получить у гугла, но проблема оказалась в том что большое число запросов гугл обрабатывать отказался и пользоваться этим не получилось, по этому  я в конце пифагором посчитал расстояние
import simplejson
def getDist(flat_page,key):
    apiurl2 = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins='+str(round(getCoords(flat_page)[0],3))+','+str(round(getCoords(flat_page)[1],3)) +'&destinations=55.7558,37.6173&key='+str(key)
    with urllib.request.urlopen(apiurl2) as url:
        s = url.read()
        data=simplejson.loads(s)
        return data['rows'][0]['elements'][0]['distance']['value']

# данная функция возвращает пандас датафрейм который выдает всю информацию о квартире вместе с ссылкой на нее.
def getStats(link):
    flatStats={}
    flat_url = 'http://www.cian.ru/sale/flat/' + str(link) + '/'
    #flat_url = 'http://www.cian.ru/sale/flat/148769291/'
    flat_page = requests.get(flat_url)
    flat_page = flat_page.content
    flat_page = BeautifulSoup(flat_page, 'lxml')
    flatStats={}
    flatStats['Price'] = getPrice(flat_page)
    flatStats['lat'], flatStats['lon'] = getCoords(flat_page)
    flatStats['Rooms'] = getRoom(flat_page)
    flatStats['Floor']= getFloor(flat_page)
    flatStats['N_Floors']=getNFloor(flat_page)
    flatStats['Area']=getArea(flat_page)
    flatStats['Kitchen']=getKitchen(flat_page)
    flatStats['LiveSP']=getLiveSP(flat_page)
    flatStats['MetroTime']=getMetro(flat_page)
    flatStats['Walk']=getWalk(flat_page)
    flatStats['Brick']=getBrick(flat_page)
    flatStats['Tel'] = getTel(flat_page)
    flatStats['Bal'] = getBal(flat_page)
    flatStats['New'] = getNew(flat_page)
    #flatStats['Dist'] = getDist(flat_page) # отключена так как не позволяла забрать инфо по всем необходимым квартирам
    flatStats['District'] = 'SAO'
    flatStats['link']=link
    print(link) # чтобы понимать на идет ли парсинг
    return pd.DataFrame.from_dict(flatStats,orient='index')


#ссылки на квартиры по каждому округу
district_cao = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=13&district%5B1%5D=14&district%5B2%5D=15&district%5B3%5D=16&district%5B4%5D=17&district%5B5%5D=18&district%5B6%5D=19&district%5B7%5D=20&district%5B8%5D=21&district%5B9%5D=22&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
district_sao = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=23&district%5B10%5D=33&district%5B11%5D=34&district%5B12%5D=35&district%5B13%5D=36&district%5B14%5D=37&district%5B15%5D=38&district%5B1%5D=24&district%5B2%5D=25&district%5B3%5D=26&district%5B4%5D=27&district%5B5%5D=28&district%5B6%5D=29&district%5B7%5D=30&district%5B8%5D=31&district%5B9%5D=32&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
district_svao = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=39&district%5B10%5D=49&district%5B11%5D=50&district%5B12%5D=51&district%5B13%5D=52&district%5B14%5D=53&district%5B15%5D=54&district%5B16%5D=55&district%5B1%5D=40&district%5B2%5D=41&district%5B3%5D=42&district%5B4%5D=43&district%5B5%5D=44&district%5B6%5D=45&district%5B7%5D=46&district%5B8%5D=47&district%5B9%5D=48&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
district_vao = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=56&district%5B10%5D=66&district%5B11%5D=67&district%5B12%5D=68&district%5B13%5D=69&district%5B14%5D=70&district%5B15%5D=71&district%5B1%5D=57&district%5B2%5D=58&district%5B3%5D=59&district%5B4%5D=60&district%5B5%5D=61&district%5B6%5D=62&district%5B7%5D=63&district%5B8%5D=64&district%5B9%5D=65&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
district_yvao = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=72&district%5B10%5D=82&district%5B11%5D=83&district%5B1%5D=73&district%5B2%5D=74&district%5B3%5D=75&district%5B4%5D=76&district%5B5%5D=77&district%5B6%5D=78&district%5B7%5D=79&district%5B8%5D=80&district%5B9%5D=81&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'

district_yao = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=84&district%5B10%5D=94&district%5B11%5D=95&district%5B12%5D=96&district%5B13%5D=97&district%5B14%5D=98&district%5B15%5D=99&district%5B1%5D=85&district%5B2%5D=86&district%5B3%5D=87&district%5B4%5D=88&district%5B5%5D=89&district%5B6%5D=90&district%5B7%5D=91&district%5B8%5D=92&district%5B9%5D=93&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
district_yzao= 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=100&district%5B10%5D=110&district%5B11%5D=111&district%5B1%5D=101&district%5B2%5D=102&district%5B3%5D=103&district%5B4%5D=104&district%5B5%5D=105&district%5B6%5D=106&district%5B7%5D=107&district%5B8%5D=108&district%5B9%5D=109&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
district_zao = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=112&district%5B10%5D=122&district%5B11%5D=123&district%5B12%5D=124&district%5B13%5D=348&district%5B14%5D=349&district%5B15%5D=350&district%5B1%5D=113&district%5B2%5D=114&district%5B3%5D=115&district%5B4%5D=116&district%5B5%5D=117&district%5B6%5D=118&district%5B7%5D=119&district%5B8%5D=120&district%5B9%5D=121&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'
district_szao = 'http://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=125&district%5B1%5D=126&district%5B2%5D=127&district%5B3%5D=128&district%5B4%5D=129&district%5B5%5D=130&district%5B6%5D=131&district%5B7%5D=132&engine_version=2&offer_type=flat&p={}&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1'


# функция возвращает список со ссылками на все квартиры в данном округе
def get_links(url, links): #links_list_name - нужно подавать строку с названием листа
    page = 1
    for page in range(1, 2):
        page_url =  url.format(page)

        search_page = requests.get(page_url)
        search_page = search_page.content
        search_page = BeautifulSoup(search_page, 'lxml')

        flat_urls = search_page.findAll('div', attrs = {'ng-class':"{'serp-item_removed': offer.remove.state, 'serp-item_popup-opened': isPopupOpen}"})
        flat_urls = re.split('http://www.cian.ru/sale/flat/|/" ng-class="', str(flat_urls))

        for link in flat_urls:
            if link.isdigit():
                links.append(link)
        print(page)

#подаем лист со ссылками, получаем лист с датафремом по квартире по каждой ссылке
#тут нужно создать пустой лист с именем округа  vao например которой потом подать как district
def  get_data(links, district):
    for link in links:
        district.append(getStats(link))
def make_csv(district, file_name): # пишем данные по округу в csv
    for i in range(len(district)):
        district[i] = district[i].transpose()
    district_data =  district[0]
    for i in district[1:]:
        district_data = pd.concat([district_data,i])
    district_data.to_csv(str(file_name))
   
   
# по отдельности для каждого округа запускаем процесс парсинга,
#периодически выскакивают ошибки, они возникают каждый раз на разной ссылке, поэтому видимо причина со сторона ЦИАНа, 
# при ошибке при записи данных по округу необходимо определить индекс на котором код споткнулся,
# и запустить алгоритм далее, но начать список ссылок со следующей квартире после той на которой ошибка
#SZAO
links_szao = []
get_links(district_szao,links_szao)
szao =[]
get_data(links_szao,szao)
make_csv(szao, 'szao_district')

#SAO
links_sao = []
get_links(district_sao,links_sao)
sao =[]
get_data(links_sao,sao)
make_csv(sao, 'sao_district')

#SVAO
links_svao = []
get_links(district_svao,links_svao)
svao =[]
get_data(links_svao,svao)
make_csv(svao, 'svao_district')

#VAO
links_vao = []
get_links(district_vao,links_vao)
vao =[]
get_data(links_vao,vao)
make_csv(vao, 'vao_district')

#YVAO
links_yvao = []
get_links(district_yvao,links_yvao)
yvao =[]
get_data(links_yvao,yvao)
make_csv(yvao, 'yvao_district')

#YAO
links_yao = []
get_links(district_yao,links_yao)
yao =[]
get_data(links_yao,yao)
make_csv(yao, 'yao_district')

#YZAO
links_yzao = []
get_links(district_yzao,links_yzao)
yzao =[]
get_data(links_yzao,yzao)
make_csv(yzao, 'yzao_district')

#ZAO
links_zao = []
get_links(district_zao,links_zao)
zao =[]
get_data(links_zao,zao)
make_csv(zao, 'zao_district')

#CAO
links_cao = []
get_links(district_cao,links_cao)
cao =[]
get_data(links_cao,cao)
make_csv(cao, 'cao_district')


# Для каждого округа получены датафреймы, теперь необходимо их объединить, и записать дистанцию от центра
data_cao = pd.read_csv('cao_district')
data_sao = pd.read_csv('sao_district')
data_svao = pd.read_csv('svao_district')
data_vao = pd.read_csv('vao_district')
data_yvao = pd.read_csv('yvao_district')
data_yao = pd.read_csv('yao_district')
data_yzao = pd.read_csv('yzao_district')
data_zao = pd.read_csv('zao_district')
data_szao = pd.read_csv('szao_district')

data = pd.concat([data_cao, data_sao,data_svao,data_vao,data_yvao,data_yao,data_yzao,data_zao,data_szao])
del data['Unnamed: 0']
from numpy import cos,sqrt

sh =55.7558 #широта у Кремля
dol = 37.6173 # долгота там же
data['new1'] = abs(data['lon']-dol)
data['new2'] = abs(data['lat']-sh)
#(cos 53,85°) × 40000 / 360 = 0,59 × 111,111... = 65,544 #километров в 1 градусе на широте Москвы
coef_2 =cos(55/57)*40000/360
coef_1 = 111
data['dist'] = sqrt((coef_1*data['new1'])**2 + (coef_2*data['new2'])**2) #посчитали дистанцию, теперь удалим временно созданные столбцы

del data['new1']
del data['new2']

data_unique=data.drop_duplicates() #отбросим дупликаты
len(data) - объем собранной выборки
data.to_csv('data') вернули  сsv.

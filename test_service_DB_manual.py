from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import os
import re

from pages_const import *
from common_functions import *




def delete_old_csv_files():
    os.chdir(downloads)
    checking_file = os.path.exists('signal_for_compare.csv')
    checking_file1 = os.path.exists('signal_for_compare (1).csv')

    count = 0    
    if checking_file:
        os.remove('signal_for_compare.csv')
        count+=1
    if checking_file1:
        os.remove('signal_for_compare (1).csv')
        count+=1

    if count==1:
        print(time.asctime(), 'Удалён 1 старый csv файл')
    elif count==2:
        print(time.asctime(), 'Удалено 2 старых csv файла')


def make_new_table(date):
    utilite_start = time.time()
        
    start_date =  ' -from '+date
    end_date = ' -to '+date
    command = path+start_date+end_date+ip+postgres_password+args
        
    scada_stop()
    time.sleep(1)  
    x = subprocess.run(command, capture_output=True, text=True )
    if x.stdout:
        print(time.asctime())
        print(x.stdout.strip())
        utilite_completed = time.time()
        print(f'На создание таблицы затрачено {round(utilite_completed-utilite_start, 1)}  с')
    if x.stderr:
        print("stderr:", x.stderr)

    scada_start()
    time.sleep(20)
    # за 20 секунд успевает стартануть служба и подготовится резервная копия таблицы


def making_csv_file():        
    driver.find_element(By.XPATH, "//button[text()='Меню']").click()
    driver.find_element(By.XPATH, "//div[@webix_l_id='db/edit']").click()
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".webix_accordionitem_label")))
    driver.find_element(By.XPATH, "//a/b[text()='signal_for_compare']").click()
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[view_id="$button7"] button')))
    time.sleep(1)
    driver.find_element(By.XPATH, "//input[@placeholder='Начальная дата']").clear()
    driver.find_element(By.XPATH, "//input[@placeholder='Начальная дата']").send_keys('28.02.2000 15:00:00')
    time.sleep(1)
    driver.find_element(By.XPATH, "//input[@placeholder='Конечная дата']").clear()
    driver.find_element(By.XPATH, "//input[@placeholder='Конечная дата']").send_keys('28.02.2000 15:30:00')
    driver.find_element(By.XPATH, "//input[@placeholder='Конечная дата']").send_keys(Keys.ENTER)
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[view_id="$button7"] button')))
    driver.find_element(By.XPATH, "//label[text()='Фильтр:']//following-sibling::span").click()
    driver.find_element(By.XPATH, "//div[@webix_l_id='1']").click()
    driver.find_element(By.CSS_SELECTOR, ".webix_icon_btn.wxi-sync").click()
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '28.02.2000 15:29:59')]")))
    driver.find_element(By.CSS_SELECTOR, ".fa-file-download").click()


def looking_for_reserved_copy():
    '''
    Функция ищет резервную копию в папке резервных копий
    и по записям в журнале событий.
    Резервная копия должна появиться сама при старте службы.
    '''    
    files = os.listdir(path_to_reserved_copies)
    flag = 0
    for file in files:
        result = re.search(reserved_copy_name_pattern, file)
        if result:
            flag += 1
    print(f'В папке {flag} РК таблицы')
    assert flag >0, 'Нет резервной копии от 28 февраля 2000 года в папке'

    look_for = 'Создана резервная копия таблицы: sgn."2000_02_28".'
    count = 0
    driver.get(events_page)
    time.sleep(1)
    events = []
    
    try:
        events_list = driver.find_elements(By.XPATH, "//div[@column='3']/div[@role='gridcell']")
        for event in events_list:
            events.append(event.text)
    except:
        print('устаревший элемент DOM "event.text"')
        time.sleep(1)
        driver.refresh()
        time.sleep(1)
        events_list2 = driver.find_elements(By.XPATH, "//div[@column='3']/div[@role='gridcell']")
        for event in events_list2:
            events.append(event.text)

    for e in events:
        if e == look_for:
            count+=1
            
    print(f'В журнале найдено {count} сообщений о восстановлении таблицы от 28 февраля 2000')
    assert look_for in events, 'В журнале не найдено сообщение о восстановлении таблицы из резервной копии'


def delete_table():       
    driver.find_element(By.XPATH, "//button[text()='Меню']").click()
    time.sleep(0.3)
    driver.find_element(By.XPATH, "//div[@webix_l_id='dba/main']").click()
    time.sleep(0.3)
    driver.find_element(By.XPATH, "//div[text()=' Резервное копирование и очистка']").click()
    time.sleep(1)

    start_date = driver.find_element(By.XPATH, "//div[@aria-label='Начальная дата']").text
    current_month = start_date[3:5]
    year_begin = start_date[-4:]

    assert current_month == '02' and year_begin == '2000', 'Не корректная начальная дата в списке таблиц'
   
    driver.find_element(By.XPATH, "//div[@aria-label='Начальная дата']").click()    
    driver.find_element(By.XPATH, '//div[@view_id="$suggest1_calendar"]//div[@aria-label="28 Февраль 2000"]').click()
    time.sleep(0.5)

    driver.find_element(By.XPATH, "//div[@aria-label='Конечная дата']").click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//div[@view_id="$suggest2_calendar"]//span[@role="button" and @class="webix_cal_month_name"]').click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//div[@view_id="$suggest2_calendar"]//span[@role="button" and @class="webix_cal_month_name"]').click()
    time.sleep(3)
   
    a=[]
    selected_years = driver.find_elements(By.XPATH, '//div[@view_id="$suggest2"]//div[@class="webix_cal_body"]/div[@role="gridcell"]')
    for year in selected_years:
        a.append(year.text)

    if '2000' not in a:
        while '2000' not in a:
            a=[]
            selected_years = driver.find_elements(By.XPATH, '//div[@view_id="$suggest2"]//div[@class="webix_cal_body"]/div[@role="gridcell"]')
            for year in selected_years:
                a.append(year.text)
            driver.find_element(By.XPATH, '//div[@aria-label="Предыдущие десять лет"]').click()

    time.sleep(0.25)
    driver.find_element(By.XPATH, '//span[text()="2000"]').click()
    time.sleep(0.25)
    driver.find_element(By.XPATH, '//span[text()="Фев"]').click()
    time.sleep(0.25)
    driver.find_element(By.XPATH, '//div[@view_id="$suggest2_calendar"]//div[@aria-label="28 Февраль 2000"]').click()
    time.sleep(0.25)

    driver.find_element(By.XPATH, "//button[@aria-label='Резервные копии и очистка']").click()    
    driver.find_element(By.XPATH, "//button[text()='Далее']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[text()='Подтвердить']").click()    
    WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Завершить']")))    
    driver.find_element(By.XPATH, "//button[text()='Завершить']").click()
    log =  driver.find_element(By.XPATH, "//textarea").text
    assert 'Удалена таблица: sgn."2000_02_28"' in log, "Дневная таблица не была удалена"
    

def delete_old_reserved_copies():    
    files = os.listdir(path_to_reserved_copies)
    old_copies = []

    for i in files:
        result = re.search(reserved_copy_name_pattern, i)
        if result:
            old_copies.append(result[0])
            
    for file in old_copies:
        os.chdir(path_to_reserved_copies)
        os.remove(file)
        print('Удалён файл',file)    


def ressurect_table():  
    driver.find_element(By.XPATH, "//button[text()='Меню']").click()
    driver.find_element(By.XPATH, "//div[@webix_l_id='dba/main']").click()    
    driver.find_element(By.XPATH, "//div[text()=' Восстановление резервных копий']").click()
    time.sleep(1)

    start_date = driver.find_element(By.XPATH, "//div[@aria-label='Начальная дата']").text
    current_month = start_date[3:5]
    year_begin = start_date[-4:]

    assert (current_month == '02' or current_month == '01') and year_begin == '2000', 'Не корректная начальная дата в списке таблиц'
             
    driver.find_element(By.XPATH, "//div[@aria-label='Начальная дата']").click()
    first_date = driver.find_element(By.XPATH, '//div[@view_id="$suggest1_calendar"]//span[@aria-live="assertive"]').text
    if first_date == 'Январь 2000':
        driver.find_element(By.XPATH, '//div[@view_id="$suggest1_calendar"]//div[@aria-label="Следующий месяц"]').click()
        time.sleep(0.25)  
    driver.find_element(By.XPATH, '//div[@view_id="$suggest1_calendar"]//div[@aria-label="28 Февраль 2000"]').click()
    time.sleep(0.5)

    driver.find_element(By.XPATH, "//div[@aria-label='Конечная дата']").click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//div[@view_id="$suggest2_calendar"]//span[@role="button" and @class="webix_cal_month_name"]').click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, '//div[@view_id="$suggest2_calendar"]//span[@role="button" and @class="webix_cal_month_name"]').click()
    time.sleep(3)
   
    a=[]
    selected_years = driver.find_elements(By.XPATH, '//div[@view_id="$suggest2"]//div[@class="webix_cal_body"]/div[@role="gridcell"]')
    for year in selected_years:
        a.append(year.text)

    if '2000' not in a:
        while '2000' not in a:
            a=[]
            selected_years = driver.find_elements(By.XPATH, '//div[@view_id="$suggest2"]//div[@class="webix_cal_body"]/div[@role="gridcell"]')
            for year in selected_years:
                a.append(year.text)
            driver.find_element(By.XPATH, '//div[@aria-label="Предыдущие десять лет"]').click()

    time.sleep(0.25)
    driver.find_element(By.XPATH, '//span[text()="2000"]').click()
    time.sleep(0.25)
    driver.find_element(By.XPATH, '//span[text()="Фев"]').click()
    time.sleep(0.25)
    driver.find_element(By.XPATH, '//div[@view_id="$suggest2_calendar"]//div[@aria-label="28 Февраль 2000"]').click()
    time.sleep(0.25)

    driver.find_element(By.XPATH, "//button[text()='Далее']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[text()='Подтвердить']").click()    
    WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Завершить']")))    
    driver.find_element(By.XPATH, "//button[text()='Завершить']").click()
    log =  driver.find_element(By.XPATH, "//textarea").text
    assert 'Восстановлена таблица: sgn."2000_02_28"' in log, "Таблица не восстановилась"


def compare_csv():
    os.chdir(downloads)
    with open('signal_for_compare.csv', 'r', encoding='utf-8') as first:
        f1 = first.read()        
    time.sleep(1)    
    with open('signal_for_compare (1).csv', 'r', encoding='utf-8') as second:
        f2 = second.read()      
    print(time.ctime(), 'файлы одинаковы' if f1==f2 else 'файлы отличаются')    

    if f1==f2:
        print(time.ctime(), 'сравниваем csv с исходным файлом')
        os.chdir("C:\\andreev_autotests")
        with open('signal_for_compare_true.csv', 'r', encoding='utf-8') as third:
            f3 = third.read()
        print(time.ctime(), 'тест пройден' if f1==f3 else 'файлы отличаются') 
    return True if(f1==f3 and f1==f2) else False


# main block
# Python должен быть открыт от имени администратора для управления службами SCADA.
if is_admin():
    scrypt_start = time.time()           

    downloads = "C:\\Users\\user\\Downloads"
    reserved_copy_name_pattern = r'wsmtdb-\d{5}-sgn-2000_02_28-\d{5,}.backup'

    # тестовая таблица будет за 28 февраля 2000 года
    date = '2000-02-28'
    end_test = False
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)    
    driver.implicitly_wait(7)

    driver.get(mainpage)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[view_id="$spacer3"]')))
    
    if "WebScadaMT" in driver.title:
        autorization(driver)

    delete_old_csv_files()

    print(time.ctime(), 'проверяем наличие старых резервных копий в папке')
    delete_old_reserved_copies()

    '''
    Здесь проверяем наличие project в папке C:\Program Files (x86)\Механотроника\WebScadaMT 4.0\Data\Projects
    Если данного проекта нет в репозитории скады, то копируем его в репозиторий из папки autotests.
    Если и в папке autotests нет нужного проекта, то error.
    '''
    run_project(project, driver)
          

    '''
    Удаляем таблицы старше 100 дней, чтобы не мешались таблицы с предыдущих автотестов.
    Создаём таблицу за 28 февраля 2000 года.
    Считываем из неё данные по одному из сигналов, формируем CSV-файл.
    Создаём резервную копию этой таблицы и удаляем её (таблицу).
    Восстанавливаем таблицу из резервной копии и считываем те же данные, что хранятся в
    первом CSV-файле.
    Сравниваем эти два файла, они должны быть идентичны.
    А также сравниваем эти файлы с опорным тестовым CSV-файлом, который хранится папке autotests.
    '''
        
    delete_old_tables(driver)
    time.sleep(1)
    make_new_table(date)
    driver.get(mainpage)
                
    print(time.ctime(), 'Формируем csv файл сигнала из БД')        
    making_csv_file()
        
    # проверяем РК в папке и в журнале событий
    looking_for_reserved_copy()
        
    print(time.ctime(), 'удаляем таблицу из БД')
    delete_table()
        
    print(time.ctime(), 'восстанавливаем ранее удалённую таблицу из РК')
    ressurect_table()
       
    print(time.ctime(), 'Формируем csv файл сигнала из БД, восстановленной из РК')        
    making_csv_file()  

    print(time.ctime(), 'сравниваем csv файлы между собой и с эталоном')
    if compare_csv():
        end_test = True
        
    scrypt_end = time.time()
    mins = int((scrypt_end-scrypt_start)//60)
    secs = round((scrypt_end-scrypt_start)%60)
    print(f'Скрипт выполнился за {mins} минут {secs} секунд')
    print('!!! ЕСТЬ ОШИБКИ В АВТОТЕСТЕ' if not end_test else 'Автотест пройден успешно')
    driver.quit()

else:
    print('Откройте Python от имени администратора')

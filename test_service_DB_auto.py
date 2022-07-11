from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os
import time

from pages_const import *
from common_functions import *


def delete_reserved_copies():
    os.chdir(path_to_reserved_copies)
    files = list(os.walk(path_to_reserved_copies))[0][2]
    if len(files)>0:
        print(time.asctime(), 'удаляем файлы резевных копий')
        for file in files:
            os.remove(file)



if is_admin():
    
    scrypt_start = time.time()
    
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(8)
    
    autorization(driver)

    '''
    Здесь проверяем наличие project в папке C:\Program Files (x86)\Механотроника\WebScadaMT\Data\Projects
    Если данного проекта нет в репозитории скады, то копируем его в репозиторий из папки autotests.
    Если и в папке autotests нет нужного проекта, то error.
    '''
    run_project(project, driver)


    # перед началом работы проверяем каталог резервных копий, если он не пустой - очищаем его
    delete_reserved_copies()

    # устанавливаем БД = 10 Гб и backups = 0,25 Гб в файле конфигурации dba_config
    print(time.asctime(), 'Проверяем файл dba_config.xml')
    parse_dba_config()
    
    # если есть старые таблицы БД - удаляем их
    delete_old_tables(driver)

    ''' 
    В цикле останавливаем службу скады и запускаем утилиту по заполнению БД, создавая одну дневную таблицу.
    Затем запускаем службу и проверяем в журнале событий сообщения о создании
    резервных копий за этот день, если сообщения найдены, то ведём подсчёт их количества.
    '''
  
    start_date = ' -from 2000-01-01'
    end_date = ' -to 2000-01-01'

    dates = [str(i).rjust(2, '0') for i in range(1, 32)]

    tabcreated = 'Создана резервная копия таблицы: sgn.'
    quantity_of_reserved_copies = 0  
    quantity_deleted_tables = 0
    
    deleted_reserved_copies_messages = set()
    deleted_tables_mesages = set()
    
    for i in range(31):
        print()
        scada_stop()
        time.sleep(0.5)

        utilite_start = time.time()

        # start_date совпадает с end_date, создаётся одна дневная таблица
        start_date = start_date[:-2]+dates[i]
        end_date = end_date[:-2]+dates[i]
        command = path+start_date+end_date+ip+postgres_password+args
        x = subprocess.run(command, capture_output=True, text=True )

        if x.stdout:
            print(time.asctime())
            print(x.stdout.strip())
            utilite_completed = time.time()
            print(f'На создание таблиц затрачено {round(utilite_completed-utilite_start, 1)}  с')
        if x.stderr:
            print("stderr:", x.stderr)

        scada_start()
        time.sleep(20)
    
        driver.get(events_page)
        WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.XPATH, "//div[@view_id='placeholder_header']")))

        if i<20:
            time.sleep(16)
        else:
            time.sleep(26)
        
        t = driver.find_elements(By.XPATH, "//div[@column='3']/div[@role='gridcell']")
        events = []
        for element in t:
            events.append(element.text)
            

        '''
        После 12 итераций цикла начинаем смотреть журнал сообщений на предмет появления там
        интересующих нас записей.
        '''
        if i>=12:           
            for j in range(len(dates)):
                table_deleted = 'Удалена таблица sgn."2000_01_'+dates[j]+'". Освобождено 380,09 МБ.'
                reserved_copy_deleted_message = r'Удалена резервная копия wsmtdb-(\d{5})-sgn-2000_01_'+dates[j]+'-(\d{9}).backup'
                for message in events:                    
                    reserved_copy_deleted = re.search(reserved_copy_deleted_message, message)
                    if reserved_copy_deleted:
                        deleted_reserved_copies_messages.add(reserved_copy_deleted.group(0))
                        break

                if table_deleted in events:
                    deleted_tables_mesages.add(table_deleted)
                    
        # приводим дату к нужному виду и просматриваем журнал событий
        day = start_date[-10:].replace('-','_')
        if tabcreated+'"'+day+'".' in events:
            quantity_of_reserved_copies+=1

        print(f'В журнале событий найдено {quantity_of_reserved_copies} сообщений о создании резервных копий таблиц')

    quantity_deleted_tables = len(deleted_tables_mesages)
    quantity_deleted_reserved_copies = len(deleted_reserved_copies_messages)

    print('\nИтоги выполнения автотеста:')    
    print(f'В журнале событий найдено:\n{quantity_deleted_tables} сообщений об удалении дневных таблиц')
    print(f'{quantity_deleted_reserved_copies} сообщений об удалении файлов резервных копий')    

    
    os.chdir(path_to_reserved_copies)
    files_in_folder = list(os.walk(path_to_reserved_copies))[0][2]
    quantity_of_files = len(files_in_folder)
    quantity_of_files_awaiting = len(dates) - quantity_deleted_reserved_copies

    scrypt_finish = time.time()
    mins = int((scrypt_finish-scrypt_start)//60)
    secs = round((scrypt_finish-scrypt_start)%60)
    print(f'Скрипт выполнился за {mins} минут {secs} секунд\n')
    print('Сообщения об удалении таблиц:')
    print(*sorted(deleted_tables_mesages), sep='\n')
    print('\nСообщения об удалении файлов резервных копий:')
    print(*sorted(deleted_reserved_copies_messages), sep='\n')

    # Должно удалится 24 резервных копии и 10 или 12 дневных таблиц.
    if quantity_of_files==quantity_of_files_awaiting and\
       quantity_deleted_reserved_copies == 24 and quantity_of_reserved_copies == 31\
       and quantity_deleted_tables in range(10,13) and mins < 33:
        print("\nТест пройден успешно")
    else:
        print('\nВ автотесте возникли проблемы')
    driver.quit()
else:
    print('Откройте Python от имени администратора')    

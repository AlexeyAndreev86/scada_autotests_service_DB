'''
В этом автотесте проверяется скорость загрузки тренда сигналов с
очень большим количеством значений, которые получаются искусственно
при помощи специальной утилиты.
На скорость загрузки влияет тот факт, что для построения графика нужно
последнее значение сигнала вне запрашиваемого временного диапазона,
чтобы график не возникал из пустоты.
Последнее значение тестового сигнала в автотесте 31 марта 2000 года.

Если проекта в репозитории нет, то он запишется туда только, если
Python открыт от имени администратора.
'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import os.path
import subprocess

from pages_const import *
from common_functions import *



def make_new_tables():
    global tables
    utilite_start = time.time()
    
    command = path+start_date+end_date+ip+postgres_password+args        
    x = subprocess.run(command, capture_output=True, text=True)
    
    if x.stdout:        
        utilite_completed = time.time()
        print(f'{time.asctime()} На создание таблиц затрачено {round(utilite_completed-utilite_start, 1)}  с')
    if x.stderr:
        print("stderr:", x.stderr)
    tables = x.returncode


def checking_trend_1():
    global time_1
    driver.get(trends_page)
    driver.find_element(By.TAG_NAME, "a").click()
    trend_start = time.time()
    # вебдрайвер ждёт пока пропадёт колесо процесса
    WebDriverWait(driver, 600).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="webix_progress_state wxi-sync webix_spin"]')))
       
    trend_finish = time.time()
    time_1 = trend_finish - trend_start
    print(f'{time.asctime()} Тренд без поиска последнего значения загружался {round(time_1,1)} секунд')


def checking_trend_2():
    global test, time_2
    # ставим галочку "Искать предыдущее значение"
    driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Искать пред. значение"]').click()
    driver.find_element(By.CSS_SELECTOR, 'div[view_id="$button7"] button').click()
    trend_start = time.time()
    # вебдрайвер ждёт пока пропадёт колесо процесса
    WebDriverWait(driver, 600).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="webix_progress_state wxi-sync webix_spin"]')))
    
    trend_good = driver.find_elements(By.CSS_SELECTOR, 'div[aria-colindex="3"]')
    
    if len(trend_good) == 1:    
        trend_finish = time.time()
        time_2 = trend_finish - trend_start
        print(f'{time.asctime()} Тренд с поиском последнего значения сигнала загружался {round(time_2,1)} секунд')
        test = True
        UTC_last = driver.find_element(By.XPATH, '//div[@column="1"]/div[@aria-rowindex="1"]').text
        assert UTC_last == '954547199000', 'Не правильная метка времени последнего значения сигнала'
    elif len(trend_good) == 0:
        print("!!! Предыдущее значение сигнала не получено !!!")


# main block
scrypt_start = time.time()
       
start_date =     ' -from 2000-03-01'
end_date =       ' -to 2000-03-31'

test = False
time_1 = 0
time_2 = 0
tables = 0 # статус код процесса утилиты

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)    
driver.implicitly_wait(7)


autorization(driver)

'''
Здесь проверяем наличие project в папке C:\Program Files (x86)\Механотроника\WebScadaMT\Data\Projects
Если данного проекта нет в репозитории скады, то копируем его в репозиторий из папки autotests.
Если и в папке autotests нет нужного проекта, то error.
'''
run_project(project, driver)

     
delete_old_tables(driver)
make_new_tables()

assert tables == 0, "Ошибка returncode работы утилиты"
checking_trend_1()
time.sleep(1)
checking_trend_2()

assert time_1 < time_2, 'Тренд с поиском последнего значения построился быстрее'
    
scrypt_end = time.time()
mins = int((scrypt_end-scrypt_start)//60)
secs = round((scrypt_end-scrypt_start)%60)
if test:
    print(time.asctime(), f'Скрипт УСПЕШНО выполнился за {mins} минут {secs} секунд')
else:
    print(time.asctime(), f'Скрипт НЕУСПЕШНО выполнился за {mins} минут {secs} секунд')
   
driver.quit() 

import subprocess
import time
import ctypes
import xml.etree.ElementTree as ET

import os
import shutil

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages_const import *



def parse_scada_projects(project):
    all_projects = os.listdir(path_to_projects)
    project = project+'.mtp'
    if project in all_projects:
        return True
    else:
        return False


def upload_test_project(project):
    project = project+'.mtp'
    try:        
        source = os.path.join(path_source, project)
        destination = os.path.join(path_to_projects, project)
        shutil.copyfile(source, destination)
        return True        
    except:
        return False
    

def parse_dba_config():
    path_to_xml = r'C:\Program Files (x86)\Механотроника\WebScadaMT\Data\dba_config.xml'
    DbSize_need =       '10737418240'
    BackupSize_need =   '268435456'
    try:
        tree = ET.parse(path_to_xml)
        root = tree.getroot()        
        DbSize = root.find('DbSize')
        BackupSize = root.find('BackupSize')

        if DbSize.text != DbSize_need:
            DbSize.text = DbSize_need
            print('значение DbSize изменено')
        else:
            print('значение DbSize не нужно изменять')
        if BackupSize.text != BackupSize_need:
            BackupSize.text = BackupSize_need
            print('значение BackupSize изменено')
        else:
            print('значение BackupSize не нужно изменять')
        tree.write(path_to_xml)    
    except:
        print('Не удалось выполнить скрипт')


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def scada_start():
    start = subprocess.run('sc start WebScadaMT')
    print(start)
    return start


def scada_stop():
    stop = subprocess.run('sc stop WebScadaMT')
    print(stop)
    return stop


def autorization(driver):
    print(time.asctime(), 'Проходим авторизацию')
    driver.get(mainpage)
    driver.find_element(By.XPATH, "//input[@placeholder='Логин']").send_keys('system')
    driver.find_element(By.XPATH, "//input[@placeholder='Пароль']").send_keys('1')
    driver.find_element(By.XPATH, "//button[text()='Вход']").click()
    time.sleep(1)
    assert driver.title == 'Домашняя страница', 'Проблема с регистрацией'


def upload_the_project(project, driver):
    driver.get(project_page)
    current_project = driver.find_element(By.XPATH, '//div[@view_id="current_project"]/div[@class="webix_el_box"]').text
    if project in current_project:
        print(time.asctime(), current_project)
    else:
        print(time.asctime(), current_project)
        print(time.asctime(), "Будет загружен проект:", project)
        driver.find_element(By.XPATH, '//div[@aria-colindex="2" and text()="'+project+'"]').click()
        driver.find_element(By.XPATH, '//button[text()="Загрузить"]').click()
        time.sleep(1)
        driver.find_element(By.XPATH, '//div[text()="Да"]').click()
        driver.find_element(By.XPATH, '//div[text()="Нет"]').click()
        time.sleep(2)
        WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.XPATH, '//button[text()="Закрыть"]')))
        driver.find_element(By.XPATH, '//button[text()="Закрыть"]').click()
        time.sleep(1)
        new_current_project = driver.find_element(By.XPATH, '//div[@view_id="current_project"]/div[@class="webix_el_box"]').text
        assert project in new_current_project, "Проблема с загрузкой требуемого проекта"



def run_project(project, driver):
    if parse_scada_projects(project):  
        upload_the_project(project, driver)
    else:
        if upload_test_project(project):
            print(time.asctime(), 'Загружаем проект в репозиторий SCADA')
            upload_the_project(project, driver)
        else:
            print(time.asctime(), '!!! Не могу найти требуемый проект в папке autotests')


def delete_old_tables(driver):
    driver.get(clean_db)
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Обновить']")))
    time.sleep(1)
    driver.find_element(By.XPATH, "//select").click()
    driver.find_element(By.XPATH, "//select/option[@value='LessThan']").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "//input[@type='text']").send_keys(Keys.BACKSPACE)
    driver.find_element(By.XPATH, "//input[@type='text']").send_keys('100')
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[@role='radio' and @aria-label='Только очистка']").click()

    dalee = driver.find_element(By.XPATH, "//button[text()='Далее']").get_attribute('disabled')
    if dalee:
        print(time.asctime(), 'нет таблиц для удаления')
    else:
        driver.find_element(By.XPATH, "//button[text()='Далее']").click()
        WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Подтвердить']")))
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[text()='Подтвердить']").click()
        WebDriverWait(driver, 150).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Завершить']")))
        deleted_tables =  driver.find_element(By.XPATH,"//textarea").text
        assert 'Удалена таблица' in deleted_tables, "Таблицы не удалены"
        time.sleep(1)
        driver.find_element(By.XPATH, "//button[text()='Завершить']").click()
        print(time.asctime(), 'удалены все дневные таблицы старше 100 дней из базы данных')

import os
import time
import getpass
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


options = Options()
options.headless = True

course_list = []
course_dict = {}

driver = webdriver.Firefox(options=options)
driver.get("https://canvas.auckland.ac.nz/")

username = driver.find_element_by_name("j_username")
password = driver.find_element_by_name("j_password")

username.send_keys(input("email or userID: "))
password.send_keys(getpass.getpass(prompt="password: "))

print("getting session from the UoA login service. . .")
driver.find_element_by_name("_eventId_proceed").click()

try:
    dashboard = WebDriverWait( driver, 5 ).until(EC.presence_of_element_located((By.XPATH,'//*[@id="dashboard_header_container"]')))
    print("loaded canvas dashboard")
    driver.get("https://canvas.auckland.ac.nz/courses")
    course_table = WebDriverWait( driver, 5 ).until(EC.presence_of_element_located((By.XPATH,'//*[@id="my_courses_table"]')))
    clear = lambda: os.system('cls')
    clear()
    print("courses found:")
    for row in course_table.find_elements_by_xpath(".//tr"):
        course_row = row.find_elements_by_xpath(".//td[2]/a")
        for td in course_row:
            if td.text != None:
                course_dict[td.text] = td.get_attribute("href").replace("https://canvas.auckland.ac.nz/courses/" ,"")
                course_list.append(td.text)
    for course in course_list:
        print("\t=> "+course)
    course_choice = int(input("choose course: ")) - 1
    print(course_dict[course_list[course_choice]])
    driver.get("https://canvas.auckland.ac.nz/courses/"+course_dict[course_list[course_choice]]+"/modules")
    print("available lectures:")
    lecture_choose = input("choose an option: ")



except Exception as e:
    print(str(e))
    driver.quit()
driver.quit()

import os
import getpass
import requests
from selenium import webdriver
from pydub import AudioSegment
import speech_recognition as sr
from urllib.parse import urlparse
from clint.textui import progress
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

clear = lambda: os.system('cls')

options = Options()
options.headless = True

lect_link = input("whats the link? ")

driver = webdriver.Firefox(options=options)
driver.get("https://canvas.auckland.ac.nz/")

username = driver.find_element_by_name("j_username")
password = driver.find_element_by_name("j_password")
clear()
username.send_keys(input("userID: "))
password.send_keys(getpass.getpass(prompt="password: "))
print("getting session from the UoA login service. . .")
driver.find_element_by_name("_eventId_proceed").click()

driver.get(lect_link)
video_view = WebDriverWait( driver, 5 ).until(EC.presence_of_element_located((By.XPATH,'//*[@id="video_view"]')))
cookies = driver.get_cookies()
if len(cookies):
    print("good cookie. . .")
else:
    print("bad cookie . . .")

lect_link = lect_link.replace(".preview",".m4a")
print("valid lecture recording found. . .")
parsed = urlparse(lect_link)
file_name = parsed.path.split("/")[4]
if not os.path.exists(file_name):
    os.makedirs(file_name)
cookies = {
    cookies[0]['name'] : cookies[0]['value'],
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

response = requests.get(lect_link, headers=headers, cookies=cookies, stream=True)
with open(file_name+"/"+file_name+'.m4a', 'wb') as f:
    total_length = int(response.headers.get('content-length'))
    for chunk in progress.bar(response.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
        if chunk:
            f.write(chunk)
            f.flush()
driver.quit()

AudioSegment.from_file(file_name+"/"+file_name+'.m4a').export(file_name+"/"+file_name+'.wav', format="wav")

audio = AudioSegment.from_wav(file_name+"/"+file_name+'.wav')
if not os.path.exists(file_name+"/chunks"):
    os.makedirs(file_name+"/chunks")

n = len(audio)

counter = 1


interval = 5 * 1000
overlap = 0.2 * 1000

start = 0
end = 0

flag = 0

for i in range(0, 2 * n, interval):
    if i == 0:
        start = 0
        end = interval
    else:
        start = end - overlap
        end = start + interval
    if end >= n:
        end = n
        flag = 1
    chunk = audio[start:end]
    filename = file_name+'/chunks/chunk_'+str(counter)+'.wav'
    chunk.export(filename, format ="wav")
    counter = counter + 1
    AUDIO_FILE = filename
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio_listened = r.listen(source)
    try:
        rec = r.recognize_google(audio_listened)
        with open(file_name+"/Output.txt", "a") as text_file:
            text_file.write(rec+" ")
        print(rec+" ", end="")
    except sr.UnknownValueError:
        pass
    except sr.RequestError as e:
        print(e)
    if flag == 1:
        fh.close()
        break
driver.quit()

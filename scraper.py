import requests
import re
import time
import progressbar
import urllib.request as ur
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

class MyProgressBar():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()

def scroll(url):
    # Opens an invisible Firefox instance and scrolls down to access all videos until it can scroll no more.
    # Saves the URLs in a dictionary
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    time.sleep(3)  # Allow 2 seconds for the web page to open
    scroll_pause_time = 3 # You can set your own pause time. My laptop is a bit slow so I use 1 sec
    screen_height = driver.execute_script("return window.screen.height;")   # get the screen height of the web
    i = 1

    while True:
        # scroll one screen height each time
        driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))  
        i += 1
        time.sleep(scroll_pause_time)
        # update scroll height each time after scrolled, as the scroll height can change after we scrolled the page
        scroll_height = driver.execute_script("return document.body.scrollHeight;")  
        # Break the loop when the height we need to scroll to is larger than the total scroll height
        if (screen_height) * i > scroll_height:
            break
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    urls = {}
    i=0
    for parent in soup.find_all(class_="thumb-link"):
        link = parent.attrs['href']
        new_url = urljoin(url, link)
        url_wena, url_mala = new_url.split('?', 1)
        urls[url_wena] = i
        i = i+1
    
    print('Total videos found: ', len(urls))
    driver.quit()

    return urls

def extract_video_urls(url):
    print('Searching videos in: ',url,'\n\nPlease wait...\nIf you get less videos than expected, interrupt the script and execute it again.\n')
    url_dict = scroll(url)

    return url_dict

def get_url_code(user, year):
    # Retrieves the unique code that every user has. This code is needed for the final URL
    url =  'https://web.archive.org/web/' + str(year) + '*/http://plays.tv/u/' + user
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    print('---SEARCHING IN---> ' + url)
    driver.get(url)
    time.sleep(2)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    parent = soup.find_all(class_="captures-range-info")

    code = re.findall('<div class="captures-range-info">Saved <strong>1 time</strong> <a href="/web/([0-9]{14})', str(parent[0]))
    
    if len(code) == 0:
        print('User code not found in',url,'\n')
        code = get_url_code(user, year-1)
    print('Success! Archives.org made a copy of your plays.tv videos in ',year)
    driver.quit()

    return code[0]

def update_urls(url_dict):
    # Transforms the dictionary into a list and updates the old URLs so we can access to them.
    string = 'mp_'
    updated_list = []
    for key in url_dict:
        if string in key:
            new_key = key.replace('mp_/https','/http')
            updated_list.append(new_key)
        else:
            updated_list.append(key)
    return updated_list

def read_url(url):
    # Reads the source code of the webpage where the video can be found, and if so, returns the URL where the video is.
    # If not, return '0'
    req = ur.Request(url)
    req.add_header('user-agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36')
    f = ur.urlopen(req)
    s = f.read().decode()
    source_url = re.findall('<source res="720" src="(.*)" type="video/mp4"><source res="480"', s)
    if len(source_url) == 0:
        finished_source_url = '0'
    else:
        finished_source_url = 'https:'+source_url[0]
    f.close()
    return finished_source_url

def download_video_from(url, filename):
    # Downloads the video and prints the progress
    local_filename = url.split('/')[-8]
    video_name = filename+'.mp4'
    ur.urlretrieve(url, video_name, MyProgressBar()) 
    print(video_name, ' succesfully downloaded!\n')
    return 

if __name__ == '__main__':
    username = input("Please enter your plays.tv username:\n")

    code = get_url_code(username, 2019)

    url = 'https://web.archive.org/web/' + code + '/http://plays.tv/u/' + username

    url_dict = extract_video_urls(url)

    updated_list = update_urls(url_dict)
    
    for url in updated_list:
        response = requests.get(url)
        local_filename = url.split('/')[-1]
        real_url = read_url(url)
        if response.status_code == 200 and real_url != '0':
            print('Downloading: ', local_filename, 'from: ', real_url)
            download_video_from(real_url, local_filename)
        else:
            print(local_filename, 'video could not be recovered... :_(\n')
    
    print('All videos downloaded!')
    


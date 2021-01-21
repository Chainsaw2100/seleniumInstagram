import glob
import os
import os.path
import pickle
import random
import sys
import urllib
import urllib.request
from time import sleep

import autoit
import vk_api
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


def save_cookies(driver, location):
    pickle.dump(driver.get_cookies(), open(location, "wb"))


def load_cookies(driver, location, url=None):
    cookies = pickle.load(open(location, "rb"))
    driver.delete_all_cookies()
    # have to be on a page before you can add any cookies, any page - does not matter which
    driver.get("https://google.com" if url is None else url)
    for cookie in cookies:
        if isinstance(cookie.get('expiry'), float):  # Checks if the instance expiry a float
            cookie['expiry'] = int(cookie['expiry'])  # it converts expiry cookie to a int
        driver.add_cookie(cookie)


def delete_cookies(driver, domains=None):
    if domains is not None:
        cookies = driver.get_cookies()
        original_len = len(cookies)
        for cookie in cookies:
            if str(cookie["domain"]) in domains:
                cookies.remove(cookie)
        if len(cookies) < original_len:  # if cookies changed, we will update them
            # deleting everything and adding the modified cookie object
            driver.delete_all_cookies()
            for cookie in cookies:
                driver.add_cookie(cookie)
    else:
        driver.delete_all_cookies()


def login_inst(driver, location, usr_location):
    if os.path.isfile(location):
        load_cookies(driver, location)
        driver.get("https://www.instagram.com/")
        sleep(3)
    else:
        # Initial load of the domain that we want to save cookies for
        button = driver.find_element_by_xpath('//*[@id="react-root"]/section/main/article/div/div/div/div[2]/button')
        button.click()
        with open(usr_location, 'r') as f:
            user = f.read()
        user = user.split('\n')
        username = driver.find_element_by_name('username')
        username.send_keys(user[0])
        password = driver.find_element_by_name('password')
        password.send_keys(user[1])
        # instead of searching for the Button (Log In) you can simply press enter when you already selected the password or the username input element.
        submit = driver.find_element_by_tag_name('form')
        submit.submit()
        sleep(4)
        save_cookies(driver, location)
        sleep(4)
        driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/button').click()


def upload_rnd_photo(photos_dir):
    sleep(3)
    elem = driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[3]/button[2]').click()
    sleep(3)
    print("do")
    photos_list = glob.glob(photos_dir)
    print(photos_list)
    ActionChains(driver).move_to_element(driver.find_element_by_xpath(
        '//*[@id="react-root"]/section/nav[2]/div/div/div[2]/div/div/div[3]')).click().perform()
    handle = "[CLASS:#32770; TITLE:Открыть]"
    autoit.win_wait(handle, 60)
    photo = str(photos_list[random.randint(0, len(photos_list))])
    print(photo)
    autoit.control_set_text(handle, "Edit1", photo)
    autoit.control_click(handle, "Button1")
    print("posle")
    sleep(3)
    driver.find_element_by_xpath('//*[@id="react-root"]/section/div[1]/header/div/div[2]/button').click()  # save
    sleep(3)
    driver.find_element_by_xpath('//*[@id="react-root"]/section/div[1]/header/div/div[2]/button').click()  # share
    sleep(2)


# Path where you want to save/load cookies to/from aka C:\my\fav\directory\cookies.txt

def like_posts(posts_location):
    with open(posts_location, 'r') as f:
        post_list = f.read()
    print(post_list.split("\n"))
    print(len(post_list))
    for i in post_list:
        print(i)
        if i != "\n":
            driver.get('https://www.instagram.com/p/' + i)
            print("SUDA", i)
            sleep(8)

            button = driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button')
            button.click()
            sleep(8)


# sleep(2)
# driver.get('https://www.instagram.com/accounts/login/?source=auth_switcher')
# sleep(3)


# username = webdriver.find_element_by_name('username')
# username.send_keys(user[0])
# password = webdriver.find_element_by_name('password')
# password.send_keys(user[1])
# #instead of searching for the Button (Log In) you can simply press enter when you already selected the password or the username input element.
# submit = webdriver.find_element_by_tag_name('form')
# submit.submit()

sleep(3)


def vk_download(vklogin, vkpassword, vkid_location):
    # ======= Открываем сессию  с VK =======
    vk_session = vk_api.VkApi(vklogin, vkpassword)
    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    vk = vk_session.get_api()

    # ======= считываем список пользователей =======
    file_id = open(os.path.join(sys.path[0], vkid_location), 'r')
    data_list = file_id.readlines()
    id_list = []
    for line in data_list:
        id_list.append(line.strip())

    # ======= начинаем перебирать каждого пользователя =======
    for id_user in id_list:

        # создаем директорию с именем пользователя, если нет
        newpath = os.path.join(sys.path[0], id_user)
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        # посылаем запрос к VK API, count свой, но не более 200
        response = vk.photos.getAll(owner_id=int(id_user), count=10)

        # работаем с каждой полученной фотографией
        for i in range(len(response["items"])):
            # берём ссылку на максимальный размер фотографии
            photo_url = str(response["items"][i]["sizes"][len(response["items"][i]["sizes"]) - 1]["url"])
            urllib.request.urlretrieve(photo_url, newpath + '/' + str(response["items"][i]['id']) + '.jpg')


chromedriver_path = 'C:\\Users\\chainsaw\\Downloads\\chromedriver_win32\\chromedriver.exe'
location = "cookies.txt"
usr_location = "user.txt"
vkid_location = "id_users.txt"
with open(vkid_location, 'r') as f:
    vk = f.read()
vk = vk.split('\n')
photos_dir = "C:\\Users\\chainsaw\\*.jpg"
print(glob.glob(photos_dir))
print(photos_dir)
posts_location = "posts_list.txt"
login = ''
password = ''

# vk_download(login, password, vkid_location)
mobile_emulation = {

    "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},

    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}

chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get('https://www.instagram.com/')
sleep(3)
login_inst(driver, location, usr_location)
upload_rnd_photo(photos_dir)
driver = webdriver.Chrome()
login_inst(driver, location, usr_location)
like_posts(posts_location)

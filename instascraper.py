from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import json
import re
import time


NUM_PATH = '//span[@class="_fd86t"]'
USERNAME_PATH = '//*[@id="react-root"]/section/main/article/header/div[2]/div[1]/h1'
BIO_PATH = '//*[@id="react-root"]/section/main/article/header/div[2]/div[2]/span/span'
FULL_NAME_PATH = '//*[@id="react-root"]/section/main/article/div[1]/h2'
WEBSITE_PATH = '//*[@id="react-root"]/section/main/article/header/div[2]/div[2]/a'
FOLLOWER_BUTTON_PATH = '//*[@id="react-root"]/section/main/article/ul/li[2]/a'
FILENAME = 'data.json'
LOGIN_URL = 'https://www.instagram.com/accounts/login/?force_classic_login'



class InstaSpider():

    def __init__(self):
        datastr = open(FILENAME).read()
        self.data = json.loads(datastr)
        self.usernames_not_seen = ["hank","hank_app"]
        self.usernames_already_seen = []

        self.driver = webdriver.Chrome("/Users/hank/Study/Git/python/ins/chromedriver")
        self.url_login = LOGIN_URL
        self.login()
        self.scrape()

    def login(self):
        self.driver.get(self.url_login)

        self.driver.find_element_by_xpath("//input[@name='username']").send_keys(self.data['USERNAME'])
        self.driver.find_element_by_xpath("//input[@name='password']").send_keys(self.data['PASSWORD'])
        self.driver.find_element_by_xpath("//input[@type='submit']").click()

        # Wait for the login page to load
        try:
            WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.LINK_TEXT, "Instagram"))
                )
        except:
            print("oh shit!!!!")
        return

    def scrape_helper(self, username):

        return_dictionary = {}

        self.driver.get("https://www.instagram.com/{0}/".format(username))

        # get general information like number of posts, followers, following, bio, fullname, website
        try:
            numbers = self.driver.find_elements_by_xpath(NUM_PATH)
            numbers = [ int(elem.text) for elem in numbers ]
            number_dic = {"posts":numbers[0],"followers":numbers[1],"following":numbers[2]}
        except:
            number_dic = {}

        try:
            biotext = self.driver.find_element_by_xpath(BIO_PATH).text
        except:
            biotext = ""
        try:
            full_name = self.driver.find_element_by_xpath(FULL_NAME_PATH).text
        except:
            full_name = ""
        try:
            website = self.driver.find_element_by_xpath(WEBSITE_PATH).text
        except:
            website = ""

        return_dictionary["numbers"] = number_dic
        return_dictionary["bio"] = biotext
        return_dictionary["fullname"] = full_name
        return_dictionary["website"] = website


        # get the followers data
        scrape_type = "follower"
        try:
            self.driver.find_element_by_partial_link_text(scrape_type).click()
        except:
            print ("Cannot search followers of " + username)
            return return_dictionary

        # try:
        xpath = '/html/body/div[4]/div/div[2]/div/div[2]/div/div[2]/ul/li[1]/div/div[1]/div/div[1]/a'
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))

        # xpath = '/html/body/div[4]/div/div[2]/div/div[2]/div/div[2]/ul'
        # for i in range(int((self.numbers[1]-10)/9) + 2):
        #     print("scrolling...{}".format(scrape_type))
        #     time.sleep(3)
        #     self.driver.find_element_by_xpath(xpath).send_keys(Keys.END)

        liElements = self.driver.find_elements_by_xpath('/html/body/div[4]/div/div[2]/div/div[2]/div/div[2]/ul/li')
        follower_list = []
        for i in range(len(liElements)):
            li = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]/div/div[2]/div/div[2]/ul/li['+str(i+1)+']/div/div[1]/div/div[1]/a')
            curr_foll = li.text
            if curr_foll not in self.usernames_already_seen and curr_foll not in self.usernames_not_seen:
                follower_list.append(curr_foll)

        # except:
        #     follower_list = []


        return_dictionary["followers"] = follower_list

        return return_dictionary

    def scrape(self):

        # username = self.data['USERNAME']

        f = open('output.txt','w')
        count  = 0
        try:
            for username in self.usernames_not_seen:
                self.usernames_already_seen.append(username)
                dictionary = self.scrape_helper(username)

                f.write(username+str(dictionary)+'\n\n\n')
                if "followers" in dictionary:
                    self.usernames_not_seen += dictionary["followers"]
                if count == 3:
                    break
                count += 1
        finally:
            # f.write(str(self.usernames_already_seen)+'\n'+str(self.usernames_not_seen)+'\n'+str(dictionary))
            f.close()

        # self.driver.click()
        # self.driver.close()

i = InstaSpider()

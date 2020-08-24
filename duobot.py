"""
duobot
A Python bot to farm XP on Duolingo in timed practice mode
Author: Francesco Ramoni
        francesco[dot]ramoni@email.it
        https://github.com/framoni/
"""

import argparse
from fuzzywuzzy import fuzz
from googletrans import Translator
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException
import time


parser = argparse.ArgumentParser(description='A Python bot to farm XP on Duolingo in timed practice mode')
parser.add_argument('-u', '--username', help="Your account username", required=True)
parser.add_argument('-p', '--password', help="Your account password", required=True)
parser.add_argument('-l', '--headless', action="store_true", help="Whether to run in headless mode")

args = parser.parse_args()

# PARAMETERS

# url to be scraped
duo_url = 'https://www.duolingo.com/practice'
# request header
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

# set webdriver options
options = webdriver.ChromeOptions()
if args.headless:
    options.add_argument('headless')
    options.add_argument("--mute-audio")
options.add_argument(f'user-agent={user_agent}')

# BOTTING

# initialize translator
translator = Translator()

# initialize points counters
sess_points = 0
tot_points = 0

# pause in seconds after each answer
pause = 1

# create a new driver
browser = webdriver.Chrome(options=options)
browser.implicitly_wait(20)

print("Starting duobot...")

# get url
browser.get(duo_url)

# login
username = browser.find_element_by_xpath("//input[@data-test='email-input']")
username.send_keys(args.username)
pwd = browser.find_element_by_xpath("//input[@data-test='password-input']")
pwd.send_keys(args.password)
time.sleep(3)
login = browser.find_element_by_xpath("//button[@data-test='register-button']").click()

# start timed practice
browser.find_element_by_xpath("//button[@data-test='player-next']").click()

print("Ready to farm points! Please wait...")

while 1:
    try:
        # determine type of exercise
        header_text = browser.find_element_by_xpath("//h1[@data-test='challenge-header']").text
        if header_text == "Scegli il significato corretto":
            # translation with choices
            question_text = browser.find_element_by_xpath(
                "//h1[@data-test='challenge-header']/parent::div/following-sibling::div").text
            question_text = question_text.split("\n")
            del question_text[1::2]
            t = translator.translate(question_text[0], src="it", dest="de")
            ratios = []
            for ans in question_text[1:]:
                 ratios.append(fuzz.token_sort_ratio(t.text, ans))
            idx = ratios.index(max(ratios))
            # click on the correspondant radio button
            radios = browser.find_elements_by_xpath("//label[@data-test='challenge-choice']")
            choice = radios[idx]
            choice.click()
            browser.find_element_by_xpath("//button[@data-test='player-next']").click()
        elif header_text == "Scrivilo in italiano":
            phrase = browser.find_element_by_xpath("//div[@data-test='challenge-translate-prompt']").text
            t = translator.translate(phrase, src="de", dest="it")
            text_area = browser.find_element_by_xpath("//textarea[@data-test='challenge-translate-input']")
            text_area.send_keys(t.text)
            browser.find_element_by_xpath("//button[@data-test='player-next']").click()
        elif header_text == "Scrivilo in tedesco":
            phrase = browser.find_element_by_xpath("//div[@data-test='challenge-translate-prompt']").text
            t = translator.translate(phrase, src="it", dest="de")
            text_area = browser.find_element_by_xpath("//textarea[@data-test='challenge-translate-input']")
            text_area.send_keys(t.text)
            browser.find_element_by_xpath("//button[@data-test='player-next']").click()
        elif 'Scrivi "' in header_text:
            # browser.find_element_by_xpath("//button[@data-test='player-skip']").click()
            phrase = header_text
            phrase = phrase.replace('Scrivi "', '')
            phrase = phrase.replace('" in tedesco', '')
            t = translator.translate(phrase, src="it", dest="de")
            text_area = browser.find_element_by_xpath("//input[@data-test='challenge-text-input']")
            text_area.send_keys(t.text)
            browser.find_element_by_xpath("//button[@data-test='player-next']").click()
        elif header_text == "Scegli la parola che manca":
            browser.find_element_by_xpath("//button[@data-test='player-skip']").click()
        elif header_text == "Pronuncia questa frase":
            # skip_speaking
            browser.find_element_by_xpath("//button[@data-test='player-skip']").click()
        elif header_text == "Seleziona ciò che senti":
            # skip_listening
            browser.find_element_by_xpath("//button[@data-test='player-skip']").click()
        # pause
        time.sleep(pause)
        result = browser.find_element_by_xpath("//div[contains(@data-test, 'blame blame')]")
        if result.get_attribute('data-test') == 'blame blame-correct':
            sess_points += 1
        browser.find_element_by_xpath("//button[@data-test='player-next']").click()
        time.sleep(pause)
    except (ElementNotInteractableException, NoSuchElementException) as e:
        tot_points += sess_points
        print("Farmed {} XP points. Total: {}".format(sess_points, tot_points))
        sess_points = 0
        while not browser.current_url == "https://www.duolingo.com/learn":
            try:
                browser.find_element_by_xpath("//button[@data-test='player-next']").click()
            except:
                browser.find_element_by_xpath('//button[text()="No, grazie"]').click()
        # when practice session is over, start another one
        start_practice = browser.find_element_by_xpath("//a[@data-test='global-practice']").click()
        # start timed practice
        browser.find_element_by_xpath("//button[@data-test='player-next']").click()

# close the driver
browser.quit()
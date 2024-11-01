"""
duobot
A Python bot to farm XP on Duolingo in timed practice mode
Author: Francesco Ramoni
        francesco[dot]ramoni@email.it
        https://github.com/framoni/
"""

import argparse
from fuzzywuzzy import fuzz
import translators as ts
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


parser = argparse.ArgumentParser(description='A Python bot to farm XP on Duolingo in timed practice mode')
parser.add_argument('-u', '--username', help="Your account username", required=True)
parser.add_argument('-p', '--password', help="Your account password", required=True)
parser.add_argument('-l', '--headless', action="store_true", help="Whether to run in headless mode")

args = parser.parse_args()

# initialize translators

# _ = ts.preaccelerate_and_speedtest()

class Duobot:

    def __init__(self):
        # base url
        self.practice_url = 'https://www.duolingo.com/practice'

        # set webdriver options
        options = webdriver.ChromeOptions()
        if args.headless:
            options.add_argument('headless')
            options.add_argument("--mute-audio")
        # request header
        # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        # options.add_argument(f'user-agent={user_agent}')

        # initialize webdriver
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(30)

        # status variables
        self.loggedin = False


    def login(self):
        print("Logging in to Duolingo...")

        # get url
        self.browser.get(self.practice_url)

        # login
        username = self.browser.find_element(By.XPATH, "//input[@data-test='email-input']")
        username.send_keys(args.username)
        pwd = self.browser.find_element(By.XPATH, "//input[@data-test='password-input']")
        pwd.send_keys(args.password)
        self.browser.find_element(By.XPATH, "//button[@data-test='register-button']").click()

        # data processing pop consent
        self.browser.find_element(By.XPATH, "//button[@aria-label='Consent']").click()

        self.loggedin = True

        print("Successfully logged in.")

    def practice(self):
        if not self.loggedin:
            print("duobot has not logged in to the Duolingo web app. Log in first.")

        self.browser.get(self.practice_url)

        while 1:

            # parse the type of challenge
            header_text = self.browser.find_element(By.XPATH, "//h1[@data-test='challenge-header']").text

            # translation challenge
            if header_text == "Select the correct meaning":

                question_text = self.browser.find_element(By.XPATH, "//div[@lang='en']").text
                options = self.browser.find_elements(By.XPATH, "//span[@data-test='challenge-judge-text']")
                translation = ts.translate_text(question_text, translator='google', from_language='en', to_language='zh')
                choice = [idx for idx, it in enumerate(options) if it.text == translation]
                if len(choice) == 1:
                    # translation appears in the options
                    options[choice[0]].click()
                    self.browser.find_element(By.XPATH, "//button[@data-test='player-next']").click()
                else:
                    # translation doesn't correspond to any of the options
                    self.browser.find_element(By.XPATH, "//button[@data-test='player-skip']").click()
                # after being notified about the result, click on the "Continue" button
                self.browser.find_element(By.XPATH, "//button[@data-test='player-next']").click()

            elif header_text=="Write this in English":

                question_text = self.browser.find_element(By.XPATH, "//div[@lang='zh']").text
                translation = ts.translate_text(question_text, translator='google', from_language='zh',
                                                to_language='en')

                # find the word buttons, extract the words
                # pick one by one the buttons that compose the translation
                # hit ok
                
                pass


if __name__ == "__main__":
    duobot = Duobot()
    duobot.login()
    duobot.practice()
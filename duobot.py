"""
duobot
A Python bot to farm XP on Duolingo in timed practice mode
Author: Francesco Ramoni
        francesco[dot]ramoni@email.it
        https://github.com/framoni/
"""

import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By

from solver import Solver

parser = argparse.ArgumentParser(description='A Python bot to farm XP on Duolingo in timed practice mode')
parser.add_argument('-u', '--username', help="Your account username", required=True)
parser.add_argument('-p', '--password', help="Your account password", required=True)
parser.add_argument('-l', '--headless', action="store_true", help="Whether to run in headless mode")

args = parser.parse_args()


class Duobot:

    def __init__(self):
        # base url
        self.practice_url = 'https://www.duolingo.com/practice'

        # set webdriver options
        options = webdriver.ChromeOptions()
        if args.headless:
            options.add_argument('headless')
            options.add_argument("--mute-audio")  # is this necessary?

        # initialize webdriver
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(30)

        self.solver = Solver(browser=self.browser)

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
                self.solver.translation()

            # sentence composition challenges
            elif header_text=="Write this in English":
                self.solver.composition('zh', 'en')

            elif header_text == "Write this in Chinese":
                self.solver.composition('en', 'zh')

            # listening challenge
            elif header_text=="Tap what you hear":

                # skip this challenge for now
                self.browser.find_element(By.XPATH, "//button[@data-test='player-skip']").click()

            # after being notified about the result, click on the "Continue" button
            self.browser.find_element(By.XPATH, "//button[@data-test='player-next']").click()


if __name__ == "__main__":
    duobot = Duobot()
    duobot.login()
    duobot.practice()
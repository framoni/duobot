import json
import re
import translators as ts
from selenium import webdriver
from selenium.webdriver.common.by import By

# initialize translators

# _ = ts.preaccelerate_and_speedtest()

class Solver:

    def __init__(self, browser: webdriver.Chrome):
        self.browser = browser

        with open("data/solutions.json", "r") as f:
            self.solutions = json.loads(f.read())

    @staticmethod
    def extract_hanzi(text):
        # match and return Chinese characters from text
        chinese_characters = re.findall(r'[\u4e00-\u9fff]', text)
        return ''.join(chinese_characters)

    def append_solution(self, question_text, solution):
        self.solutions["zh(en)"][question_text] = solution

        with open("data/solutions.json", "w") as f:
            f.write(json.dumps(self.solutions))

    def translation(self):

        question_text = self.browser.find_element(By.XPATH, "//div[@lang='en']").text
        options = self.browser.find_elements(By.XPATH, "//span[@data-test='challenge-judge-text']")
        translation = ts.translate_text(question_text, translator='google', from_language='en',
                                        to_language='zh')
        choice = [idx for idx, it in enumerate(options) if self.extract_hanzi(it.text) == translation]
        if len(choice) == 1:
            # translation appears in the options
            options[choice[0]].click()
            self.browser.find_element(By.XPATH, "//button[@data-test='player-next']").click()
        else:
            # translation doesn't correspond to any of the options
            self.browser.find_element(By.XPATH, "//button[@data-test='player-skip']").click()

    def composition(self, from_language, to_language):

        question_text = self.browser.find_element(By.XPATH, "//div[@lang='{}']".format(from_language)).text

        # check if a solution was already stored
        if question_text in self.solutions["zh(en)"]:
            translation = self.solutions["zh(en)"][question_text]
        # if not, translate
        else:
            if from_language == 'zh':  # remove pinyin
                question_text = self.extract_hanzi(question_text)
            translation = ts.translate_text(question_text, translator='google', from_language=from_language,
                                            to_language=to_language)

        challenge_buttons = self.browser.find_elements(By.XPATH, "//button[@lang='{}']".format(to_language))

        # split translation in tokens
        for token in translation.split(" "):
            # convert to lower case
            token = token.lower()
            # search for a button with the same text as the token
            choice = [idx for idx, it in enumerate(challenge_buttons) if it.text.lower() == token]
            if len(choice) == 1:
                challenge_buttons[choice[0]].click()

        # submit answer
        self.browser.find_element(By.XPATH, "//button[@data-test='player-next']").click()

        # check if solution is wrong
        solution = self.browser.find_element(
            By.XPATH, "//div[@data-test='blame blame-incorrect']"
        ).text.split("\n")[1]
        if solution:
            # save the solution for future use
            self.append_solution(question_text, solution)

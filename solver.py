from ast import literal_eval
import json
import re
from recursion import Node
import translators as ts
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# initialize translators

# _ = ts.preaccelerate_and_speedtest()

class Solver:

    def __init__(self, browser: webdriver.Chrome, course="zh(en)"):
        self.browser = browser
        self.course = course
        self.pratice_finished = False

        with open("data/solutions.json", "r") as f:
            self.solutions = json.loads(f.read())

        with open("data/courses.json", "r") as f:
            self.params = json.loads(f.read())[self.course]

    def hide_pinyin(self):
        # press "Settings" button
        self.browser.find_element(By.XPATH, "//button[@class='_2VEsk bafGS _2LoNU VzbUl _1saKQ _1AgKJ']").click()
        # deselect "Show pronunciation"
        self.browser.find_element(By.XPATH, "//button[@aria-pressed='true']").click()
        # close the settings window
        self.browser.find_element(By.XPATH, "//span[text()='Done']").click()

    def append_solution(self, question_text, solution):
        self.solutions[self.course][question_text] = solution
        with open("data/solutions.json", "w") as f:
            f.write(json.dumps(self.solutions))

    def check_solution(self, question_text, to_language='en'):
        # check if solution is wrong
        try:
            blame_text = self.browser.find_element(
                By.XPATH, "//div[contains(@data-test, 'blame blame-')]"
            ).text
        except NoSuchElementException:
            # practice finished
            self.pratice_finished = True
            return
        if blame_text.split("\n")[0] == "Correct solution:":
            if to_language == "zh":
                solution = re.sub(r'[^\u4e00-\u9fff]', '', blame_text)
            else:
                solution = blame_text.split("\n")[1]
            # save the solution for future use
            self.append_solution(question_text, solution)

    @staticmethod
    def simplify(word):
        return re.sub(r'[^a-zA-Z\u4e00-\u9fff]', '', word).lower()

    def do_challenge(self, header_text):
        # translation challenge
        if header_text == "Select the correct meaning":
            self.translation(self.params["base_code"], self.params["studied_code"])

        # sentence composition challenges
        elif header_text == "Write this in English":
            self.composition(self.params["studied_code"], self.params["base_code"])

        elif header_text == "Write this in Chinese":
            self.composition(self.params["base_code"], self.params["studied_code"])

        # listening challenge
        elif header_text == "Tap what you hear":
            # skip this challenge for now
            self.browser.find_element(By.XPATH, "//button[@data-test='player-skip']").click()

    def translation(self, from_language, to_language):

        question_text = self.browser.find_element(By.XPATH, "//div[@lang='{}']".format(from_language)).text
        options = self.browser.find_elements(By.XPATH, "//span[@data-test='challenge-judge-text']")

        # check if a solution was already stored
        if question_text in self.solutions[self.course]:
            translation = self.solutions[self.course][question_text]
        # if not, translate
        else:
            translation = ts.translate_text(question_text, translator='google', from_language=from_language,
                                            to_language=to_language)

        choice = [idx for idx, it in enumerate(options) if it.text == translation]
        if len(choice) == 1:
            # translation appears in the options
            options[choice[0]].click()
            self.browser.find_element(By.XPATH, "//button[@data-test='player-next']").click()
        else:
            # translation doesn't correspond to any of the options
            self.browser.find_element(By.XPATH, "//button[@data-test='player-skip']").click()

        # check solution
        self.check_solution(question_text)

    def composition(self, from_language, to_language):

        question_text = self.browser.find_element(By.XPATH, "//div[@lang='{}']".format(from_language)).text

        # check if a solution was already stored
        if question_text in self.solutions[self.course]:
            translation = self.solutions[self.course][question_text]
        # if not, translate
        else:
            translation = ts.translate_text(question_text, translator='google', from_language=from_language,
                                            to_language=to_language)

        # remove all punctuation and white spaces in both the translation and the buttons' text
        translation = self.simplify(translation)

        challenge_buttons = self.browser.find_elements(By.XPATH, "//button[@lang='{}']".format(to_language))
        tokens = [self.simplify(button.text) for button in challenge_buttons]

        with open('composition.log', 'w') as f:
            f.write('[]')

        n = Node(translation, tokens)
        n.scan_tree(translation)

        with open('composition.log', 'r') as f:
            chosen_tokens = literal_eval(f.read())

        if len(chosen_tokens) == 0:
            challenge_buttons[0].click()
        for token in chosen_tokens:
            for button in challenge_buttons:
                if self.simplify(button.text) == token:
                    button.click()
                    challenge_buttons.remove(button)
                    break

        # submit answer
        self.browser.find_element(By.XPATH, "//button[@data-test='player-next']").click()

        # check solution
        self.check_solution(question_text, to_language=to_language)
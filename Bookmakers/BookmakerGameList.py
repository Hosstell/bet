from abc import ABC, abstractmethod
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import Levenshtein
from Bookmakers.BookmakerGame import WinlineGame


class BookmakerGameListABC(ABC):
    def __init__(self):
        self.browser = webdriver.Chrome()

    def get_game_by_player_names(self, names):
        games = self.get_games()

        max_value = 0
        max_value_game_link = None
        for game in games:
            for name in names:
                value1 = Levenshtein.jaro_winkler(name, game['left_name'])
                value2 = Levenshtein.jaro_winkler(name, game['right_name'])
                value = max(value1, value2)
                if value > max_value:
                    max_value = value
                    max_value_game_link = game['link']

        if max_value > 0.75:
            return WinlineGame(max_value_game_link)

    @abstractmethod
    def get_games(self):
        pass

    def __del__(self):
        self.browser.quit()
        self.browser.close()


class WinlineGameList(BookmakerGameListABC):
    def __init__(self):
        super().__init__()
        self.browser.get('https://winline.ru/stavki/sport/tennis/')
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "statistic")))

    def get_games(self):
        all_games = self.browser.find_elements_by_class_name('table__item')

        links = []
        for game in all_games:
            elems = game.find_elements_by_class_name('table-counter__wrap')
            if len(elems):
                a_tag = game.find_element_by_class_name('statistic__match')
                left_name, right_name = a_tag.find_element_by_class_name('statistic__team').text.split('\n')
                link = a_tag.get_attribute('href')
                links.append({
                    'left_name': left_name,
                    'right_name': right_name,
                    'link': link
                })
        return links


# class OneXBetGameList(BookmakerGameListABC):
#     def __init__(self):
#         super().__init__()
#         self.browser.get('https://1xbet.co.nz/ru/live/Tennis/')
#         # WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "statistic")))
#
#     def get_games(self):
#         all_games = self.browser.find_elements_by_class_name('c-events__teams')
#
#         links = []
#         for game in all_games:
#             left_name, right_name = game.text.split('\n')
#             link = game.find_element_by_xpath('..').get_attribute('href')
#             links.append({
#                 'left_name': left_name,
#                 'right_name': right_name,
#                 'link': link
#             })
#
#         return links


if __name__ == '__main__':
    pass
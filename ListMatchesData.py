#coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from MatchData import MatchData
import Levenshtein


class MyScoreMatchList:
    def __init__(self):
        self.window = webdriver.Chrome()
        self.window.minimize_window()
        self.window.get("https://www.myscore.ru/tennis/")
        WebDriverWait(self.window, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "container__fsbody")))
        tab_panel = self.window.find_element_by_class_name('tabs__list')
        tab_panel.find_elements_by_class_name('tabs__text')[1].click()

    def get_links_of_online_matches(self):
        matches = self.window.find_elements_by_class_name("event__match--live")[::2]
        match_ids = [match.get_attribute('id').split("_")[-1] for match in matches]
        link = 'https://www.myscore.ru/match/{0}/#point-by-point;1'
        return list(map(lambda x: link.format(x), match_ids))

    def get_game_by_player_names(self, names):
        games = self.window.find_elements_by_class_name('event__match')

        max_value = 0
        max_value_game = None
        for game in games:
            players = game.find_elements_by_class_name('event__participant')
            player_names = list(map(lambda x: x.text.lower(), players))

            for name in names:
                for player_name in player_names:
                    value = Levenshtein.jaro_winkler(name, player_name)
                    if value > max_value:
                        max_value = value
                        max_value_game = game

        if max_value > 0.75:
            id = max_value_game.get_attribute('id').split('_')[-1]
            return MatchData(id)

    def __del__(self):
        self.window.quit()
        self.window.close()


if __name__ == "__main__":
    a = MyScoreMatchList()
    print(a.get_game_by_player_names(['хачанов']))


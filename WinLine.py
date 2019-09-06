from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class WinLineGameList:
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.browser.minimize_window()
        self.browser.get("https://winline.ru/stavki/sport/tennis/")
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "statistic")))

    def get_active_game_links(self):
        all_games = self.browser.find_elements_by_class_name('table__item')
        links = []
        for game in all_games:
            elems = game.find_elements_by_class_name('table-counter__wrap')
            if len(elems):
                a_tag = game.find_element_by_class_name('statistic__match')
                links.append(a_tag.get_attribute('href'))
        return links

    def __del__(self):
        self.browser.quit()


class WinLineGame:
    def __init__(self, link):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1000,500')
        self.browser = webdriver.Chrome(chrome_options=options)
        self.browser.set_window_position(0, 500)
        self.browser.get(link)
        WebDriverWait(self.browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'markets-area')))

    def get_bets(self):
        try:
            main_table = self.browser.find_element_by_class_name('result-table')
            bets = main_table.find_elements_by_class_name('result-table__row')
            data = []
            for bet in bets:
                try:
                    bet_text = bet.find_element_by_class_name('result-table__item').text
                    if 'гейм' in bet_text:
                        game, set = bet_text.split(', ')
                        game = int(game.split(' ')[0])
                        set = int(set[0])

                        bet_values = bet.find_elements_by_class_name('result-table__count')
                        left_value, right_value = list(map(lambda x: float(x.text), bet_values))
                        data.append({
                            'set_game': (set, game),
                            'left_coeff': left_value,
                            'right_coeff': right_value
                        })
                except:
                    pass
            return data
        except:
            return []

    def get_names(self):
        name_elem = self.browser.find_element_by_class_name('sport-center__gamers')
        names = name_elem.find_elements_by_tag_name('h2')
        names = list(map(lambda x: x.text.split(' ')[0].lower(), names))
        return names

    def __del__(self):
        self.browser.quit()


if __name__ == '__main__':
    # link = WinLineGameList().get_active_game_links()
    link = 'https://winline.ru/stavki/sport/tennis/chellendzher_(m)/augsburg__germaniya/plus/5476777/'
    print(len(link))
    print(link[0])
    winline_game = WinLineGame(link)
    while True:
        print(winline_game.get_bets())
        time.sleep(1)
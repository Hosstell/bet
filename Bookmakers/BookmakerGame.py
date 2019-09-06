from abc import ABC, abstractmethod
from selenium import webdriver


class BookmakerGameABC(ABC):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--window-size=1000,500')
        self.browser = webdriver.Chrome(chrome_options=options)

    @abstractmethod
    def get_bets(self):
        pass

    def __del__(self):
        self.browser.quit()
        self.browser.close()


class WinlineGame(BookmakerGameABC):
    def __init__(self, link):
        super().__init__()
        self.browser.get(link)

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

#
# class OneXBetGame(BookmakerGameABC):
#     def __init__(self, link):
#         super().__init__()
#         self.browser.get(link)
#
#     def get_bets(self):
#         bets = self.browser.find_elements_by_class_name('min')
#         a = list(map(lambda x: x.text, bets))
#         print('get_bets')
#         pass


if __name__ == '__main__':
    one_x_bet_game = OneXBetGame('https://1xbet.co.nz/ru/live/Tennis/1486561-ITF-Gyor/205145064-Roberto-Cid-Subervi-Vit-Kopriva/')
    one_x_bet_game.get_bets()

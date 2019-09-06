from WinLine import WinLineGameList, WinLineGame
from Bookmakers.BookmakerGameHandler import BookmakerGameHandler
from ListMatchesData import MyScoreMatchList
from MatchData import MatchData
import time


class MainProcess:
    def __init__(self):
        self.games = []
        self.running_links = []
        self.max_active_game = 3
        # self.bookmaker_game_handler = BookmakerGameHandler()
        self.myscore_game_list = MyScoreMatchList()
        self.bets = []

    def run(self):
        while True:
            self.add_new_games()
            self.make_bets()
            self.check_bets()
            self.check_match_statuses()
            time.sleep(5)

    def add_new_games(self):
        active_links = self.myscore_game_list.get_links_of_online_matches()
        for active_link in active_links:
            if len(self.games) >= self.max_active_game:
                continue

            if active_link in self.running_links:
                continue

            myscore_game = MatchData(active_link)
            bookmaker_game_handler = BookmakerGameHandler(myscore_game.get_names())

            if bookmaker_game_handler.bookmaker_count():
                self.games.append({
                    'myscore': myscore_game,
                    'bookmaker_handler': bookmaker_game_handler,
                    'status': True
                })
            else:
                myscore_game.__del__()
            self.running_links.append(active_link)

    def make_bets(self):
        for game in self.games:
            bookmaker_handler = game['bookmaker_handler']
            myscore_game = game['myscore']

            try:
                bets = bookmaker_handler.get_bets()
            except:
                continue

            for bet in bets:
                if bet['set_game'][1] == 1:
                    continue

                try:
                    active_set_game = myscore_game.get_current_set_and_game()
                except:
                    active_set_game = None

                if not active_set_game and active_set_game == bet['set_game']:
                    continue

                ball_player = myscore_game.ball_player_set_game(*bet['set_game'])
                if not ball_player:
                    continue

                my_left_coeff = 1 / myscore_game.get_probability_by_set_game(*bet['set_game'], 'left')
                my_right_coeff = 1 / myscore_game.get_probability_by_set_game(*bet['set_game'], 'right')
                bet_left_coeff = bet['left_coeff']
                bet_right_coeff = bet['right_coeff']

                print('На LEFT')
                print('Пари. Сет-Гейм:{} \tКеф: {} ({})'.format(bet['set_game'], bet_left_coeff, round(1/bet_left_coeff*100, 2)))
                print('Мои условия: \t\t\tКеф: {} ({})'.format(round(my_left_coeff, 2), round(1/my_left_coeff*100, 2)))
                if bet_left_coeff > my_left_coeff:
                    print('Ставка сделана')
                    myscore_game.make_bet(bet['set_game'], 'left', bet_left_coeff)

                print()
                print('На RIGHT')
                print('Пари. Сет-Гейм:{} \tКеф: {} ({})'.format(bet['set_game'], bet_right_coeff, round(1 / bet_right_coeff*100, 2)))
                print('Мои условия: \t\t\tКеф: {} ({})'.format(round(my_right_coeff, 2), round(1/my_right_coeff * 100, 2)))
                if bet_right_coeff > my_right_coeff:
                    print('Ставка сделана')
                    myscore_game.make_bet(bet['set_game'], 'right', bet_right_coeff)

    def check_bets(self):
        for game in self.games:
            game['myscore'].check_bets()

    def check_match_statuses(self):
        for game in self.games:
            if not game['myscore'].is_active_game():
                game['status'] = False

        finished_games = list(filter(lambda x: not x['status'], self.games))
        self.games = list(filter(lambda x: x['status'], self.games))
        for finished_game in finished_games:
            pass


if __name__ == '__main__':
    MainProcess().run()

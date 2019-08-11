from WinLine import WinLineGameList, WinLineGame
from ListMatchesData import MyScoreMatchList
import time


class MainProcess:
    def __init__(self):
        self.games = []
        self.running_links = []
        self.max_active_game = 1
        self.winline_game_list = WinLineGameList()
        self.myscore_game_list = MyScoreMatchList()
        self.bets = []

    def run(self):
        while True:
            self.add_new_games()
            self.make_bets()
            time.sleep(5)

    def add_new_games(self):
        active_links = self.winline_game_list.get_active_game_links()
        for active_link in active_links:
            if len(self.games) >= self.max_active_game:
                continue

            if active_link in self.running_links:
                continue

            winline_game = WinLineGame(active_link)
            player_names = winline_game.get_names()
            myscore_game = self.myscore_game_list.get_game_by_player_names(player_names)
            if myscore_game:
                self.games.append({
                    'myscore': myscore_game,
                    'winline': winline_game
                })
            else:
                winline_game.__del__()
            self.running_links.append(active_link)

    def make_bets(self):
        for game in self.games:
            winline_game = game['winline']
            myscore_game = game['myscore']

            for bet in winline_game.get_bets():
                active_set_game = myscore_game.get_current_set_and_game()
                if active_set_game == bet['set_game']:
                    continue

                left_value = myscore_game.get_probability_by_set_game(*bet['set_game'], 'left')
                right_value = myscore_game.get_probability_by_set_game(*bet['set_game'], 'right')

                print(left_value, 1/bet['left_value'])
                if left_value > 1/bet['left_value']:
                    myscore_game.make_bet(bet['set_game'], 'left', bet['left_value'])

                print(right_value, 1/bet['right_value'])
                if right_value > 1/bet['right_value']:
                    myscore_game.make_bet(bet['set_game'], 'right', bet['right_value'])

    def check_bets(self):
        for game in self.games:
            game['myscore'].check_bets()


if __name__ == '__main__':
    MainProcess().run()

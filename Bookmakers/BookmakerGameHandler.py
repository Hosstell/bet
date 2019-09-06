from Bookmakers.BookmakerGameList import WinlineGameList

bookmakers_game_lists = [
    WinlineGameList()
]


class BookmakerGameHandler:
    def __init__(self, names):
        self.bookmaker_games = []
        for bookmakers_game_list in bookmakers_game_lists:
            game = bookmakers_game_list.get_game_by_player_names(names)
            if game:
                self.bookmaker_games.append(game)

    def get_bets(self):
        all_bets = []
        for bookmaker_game in self.bookmaker_games:
            all_bets.extend(bookmaker_game.get_bets())

        best_bets = []
        bet_set_games = list(set(map(lambda x: x['set_game'], all_bets)))
        for bet_set_game in bet_set_games:
            filtered_bets = list(filter(lambda x: x['set_game'] == bet_set_game, all_bets))
            max_left_coeff = max(map(lambda x: x['left_coeff'], filtered_bets))
            max_right_coeff = max(map(lambda x: x['right_coeff'], filtered_bets))

            best_bets.append({
                'set_game': bet_set_game,
                'left_coeff': max_left_coeff,
                'right_coeff': max_right_coeff
            })

        return best_bets

    def bookmaker_count(self):
        return len(self.bookmaker_games)


if __name__ == '__main__':
    bookmaker_game_handler = BookmakerGameHandler(['Чунг'])
    print(bookmaker_game_handler.get_bets())
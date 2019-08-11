#coding:utf-8
from selenium import webdriver
import time


def add_to_file(set_game, coeff, result):
    file = open('bets.log', 'a')
    line = '{}: {} - {}\n'.format(result, coeff, set_game)
    file.write(line)
    file.close()


class MatchData:
    def __init__(self, match_iD):
        self.id = match_iD
        self.data = {}
        self.MINIMAL_COUNT_SCORES = 2
        self.max_update_time = 5
        self.last_update_time = None
        self.bets = []
        self.AMOUNT = 50

        link = "https://www.myscore.ru/match/{0}/#point-by-point;1".format(match_iD)
        self.window = webdriver.Chrome()
        self.window.get(link)
        self.update_data()

    def update_data(self):
        try:
            self.__update_data()
            self.last_update_time = time.time()
        except:
            self.update_data()

    def __update_data(self):
        self.data["scores"] = self.__get_information_of_games()
        self.data["probability"] = self.__get_probability_ball_by_players()

    def __get_information_of_games(self):
        data = []
        set = self.__get_current_set()
        filling = self.__get_initial_filing()
        for i in range(set):
            self.__click_to_set(i + 1)
            statistics = self.window.find_element_by_id("tab-mhistory-{0}-history".format(i + 1))
            statistics = [elem.text for elem in statistics.find_elements_by_class_name("fifteen")]
            scores = [j.text for j in self.window.find_elements_by_class_name("match-history-score") if j.text != ""]
            game = []
            for j in range(len(statistics)):
                player = ["left", "right"][j % 2 == ("left" == filling[i])]
                score = statistics[j]
                score = self.__get_only_balls(score)

                if j < len(scores):
                    game.append({
                        "player": player,
                        "score": score,
                        "table": scores[j]
                    })
                else:
                    game.append({
                        "player": player,
                        "score": score,
                        "table": "live"
                    })

            data.append(game)
        return data

    def __get_only_balls(self, elem):
        elem = elem.replace(u"БП", u"")
        elem = elem.replace(u" ", u"")
        elem = elem.replace(u"СП", u"")
        elem = elem.replace(u"M\u041f", u"")
        return elem

    def __get_current_set(self):
        return int(self.window.find_element_by_class_name("mstat").text[0])

    def __get_current_game(self):
        scores = self.window.find_element_by_class_name("mstat").text.split("\n")[1]
        games = scores.split("(")[0].split(":")
        game = int(games[0]) + int(games[1]) + 1
        return game

    def get_current_set_and_game(self):
        return (self.__get_current_set(), self.__get_current_game())

    # Возращает первые подачи в сетах
    def __get_initial_filing(self):
        mas = []
        history = self.window.find_element_by_id('match-history-content')
        for i in range(1, 6, 1):
            name_class = "tab-mhistory-{0}-history".format(i)
            pages = history.find_elements_by_id(name_class)
            if len(pages):
                servers = pages[0].find_elements_by_class_name("server")
                if (servers[0].find_elements_by_class_name("icon-box") != []):
                    mas.append("left")
                else:
                    mas.append("right")
        return mas

    def __click_to_set(self, set):
        classname = "mhistory-{0}-history".format(set)
        self.window.find_element_by_id(classname).find_element_by_tag_name('a').click()

    def __get_probability_ball_by_players(self):
        return {
            "left": self.__get_probability_ball_by("left"),
            "right": self.__get_probability_ball_by("right")
        }

    def __get_probability_ball_by(self, player):
        left, right = 0, 0
        scores = [u"15", u"30", u"40"]
        for set in self.data["scores"]:
            for game in set:
                if game["player"] == player:
                    left_str = [point.split(u":")[0] for point in game["score"].split(u",")]
                    right_str = [point.split(u":")[1] for point in game["score"].split(u",")]
                    left_player = sum([1 for score in scores if score in left_str]) + left_str.count(u"A") + right_str[:-1].count(u"A")
                    right_player = sum([1 for score in scores if score in right_str]) + right_str.count(u"A") + left_str[:-1].count(u"A")

                    if left_player > right_player:
                        left_player += 1
                    else:
                        right_player += 1

                    left += left_player
                    right += right_player

        if left + right > self.MINIMAL_COUNT_SCORES:
            if player == "left":
                return left / (right+left)
            else:
                return right / (right + left)

    def get_probability_ball(self, player):
        self.__update_data_if_needed()
        return self.data["probability"][player]

    def get_probability_ball_by_player(self, player):
        self.__update_data_if_needed()
        return self.data["probability"][player]

    def __update_data_if_needed(self):
        if self.__check_time_last_update():
            self.update_data()

    def __check_time_last_update(self):
        return time.time() - self.last_update_time > self.max_update_time

    def get_probability_by_set_game(self, set, game, player):
        ball_player_in_game = self.__get_initial_filing()[int(set)-1]

        if int(game) % 2 == 0:
            ball_player_in_game = ['left', 'right'][ball_player_in_game == 'left']

        probability = self.get_probability_ball(ball_player_in_game)
        if player == ball_player_in_game:
            return probability
        else:
            return 1 - probability

    def who_is_winner_in_set_game(self, set, game):
        try:
            set_balls = self.data["scores"][set-1]
            scores_in_game = set_balls[game-1]['score']

            scores = [u"15", u"30", u"40"]
            left_str = [point.split(u":")[0] for point in scores_in_game.split(u",")]
            right_str = [point.split(u":")[1] for point in scores_in_game.split(u",")]
            left_player = sum([1 for score in scores if score in left_str]) + left_str.count(u"A") + right_str[:-1].count(u"A")
            right_player = sum([1 for score in scores if score in right_str]) + right_str.count(u"A") + left_str[:-1].count(u"A")

            return ['right', 'left'][left_player > right_player]
        except:
            pass

    def make_bet(self, set_game, player, coeff):
        maked_set_game = list(map(lambda x: x['set_game'], self.bets))
        if set_game not in maked_set_game:
            self.bets.append({
                'set_game': set_game,
                'player': player,
                'coeff': coeff,
                'status': False
            })

    def check_bets(self):
        for bet in self.bets:
            if bet['status']:
                continue

            winner_in_game = self.who_is_winner_in_set_game(*bet['set_game'])
            if not winner_in_game:
                continue

            if winner_in_game == bet['player']:
                add_to_file(bet['set_game'], bet['coeff'], self.AMOUNT*bet['coeff'])
            else:
                add_to_file(bet['set_game'], bet['coeff'], 0)

            bet['status'] = True

    def __del__(self):
        self.window.close()
        self.window.quit()


if __name__ == '__main__':
    a = [1, 2, 3]
    for b in a:
        if b == 2:
            del b
            break
    print(a)


    match = MatchData('IB1uavy9')
    print(match.get_current_set_and_game())
    print(match.get_probability_by_set_game(1, 8, 'right'))
    print(match.get_probability_by_set_game(1, 9, 'left'))
    print(match.get_probability_by_set_game(1, 9, 'right'))

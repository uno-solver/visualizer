import json
import os
import shutil


class Activity():

    def __init__(self, activity):
        self.activity = activity
        self.dealer = activity["dealer"]
        self.player = activity["player"]
        self.event = activity["event"]
        self.contents = activity["contents"]
        self.turn = activity["turn"] if "turn" in activity else None

    def __str__(self):
        return json.dumps(self.activity, indent=2, ensure_ascii=False)


class Turn():

    def __init__(self, activity):
        self.turn = activity.turn
        self.first_player = activity.contents["first_player"]
        self.white_wild = activity.contents["white_wild"]
        self.first_card = activity.contents["first_card"]
        self.play_order = activity.contents["play_order"]
        self.cards_receive = activity.contents["cards_receive"]
        self.activities = []
        self.turn_data = []

    def make_activities(self):
        activities = self.activities
        players = list(self.cards_receive.keys())

        res_list = []
        for activity in activities:
            temp_list = [""] * 7
            temp_list[0] = [activity.event]

            if activity.event == "first-player":
                played_card = activity.contents["first_card"]
                temp_list[1] = [self.parse_card(played_card)]
                for i in range(4):
                    temp_list[i + 2] = sorted([
                        self.parse_card(a)
                        for a in activity.contents["cards_receive"][players[i]]
                    ])
                first_player = activity.contents["first_player"]
                index = players.index(first_player)
                temp_list[index + 2] += ["", "First Player"]

            if activity.event == "next-player":
                played_card = activity.contents["card_before"]
                temp_list[1] = [self.parse_card(played_card)]
                next_player = activity.contents["next_player"]
                index = players.index(next_player)
                temp_list[index + 2] = sorted([
                    self.parse_card(a)
                    for a in activity.contents["card_of_player"]
                ])
                if not activity.contents["turn_right"]:
                    temp_list[6] = ["R"]

            if activity.event == "play-card":
                player = activity.player
                index = players.index(player)
                if not "card_play" in activity.contents:
                    temp_list[index + 2] = ["no card play"]
                elif activity.contents["yell_uno"]:
                    temp_list[1] = [self.parse_card(played_card)]
                    temp_list[index + 2] = [
                        self.parse_card(activity.contents["card_play"])
                    ]
                    temp_list[index + 2] += ["", "UNO"]
                else:
                    played_card = activity.contents["card_play"]
                    temp_list[1] = [self.parse_card(played_card)]
                    temp_list[index + 2] = [
                        self.parse_card(activity.contents["card_play"])
                    ]

            if activity.event == "special-logic":
                player = activity.player
                index = players.index(player)
                temp_list[index + 2] = [activity.contents["title"]]

            if activity.event == "shuffle-wild":
                for i in range(4):
                    temp_list[i + 2] = sorted([
                        self.parse_card(a)
                        for a in activity.contents["cards_receive"][players[i]]
                    ])

            if activity.event == "color-change-request":
                player = activity.contents["player"]
                index = players.index(player)
                temp_list[index + 2] = ["↓"]

            if activity.event == "color-of-wild":
                player = activity.player
                index = players.index(player)
                if "color_of_wild" in activity.contents:
                    temp_list[index + 2] = [
                        self.parse_color_of_wild(
                            activity.contents["color_of_wild"])
                    ]
                else:
                    temp_list[index + 2] = ["×"]

            if activity.event == "draw-card":
                player = activity.player
                index = players.index(player)
                temp_list[index + 2] = sorted([
                    self.parse_card(a) for a in activity.contents["card_draw"]
                ])

            if activity.event == "play-draw-card":
                player = activity.player
                index = players.index(player)
                if "card_play" in activity.contents:
                    temp_list[1] = [
                        self.parse_card(activity.contents["card_play"])
                    ]
                    temp_list[index + 2] = [
                        self.parse_card(activity.contents["card_play"])
                    ]
                else:
                    temp_list[index + 2] = ["no card play"]

            if activity.event == "penalty":
                player = activity.contents["player"]
                index = players.index(player)
                temp_list[index + 2] = sorted([
                    self.parse_card(a)
                    for a in activity.contents["cards_receive"]
                ])

                temp_list[index + 2] += ["", activity.contents["error"]]

            if activity.event == "public-card":
                player = activity.contents["player"]
                index = players.index(player)
                temp_list[index + 2] = sorted(
                    [self.parse_card(a) for a in activity.contents["cards"]])

            if activity.event == "challenge":
                src_player = activity.player
                src_index = players.index(src_player)
                target_player = activity.contents["target"]
                target_index = players.index(target_player)
                if activity.contents["is_challenge"]:
                    if activity.contents["result"]["is_challenge_success"]:
                        temp_list[src_index + 2] = ["※チャレンジ成功"]
                        temp_list[target_index + 2] = sorted([
                            self.parse_card(a) for a in
                            activity.contents["result"]["cards_receive"]
                        ])
                    else:
                        temp_list[src_index + 2] = sorted([
                            self.parse_card(a) for a in
                            activity.contents["result"]["cards_receive"]
                        ])
                        temp_list[target_index + 2] = ["※チャレンジ失敗"]
                else:
                    temp_list[src_index + 2] = ["チャレンジせず"]

            if activity.event == "say-uno-and-play-card":
                played_card = activity.contents["card_play"]
                temp_list[1] = [self.parse_card(played_card)]
                player = activity.player
                index = players.index(player)
                temp_list[index + 2] = sorted(
                    [self.parse_card(activity.contents["card_play"])])

            if activity.event == "say-uno-and-play-draw-card":
                player = activity.player
                index = players.index(player)
                if "card_play" in activity.contents:
                    temp_list[1] = [
                        self.parse_card(activity.contents["card_play"])
                    ]
                    temp_list[index + 2] = [
                        self.parse_card(activity.contents["card_play"])
                    ]
                else:
                    temp_list[index + 2] = ["no card play"]

            if activity.event == "finish-turn":
                for i in range(4):
                    temp_list[i + 2] = sorted([
                        self.parse_card(a) for a in
                        activity.contents["card_of_player"][players[i]]
                    ])
                    if players[i] not in activity.contents["score"]:
                        activity.contents["score"][players[i]] = -99999999
                    temp_list[i + 2] += [
                        "",
                        "score: " + str(activity.contents["score"][players[i]])
                    ]
                    temp_list[i + 2] += [
                        "", "total_score: " +
                        str(activity.contents["total_score"][players[i]])
                    ]

            res_list.append(temp_list)

        return res_list, players

    def parse_card(self, arg):
        if type(arg) == dict:
            if "color" in arg and "number" in arg:
                return arg["color"] + ": " + str(arg["number"])
            elif "color" in arg and "special" in arg:
                return arg["color"] + ": " + arg["special"]
        return arg

    def parse_color_of_wild(self, arg):
        return arg

    def __str__(self):
        temp = {}
        temp["turn"] = self.turn
        temp["first_player"] = self.first_player
        temp["white_wild"] = self.white_wild
        temp["first_card"] = self.first_card
        temp["play_order"] = self.play_order
        return json.dumps(temp, indent=2, ensure_ascii=False)


class UnparsedTurn(Turn):

    def __init__(self, turn: Turn):
        self.activities = turn.activities
        self.cards_receive = turn.cards_receive

    def parse_card(self, arg):
        special_dict = {
            "wild": "W",
            "skip": "Sk",
            "reverse": "Rv",
            "white_wild": "WhW",
            "draw_2": "D2",
            "wild_draw_4": "WD4",
            "wild_shuffle": "WSh"
        }
        if type(arg) == dict:
            if "color" in arg and "number" in arg:
                return [arg["color"], str(arg["number"])]
            elif "color" in arg and "special" in arg:
                return [arg["color"], special_dict[arg["special"]]]
        return arg

    def parse_color_of_wild(self, arg):
        return [arg, arg]


class Game():

    def __init__(self, path):
        self.path = path
        self.players = {}
        self.turns = []
        self._load_log(path)

    def _load_log(self, path):
        with open(path) as f:
            lines = f.readlines()

        for i, l in enumerate(lines):
            # if i > 1000000: break
            activity = Activity(json.loads(l))

            if activity.event == "join-room":
                self.players[activity.contents[
                    "player_code"]] = activity.contents["player_name"]
            elif activity.event == "first-player":
                turn = Turn(activity)
                turn.activities.append(activity)
                turn.turn_data.append(activity.event)
            elif activity.event == "finish-turn":
                turn.activities.append(activity)
                self.turns.append(turn)
                turn.turn_data.append(activity.event)
                turn.turn_data = list(set(turn.turn_data))
            elif activity.event == "finish-game":
                self.finish_game_activity = activity
            elif activity.event == "disconnect":
                if "turn" in locals() and "finish_game_activity" not in dir(
                        self):
                    turn.activities.append(activity)
                    turn.turn_data.append(activity.event)
            else:
                turn.activities.append(activity)
                turn.turn_data.append(activity.event)

    def save_separated_logs(self):
        dir_path = self.path[:-4]
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path, exist_ok=True)
        for i in range(len(self.turns)):
            turn_num = self.turns[i].turn
            with open(f"{dir_path}/{turn_num}.log", mode='w') as f:
                f.write('\n'.join([
                    json.dumps(self.turns[i].activities[j].activity,
                               ensure_ascii=False)
                    for j in range(len(self.turns[i].activities))
                ]))
                print(self.turns[i].activities[0].activity)
        game_data = {}
        game_data["players"] = self.players
        game_data["turn_data"] = [t.turn_data for t in self.turns]
        with open(f"{dir_path}/game_data.json", mode='w') as f:
            json.dump(game_data, f, indent=4)

    def __str__(self):
        return json.dumps(self.finish_game_activity.activity,
                          indent=2,
                          ensure_ascii=False)

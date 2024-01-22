from collections import defaultdict
from math import ceil, inf
from sys import argv
from matplotlib import gridspec
import matplotlib.pyplot as plt
import numpy

from structures import *
from constants import *

VERSION = "2"


def plot(dealerName, turns=None, saveName=None):
    if saveName == None:
        saveName = f"{dealerName}_{VERSION}"

    filePath = LOGS_DIR + f"{ dealerName }.log"
    imagePath = f"{ IMAGES_DIR }{ saveName }.png"

    # if os.path.isfile(imagePath):
    #     return imagePath

    if turns == None:
        game = Game(filePath)
        turns = game.turns

    playerList = []
    playerName = defaultdict(str)

    with open(filePath, 'r') as f:
        for line in f:
            data = json.loads(line)

            if data["event"] != "join-room":
                break

            player = data["player"]
            name = data["contents"]["player_name"].split("_")[0]

            playerList.append(player)
            playerName[player] = name

    n = len(turns)

    somoothing_window_size = (int(ceil(n / 150)) | 1) + 1
    moving_mean_window_size = ceil(n / 5)

    winCount = defaultdict(int)
    totalScore = defaultdict(int)

    profit = defaultdict(int)
    debt = defaultdict(int)

    winCountList = defaultdict(lambda: [0])
    totalScoreList = defaultdict(lambda: [0])

    winCountList = defaultdict(lambda: [0])
    totalScoreList = defaultdict(lambda: [0])

    deltaScoreList = defaultdict(lambda: [])
    deltaWinCountList = defaultdict(lambda: [])

    bestGain = defaultdict(lambda: (-inf, 0))
    worstLose = defaultdict(lambda: (inf, 0))

    challengeCount = [[0] * 4 for _ in range(4)]
    challengeSuccessCount = [[0] * 4 for _ in range(4)]

    for i, turn in enumerate(turns, 1):
        print(f"\r{ i } / { n }", end="")

        for activity in turn.activities:
            if activity.event == "first-player":
                for player in activity.contents["play_order"]:
                    winCount[playerName[player]] += 0

            if activity.event == "finish-turn":
                winner = activity.contents["winner"]
                winCount[playerName[winner]] += 1

                for code, score in activity.contents["score"].items():
                    player = playerName[code]

                    totalScore[player] += score
                    deltaScoreList[player].append(score)
                    deltaWinCountList[player].append((winner == code) - 1 / 4)

                    if bestGain[player][0] < score:
                        bestGain[player] = (score, i)

                    if worstLose[player][0] > score:
                        worstLose[player] = (score, i)

                    if code == winner: profit[player] += score
                    else: debt[player] += score

            if activity.event == "challenge" and activity.contents["is_challenge"]:
                challenger = playerList.index(activity.player)
                target = playerList.index(activity.contents["target"])
                success = activity.contents["result"]["is_challenge_success"]

                challengeCount[challenger][target] += 1
                challengeSuccessCount[challenger][target] += success

        for player, count in winCount.items():
            winCountList[player].append(count - i / 4)

        for player, score in totalScore.items():
            totalScoreList[player].append(score)

    print(dict(bestGain))
    print(dict(worstLose))

    fig = plt.figure(figsize=(20, 20), dpi=80)

    gs = gridspec.GridSpec(4, 2)
    winCount = fig.add_subplot(gs[0, 0])
    deltaWinCount = fig.add_subplot(gs[1, 0])
    totalScore = fig.add_subplot(gs[0, 1])
    deltaScore = fig.add_subplot(gs[1, 1])
    challengedCount = fig.add_subplot(gs[2, 0])

    winCount.set_title("Win-Count (deviation)")
    deltaWinCount.set_title(f"Win-Count Increment  MM ({ moving_mean_window_size } turns)")
    totalScore.set_title("Total Score")
    deltaScore.set_title(f"Total Score Increment MM ({ moving_mean_window_size } turns)")
    challengedCount.set_title("Challenged")

    winCount.set_xlim(0, n)
    deltaWinCount.set_xlim(0, n)
    totalScore.set_xlim(0, n)
    deltaScore.set_xlim(0, n)

    winCount.grid(axis="y")
    deltaWinCount.grid(axis="y")
    totalScore.grid(axis="y")
    deltaScore.grid(axis="y")

    somoothing_lernel = numpy.ones(somoothing_window_size) / somoothing_window_size
    moving_mean_lernel = numpy.ones(moving_mean_window_size) / moving_mean_window_size

    for player, data in sorted(winCountList.items()):
        data = numpy.array(data)
        data = numpy.convolve(data, somoothing_lernel, 'valid')
        data = numpy.insert(data, 0, [None] * (somoothing_window_size // 2))
        winCount.plot(data, linestyle="-", label=player)

    for player, data in sorted(deltaWinCountList.items()):
        data = numpy.array(data)
        data = numpy.convolve(data, moving_mean_lernel, 'same')
        data = numpy.convolve(data, somoothing_lernel, 'valid')
        data = numpy.insert(data, 0, [None] * (somoothing_window_size // 2))
        deltaWinCount.plot(data, linestyle="-", label=player)

    for player, data in sorted(totalScoreList.items()):
        data = numpy.array(data)
        data = numpy.convolve(data, somoothing_lernel, 'valid')
        data = numpy.insert(data, 0, [None] * (somoothing_window_size // 2))
        totalScore.plot(data, linestyle="-", label=player)

    for player, data in sorted(deltaScoreList.items()):
        data = numpy.array(data)
        data = numpy.convolve(data, moving_mean_lernel, 'same')
        data = numpy.convolve(data, somoothing_lernel, 'valid')
        data = numpy.insert(data, 0, [None] * (somoothing_window_size // 2))
        deltaScore.plot(data, linestyle="-", label=player)

    challengeCount = [
        *map(lambda raw: [*map(lambda x: f"{ x[0] } / { x[1] }", zip(raw[0], raw[1]))],
             zip(challengeSuccessCount, challengeCount))
    ]

    for i in range(4):
        challengeCount[i][i] = ""

    print(challengeCount)

    challengedCount.axis('off')
    challengedCount.axis('tight')

    index = [*map(lambda code: playerName[code], playerList)]

    # challengedCount.text(-0.080, -0.01, "Challenger", va="center", size="large", rotation=90)
    table = challengedCount.table(
        cellText=challengeCount,
        colLabels=index,
        rowLabels=index,
        loc="center",
        rowLoc="center",
        bbox=[0, 0, 1, 1],
    )
    table.add_cell(0, -1, 0, 0.05, text="Challenger \ Challenged", loc='center')

    winCount.legend(loc="lower left")
    deltaWinCount.legend(loc="lower left")
    totalScore.legend(loc="lower left")
    deltaScore.legend(loc="lower left")

    fig.savefig(imagePath)

    return imagePath


if __name__ == "__main__":
    plot(argv[1])

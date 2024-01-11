from collections import defaultdict
from math import inf
from sys import argv
import PIL
import matplotlib.pyplot as plt

from structures import *
from constants import *


def plot(dealerName, turns=None, saveName=None):
    if saveName == None:
        saveName = dealerName

    filePath = LOGS_DIR + f"{dealerName}.log"
    imagePath = f"{ IMAGES_DIR }{ saveName }.png"

    if os.path.isfile(imagePath):
        return imagePath

    if turns == None:
        game = Game(filePath)
        turns = game.turns

    playerName = defaultdict(str)

    with open(filePath, 'r') as f:
        for line in f:
            data = json.loads(line)

            if data["event"] != "join-room":
                break

            playerName[data["player"]] = data["contents"]["player_name"].split("_")[0]

    n = len(turns)

    winCount = defaultdict(int)
    totalScore = defaultdict(int)

    winCountList = defaultdict(lambda: [0])
    totalScoreList = defaultdict(lambda: [0])

    bestGain = defaultdict(lambda: (-inf, 0))
    worstLose = defaultdict(lambda: (inf, 0))

    for i, turn in enumerate(turns, 1):
        print(f"\r{ i } / { n }", end="")

        for activity in turn.activities:
            if activity.event == "first-player":
                for player in activity.contents["play_order"]:
                    winCount[playerName[player]] += 0

            if activity.event == "finish-turn":
                winCount[playerName[activity.contents["winner"]]] += 1

                for code, score in activity.contents["score"].items():
                    player = playerName[code]

                    totalScore[player] += score

                    if bestGain[player][0] < score:
                        bestGain[player] = (score, i)

                    if worstLose[player][0] > score:
                        worstLose[player] = (score, i)

        for player, count in winCount.items():
            winCountList[player].append(count - i / 4)

        for player, score in totalScore.items():
            totalScoreList[player].append(score)
    print()

    print(dict(bestGain))
    print(dict(worstLose))

    fig = plt.figure(figsize=(10, 10))

    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)

    ax1.set_title("Win Count (diff. from ave.)")
    ax2.set_title("Total Score")

    ax1.set_xlim(0, n)
    ax2.set_xlim(0, n)

    ax1.grid(axis="y")
    ax2.grid(axis="y")

    # ax1.hlines([0], 0, n, color="gray", linestyles=":")
    # ax2.hlines([0], 0, n, color="gray", linestyles=":")

    for player, counts in sorted(winCountList.items()):
        ax1.plot(counts, linestyle="-", label=player)

    for player, scores in sorted(totalScoreList.items()):
        ax2.plot(scores, linestyle="-", label=player)

    ax1.legend(loc="lower left")
    ax2.legend(loc="upper left")

    fig.savefig(imagePath)

    return imagePath


if __name__ == "__main__":
    plot(argv[1])

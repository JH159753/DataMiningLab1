from chessdotcom import get_player_game_archives
import pprint
import requests
import csv
import re #regex things for pulling data out of the PGN

printer = pprint.PrettyPrinter()
data = ['Game ID', 'opponent username', 'player elo', 'opponent elo', 'opening name', 'moves', 'game result', 'time format']

def get_games(username):
    #this part just pulls one game so I can pull the data from that game to put in the CSV
    allMonthsPlayed = get_player_game_archives(username)
    specificMonth = allMonthsPlayed.archives[0]
    allGamesInMonth = requests.get(specificMonth).json()
    #0 is probably the first game played that month
    specificGame = allGamesInMonth["games"][0]

    #this part is pulling the data I want to put in the CSV
    gameID = specificGame["url"]
    #regex to remove the part of the URL we don't need
    gameID = re.sub(r"https://www.chess.com/game/live/", "", gameID)

    #dependent on who is what color in the game
    if username == specificGame["white"]["username"] :
        opponentUsername = specificGame["black"]["username"] 
        opponentElo = specificGame["black"]["rating"]
        playerElo = specificGame["white"]["rating"]
        gameResult = specificGame["white"]["result"]
    else :
        opponentUsername = specificGame["white"]["username"]
        opponentElo = specificGame["white"]["rating"]
        playerElo = specificGame["black"]["rating"]
        gameResult = specificGame["black"]["result"]

    #regex to pull only what comes after chess.com/openings/ because thats the opening name
    pgn = specificGame["pgn"]
    openingName = re.search(r"\[ECOUrl \"https\:\/\/www.chess.com\/openings\/(.*?)\"\]", pgn).group(1)

    #probably also want to pull only moves from the pgn too
    moves = re.sub(r"\[.*?\]", "", pgn)
    moves = re.sub(r"\{.*?\}", "", moves)
    moves = re.sub(r"\n", "", moves)

    timeFormat = specificGame["time_class"]

    #printing stuff so I know it's working properly
    printer.pprint(gameID)
    printer.pprint(opponentUsername)
    printer.pprint(playerElo)
    printer.pprint(opponentElo)
    printer.pprint(openingName)
    printer.pprint(moves)
    printer.pprint(gameResult)
    printer.pprint(timeFormat)

    data = [gameID, opponentUsername, playerElo, opponentElo, openingName, moves, gameResult, timeFormat]
    with open("chess.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(data)

get_games("jayyych")
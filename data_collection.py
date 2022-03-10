from chessdotcom import get_player_game_archives
import pprint
import requests
import csv
import pandas as pd
import re #regex things for pulling data out of the PGN

printer = pprint.PrettyPrinter()
data = ['Game ID', 'opponent username', 'player elo', 'opponent elo', 'opening name', 'moves', 'game result', 'time format', 'player color' 'elo difference', 'amount of moves']

def save_one_game(specificGame, filename):
    #this part is pulling the data I want to put in the CSV
    gameID = specificGame["url"]
    #regex to remove the part of the URL we don't need
    gameID = re.sub(r"https://www.chess.com/game/live/", "", gameID)

    #dependent on who is what color in the game
    if "jayyych" == specificGame["white"]["username"] :
        opponentUsername = specificGame["black"]["username"] 
        opponentElo = specificGame["black"]["rating"]
        playerElo = specificGame["white"]["rating"]
        gameResult = specificGame["white"]["result"]
        playerColor = "white"
    else :
        opponentUsername = specificGame["white"]["username"]
        opponentElo = specificGame["white"]["rating"]
        playerElo = specificGame["black"]["rating"]
        gameResult = specificGame["black"]["result"]
        playerColor = "black"

    #regex to pull only what comes after chess.com/openings/ because thats the opening name
    pgn = specificGame["pgn"]
    match = re.search(r"\[ECOUrl \"https\:\/\/www.chess.com\/openings\/(.*?)\"\]", pgn)
    if match != None: 
        openingName = match.group(1)
    else :
        openingName = "not found"

    #probably also want to pull only moves from the pgn too
    moves = re.sub(r"\[.*?\]", "", pgn)
    moves = re.sub(r"\{.*?\}", "", moves)
    moves = re.sub(r"\n", "", moves)

    timeFormat = specificGame["time_class"]
    #calculates difference between my elo and opponent elo; if mine is higher, it will be positive, if mine is lower it will be negative
    eloDifference = playerElo - opponentElo

    if match != None:
        amountOfMoves = re.search("(\d+)\.+[^.]*$", moves).group(1)
    else:
        amountOfMoves = 0

    #saves the needed things into data
    data = [gameID, opponentUsername, playerElo, opponentElo, openingName, moves, gameResult, timeFormat, playerColor, eloDifference, amountOfMoves] 


    with open(filename, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)

def get_dataset(filename, rows=None):
    #add .csv to the filename
    filename = filename + ".csv"

    allMonthsPlayed = get_player_game_archives("jayyych")
    specificMonth = allMonthsPlayed.archives[0]
    allGamesInMonth = requests.get(specificMonth).json()
    #0 is probably the first game played that month
    specificGame = allGamesInMonth["games"][0]
    if rows == None:
        #pull literally everything
        allMonthsPlayed = get_player_game_archives("jayyych")
        amountOfMonths = len(allMonthsPlayed.archives)
        while (amountOfMonths > 0) :
            amountOfMonths -= 1
            specificMonth = allMonthsPlayed.archives[amountOfMonths]
            allGamesInMonth = requests.get(specificMonth).json()

            for game in allGamesInMonth["games"] :
                save_one_game(game, filename)
    else:
        #pull only the correct amount of rows
        gamesSaved = 0
        allMonthsPlayed = get_player_game_archives("jayyych")
        amountOfMonths = len(allMonthsPlayed.archives)
        while (amountOfMonths > 0) :
            amountOfMonths -= 1
            specificMonth = allMonthsPlayed.archives[amountOfMonths]
            allGamesInMonth = requests.get(specificMonth).json()
            for game in allGamesInMonth["games"] :
                if gamesSaved >= rows:
                    break
                save_one_game(game, filename)
                gamesSaved += 1

def main():
    get_dataset('chess')
    print(pd.read_csv('chess.csv'))

    
if __name__ == '__main__':
    main()
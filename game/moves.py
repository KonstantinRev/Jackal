import simplejson as json

from .models import Board
from .helpers import load_ships_p, is_water

# Here is all possible moves

MOVES = {
    1: "empty", # 18 empty tiles
    2: "h_arrow", # 3 horizontal arrows {4 options}
    3: "d_arrow", # 3 diagonal arrows {4 options}
    4: "h2_arrow", # 3 horizontal both arrows {2 options}
    5: "d2_arrow", # 3 diagonal both arrows {2 options}
    6: "arrow_3", # 3 3-way arrows {4 options}
    7: "h4_arrow", # 3 4-way horizontal arrows
    8: "d4_arrow", # 3 4-way diagonal arrows
    9: "horse", # 2 horse
    10: "empty", # 5 jungle-go
    11: "empty", # 4 desert-go
    12: "empty", # 2 swamp-go
    13: "empty", # 1 waterfall-go
    14: "empty", # 6 Ice
    15: "empty", # 3 pit
    16: "empty", # 4 crocs
    17: "empty", # 1 cannibal
    18: "empty", # 2 fortress
    19: "empty", # 1 ressurect
    20: "empty", # 5 gold (1 coin)
    21: "empty", # 5 gold (2 coin)
    22: "empty", # 3 gold (3 coin)
    23: "empty", # 2 gold (4 coin)
    24: "empty", # 1 gold (5 coin)
    25: "empty", # 1 treasure
    26: "airplane", # 1 airplane
    27: "empty", # 1 carramba
    28: "balloon", # 2 balloons
    29: "cannon", # 2 cannons
    30: "empty", # 1 lighthouse
    31: "empty", # 1 Ben Gan
    32: "empty", # 1 missioner
    33: "empty", # 1 Friday
    34: "empty", # 3 Rum1
    35: "empty", # 2 Rum2
    36: "empty", # 1 Rum3
    37: "empty", # 4 barrel of rum
    38: "empty", # 4 cave
    39: "empty", # 1 earthquake
    40: "empty", # 3 jungle
    41: "empty" # 2 cannabis
}


def Every(id, board_id, ice=None):
    '''
    Function take ID of tile and calculate moves that can be made from that tile
    Return: list of possible moves
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Load ships
    ships = load_ships_p(board_id)

    # Get empty list
    moves = []

    # if tile is ICE
    if ice != None:
        function_name = globals()[MOVES[ice]]
        moves = function_name(id, board_id)
    else:
        # Look for moves
        if id in ships: # Moves on ship
            if int(id / 100) == 11:
                moves.append(id + 100)
                if (id - 1) == 1112:
                    moves.append(id + 1)
                elif (id + 1) == 1122:
                    moves.append(id - 1)
                else:
                    moves.append(id + 1)
                    moves.append(id - 1)
            elif int(id % 100) == 23:
                moves.append(id - 1)
                if (id - 100) == 1223:
                    moves.append(id + 100)
                elif (id + 100) == 2223:
                    moves.append(id - 100)
                else:
                    moves.append(id + 100)
                    moves.append(id - 100)
            elif int(id / 100) == 23:
                moves.append(id - 100)
                if (id - 1) == 2312:
                    moves.append(id + 1)
                elif (id + 1) == 2322:
                    moves.append(id - 1)
                else:
                    moves.append(id + 1)
                    moves.append(id - 1)
            elif int(id % 100) == 11:
                moves.append(id + 1)
                if (id - 100) == 1211:
                    moves.append(id + 100)
                elif (id + 100) == 2211:
                    moves.append(id - 100)
                else:
                    moves.append(id + 100)
                    moves.append(id - 100)
            else:
                print('Error, check moves.py->Every')

        elif is_water(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3], board_id): # movement in water
            water = is_water(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3], board_id)
            for k in (-1, 0 , 1):
                for l in (-1, 0, 1):
                    try:
                        if ((k == 0) and (l == 0)): # Tile under pirat is not a move
                            pass
                        elif (0 <= int((int(str(id)[0:2]) - 11) + k) <= 12) and (0 <= int((int(str(id)[2:4]) - 11) + l) <= 12) and board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3] in ships: # Try to escape out of borders
                            moves.append(board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3])
                        else:
                            if (((int(str(id)[0:2]) - 11) + k) < 0) or (((int(str(id)[2:4]) - 11) + l) < 0):
                                pass
                            else:
                                if water and is_water(board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3], board_id):
                                    moves.append(board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3])
                    except:
                        pass

        else: # moves on ground
            function_name = globals()[MOVES[board[(int(str(id)[0:2]) - 11)][(int(str(id)[2:4]) - 11)][1]]]
            moves = function_name(id, board_id)

    return moves

def empty(id, board_id):
    '''
    Function take ID of tile and returns every move in 3x3 (exclude water)
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Load ships
    ships = load_ships_p(board_id)

    # Get empty list
    moves = []

    # Look for moves
    for k in (-1, 0 , 1):
        for l in (-1, 0, 1):
            if ((k == 0) and (l == 0)): # Tile under pirat is not a move
                pass
            elif board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3] in ships:
                moves.append(board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3])
            else:
                if not is_water(board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3], board_id):
                    moves.append(board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3])
    return moves

def horse(id, board_id):
    '''
    Function take ID of tile and returns every move of horse
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Load ships
    ships = load_ships_p(board_id)

    # Get empty list
    moves = []

    # Look for moves
    for k in (-2, 2):
        for l in (-1, 1):
            if (0 <= int((int(str(id)[0:2]) - 11) + k) <= 12) and (0 <= int((int(str(id)[2:4]) - 11) + l) <= 12): # Try to escape out of borders
                if board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3] in ships:
                    moves.append(board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3])
                else:
                    moves.append(board[(int(str(id)[0:2]) - 11) + k][(int(str(id)[2:4]) - 11) + l][3])
    for k2 in (-1, 1):
        for l2 in (-2, 2):
            if (0 <= int((int(str(id)[0:2]) - 11) + k2) <= 12) and (0 <= int((int(str(id)[2:4]) - 11) + l2) <= 12): # Try to escape out of borders
                if board[(int(str(id)[0:2]) - 11) + k2][(int(str(id)[2:4]) - 11) + l2][3] in ships: 
                    moves.append(board[(int(str(id)[0:2]) - 11) + k2][(int(str(id)[2:4]) - 11) + l2][3])
                else:
                    moves.append(board[(int(str(id)[0:2]) - 11) + k2][(int(str(id)[2:4]) - 11) + l2][3])
    return moves


def airplane(id, board_id):
    '''
    Function take ID of tile and returns every move on board
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # If airplane already used - make it empty tile
    if get_board.airplane:
        # Get empty list
        moves = []

        # Find ID in board
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j][3] == id:
                    pass
                else:
                    moves.append(board[i][j][3])
    else:
        return empty(id, board_id)

    return moves


def h_arrow(id, board_id):
    '''
    Function take ID of tile and returns moves for arrow
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get empty list
    moves = []

    # Look for moves
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 1:
        moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) + 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 2:
        moves.append(board[(int(str(id)[0:2]) - 11) - 1][(int(str(id)[2:4]) - 11)][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 3:
        moves.append(board[(int(str(id)[0:2]) - 11)][(int(str(id)[2:4]) - 11) - 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 4:
        moves.append(board[(int(str(id)[0:2]) - 11) + 1][(int(str(id)[2:4]) - 11)][3])

    return moves


def d_arrow(id, board_id):
    '''
    Function take ID of tile and returns moves for arrow
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get empty list
    moves = []

    # Look for moves
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 1:
        moves.append(board[(int(str(id)[0:2]) - 11) - 1][(int(str(id)[2:4]) - 11) + 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 2:
        moves.append(board[(int(str(id)[0:2]) - 11) - 1][(int(str(id)[2:4]) - 11) - 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 3:
        moves.append(board[(int(str(id)[0:2]) - 11) + 1][(int(str(id)[2:4]) - 11) - 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 4:
        moves.append(board[(int(str(id)[0:2]) - 11) + 1][(int(str(id)[2:4]) - 11) + 1][3])

    return moves


def h2_arrow(id, board_id):
    '''
    Function take ID of tile and returns moves for arrow
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get empty list
    moves = []

    # Look for moves
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 1:
        moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) + 1][3])
        moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) - 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 2:
        moves.append(board[(int(str(id)[0:2]) - 11) + 1][int(str(id)[2:4]) - 11][3])
        moves.append(board[(int(str(id)[0:2]) - 11) - 1][int(str(id)[2:4]) - 11][3])

    return moves


def d2_arrow(id, board_id):
    '''
    Function take ID of tile and returns moves for arrow
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get empty list
    moves = []

    # Look for moves
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 1:
        moves.append(board[int(str(id)[0:2]) - 11 - 1][(int(str(id)[2:4]) - 11) + 1][3])
        moves.append(board[int(str(id)[0:2]) - 11 + 1][(int(str(id)[2:4]) - 11) - 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 2:
        moves.append(board[int(str(id)[0:2]) - 11 + 1][(int(str(id)[2:4]) - 11) + 1][3])
        moves.append(board[int(str(id)[0:2]) - 11 - 1][(int(str(id)[2:4]) - 11) - 1][3])

    return moves


def arrow_3(id, board_id):
    '''
    Function take ID of tile and returns moves for arrow
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get empty list
    moves = []

    # Look for moves
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 1:
        moves.append(board[(int(str(id)[0:2]) - 11) - 1][(int(str(id)[2:4]) - 11) - 1][3])
        moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) + 1][3])
        moves.append(board[(int(str(id)[0:2]) - 11) + 1][int(str(id)[2:4]) - 11][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 2:
        moves.append(board[(int(str(id)[0:2]) - 11) + 1][(int(str(id)[2:4]) - 11) - 1][3])
        moves.append(board[(int(str(id)[0:2]) - 11) - 1][int(str(id)[2:4]) - 11][3])
        moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) + 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 3:
        moves.append(board[(int(str(id)[0:2]) - 11) + 1][(int(str(id)[2:4]) - 11) + 1][3])
        moves.append(board[(int(str(id)[0:2]) - 11) - 1][int(str(id)[2:4]) - 11][3])
        moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) - 1][3])
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 4:
        moves.append(board[(int(str(id)[0:2]) - 11) - 1][(int(str(id)[2:4]) - 11) + 1][3])
        moves.append(board[(int(str(id)[0:2]) - 11) + 1][int(str(id)[2:4]) - 11][3])
        moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) - 1][3])

    return moves


def h4_arrow(id, board_id):
    '''
    Function take ID of tile and returns moves for arrow
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get empty list
    moves = []

    # Look for moves
    moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) + 1][3])
    moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) - 1][3])
    moves.append(board[(int(str(id)[0:2]) - 11) + 1][int(str(id)[2:4]) - 11][3])
    moves.append(board[(int(str(id)[0:2]) - 11) - 1][int(str(id)[2:4]) - 11][3])

    return moves


def d4_arrow(id, board_id):
    '''
    Function take ID of tile and returns moves for arrow
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get empty list
    moves = []

    # Look for moves
    moves.append(board[(int(str(id)[0:2]) - 11) - 1][(int(str(id)[2:4]) - 11) + 1][3])
    moves.append(board[(int(str(id)[0:2]) - 11) + 1][(int(str(id)[2:4]) - 11) + 1][3])
    moves.append(board[(int(str(id)[0:2]) - 11) + 1][(int(str(id)[2:4]) - 11) - 1][3])
    moves.append(board[(int(str(id)[0:2]) - 11) - 1][(int(str(id)[2:4]) - 11) - 1][3])

    return moves


def cannon(id, board_id):
    '''
    Function take ID of tile and returns nearest water in the direction of cannon
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Load ships
    ships = load_ships_p(board_id)

    # Get empty list
    moves = []

    # Look for moves
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 1:
        for k in range(12 - (int(str(id)[2:4]) - 11) + 1):
            if board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) + k][0] == -1 or board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) + k][0] in ships:
                moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) + k][3])
                break
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 2:
        for k in range((int(str(id)[0:2]) - 11) + 1):
            if board[(int(str(id)[0:2]) - 11) - k][int(str(id)[2:4]) - 11][0] == -1 or board[(int(str(id)[0:2]) - 11) - k][int(str(id)[2:4]) - 11][0] in ships:
                moves.append(board[(int(str(id)[0:2]) - 11) - k][int(str(id)[2:4]) - 11][3])
                break
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 3:
        for k in range((int(str(id)[2:4]) - 11) + 1):
            if board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) - k][0] == -1 or board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) - k][0] in ships:
                moves.append(board[int(str(id)[0:2]) - 11][(int(str(id)[2:4]) - 11) - k][3])
                break
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][2] == 4:
        for k in range(12 - (int(str(id)[0:2]) - 11) + 1):
            if board[(int(str(id)[0:2]) - 11) + k][int(str(id)[2:4]) - 11][0] == -1 or board[(int(str(id)[0:2]) - 11) + k][int(str(id)[2:4]) - 11][0] in ships:
                moves.append(board[(int(str(id)[0:2]) - 11) + k][int(str(id)[2:4]) - 11][3])
                break

    return moves


def balloon(id, board_id):
    '''
    Function take ID of tile and returns ID of ship of team
    Return: list of possible moves 
    '''

    # Get board
    get_board = Board.objects.get(pk=board_id)

    # Load ships
    ships = load_ships_p(board_id)

    # Look for ship
    moves = [int(ships[int(get_board.mover[0]) - 1])]

    return moves


def Cave(id, board_id):
    '''
    Function return all opened caves
    Return: list of possible moves 
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get empty list
    moves = []

    # Look for moves
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j][1] == 38:
                if board[i][j][3] != id and board[i][j][0] == 2:
                    moves.append(board[i][j][3])

    return moves

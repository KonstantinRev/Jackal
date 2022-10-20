import simplejson as json

from .models import Board

# Here is some functions for calculation

def load_ships_p(board_id):
    '''
    Function load all ships to a list with int's
    Return: list with four ID (int)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    # return ships positions
    return [int(get_board.ship1), int(get_board.ship2), int(get_board.ship3), int(get_board.ship4)]


def is_water(tile_id, board_id):
    '''
    Function check if tile is water tile
    Return: True - is tile is water, False - if tile is not water
    '''

    # Get board from database and unpack it
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Check if tile is water
    if board[int(str(tile_id)[0:2]) - 11][int(str(tile_id)[2:4]) - 11][0] == -1:
        return True
    return False


def what_turn(board_id):
    '''
    Function return the number of team, who's turn is now
    Return: number of team (int)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    return int(get_board.turn)

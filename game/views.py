from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.db.models import Q
from random import randrange
import simplejson as json

from .models import Board, User, Turns
from .moves import Every, Cave
from .helpers import load_ships_p, is_water, what_turn

# Create your views here.

# Make list of action moves
MOVES = {
    0: "move_water", # 0, else: water or ships
    1: "move_stop", # 18 empty tiles
    2: "move_auto", # 3 horizontal arrows {4 options}
    3: "move_auto", # 3 diagonal arrows {4 options}
    4: "move_next", # 3 horizontal both arrows {2 options}
    5: "move_next", # 3 diagonal both arrows {2 options}
    6: "move_next", # 3 3-way arrows {4 options}
    7: "move_next", # 3 4-way horizontal arrows
    8: "move_next", # 3 4-way diagonal arrows
    9: "move_next", # 2 horse
    10: "move_jungle", # 5 jungle-go
    11: "move_desert", # 4 desert-go
    12: "move_swamp", # 2 swamp-go
    13: "move_waterfall", # 1 waterfall-go
    14: "move_ice", # 6 Ice
    15: "move_pit", # 3 pit
    16: "move_croc", # 4 crocs
    17: "move_cannibal", # 1 cannibal
    18: "move_stop", # 2 fortress
    19: "move_stop", # 1 ressurect
    20: "move_stop", # 5 gold (1 coin)
    21: "move_stop", # 5 gold (2 coin)
    22: "move_stop", # 3 gold (3 coin)
    23: "move_stop", # 2 gold (4 coin)
    24: "move_stop", # 1 gold (5 coin)
    25: "move_stop", # 1 treasure
    26: "move_airplane", # 1 airplane
    27: "move_stop", # 1 carramba
    28: "move_auto", # 2 balloons
    29: "move_auto", # 2 cannons
    30: "move_lighthouse", # 1 lighthouse
    31: "move_bengan", # 1 Ben Gan
    32: "move_missioner", # 1 missioner
    33: "move_friday", # 1 Friday
    34: "move_rum", # 3 Rum1
    35: "move_rum", # 2 Rum2
    36: "move_rum", # 1 Rum3
    37: "move_barrel", # 4 barrel of rum
    38: "move_cave", # 4 cave
    39: "move_earthquake", # 1 earthquake
    40: "move_stop", # 3 jungle
    41: "move_cannabis" # 2 cannabis
}

@login_required
def pre_create_board(request):
    '''
    Function render html for game creation page
    Return: HTML page
    Login required
    '''
    users = []

    for user in User.objects.all():
        users.append(user.username)

    return render(request, "game/create.html", {
        'users': users
        })


@login_required
def create_board(request):
    '''
    Function create new board and fill it
    Return: redirect to game page
    Login required
    '''

    if request.method == "POST":

        # Look for Users
        user1_name = request.POST["pirat1_chosen"]
        user2_name = request.POST["pirat2_chosen"]
        user3_name = request.POST["pirat3_chosen"]
        user4_name = request.POST["pirat4_chosen"]

        # Create board
        board = Board() 

        # Load Users
        board.user1 = User.objects.get(username=user1_name)
        board.user2 = User.objects.get(username=user2_name)
        board.user3 = User.objects.get(username=user3_name)
        board.user4 = User.objects.get(username=user4_name)

        # Create ships
        board.ship1 = 1117
        board.ship2 = 1723
        board.ship3 = 2317
        board.ship4 = 1711
        
        # Create list of coins
        coins = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
        board.coins = json.dumps(coins)
        board.treasure = 0

        # Create pirats
        pirats = [
            [[1117, 0, 0, 0], [1117, 0, 0, 0], [1117, 0, 0, 0]], # Team 1
            [[1723, 0, 0, 0], [1723, 0, 0, 0], [1723, 0, 0, 0]], # Team 2
            [[2317, 0, 0, 0], [2317, 0, 0, 0], [2317, 0, 0, 0]], # Team 3
            [[1711, 0, 0, 0], [1711, 0, 0, 0], [1711, 0, 0, 0]] # Team 4
        ]
        board.pirats = json.dumps(pirats)

        # Create rum
        board.rum = json.dumps([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        # Create persons
        board.bengan = '100000000'
        board.friday = '1000000'
        board.missioner = '1000000000'

        # Make variables
        board.mover = ''
        board.chosen = ''
        board.event = 0
        board.cave = 0
        board.turn = 1

        # Create Board 13x13
        new_board = [
            [[-1, 0, 0, 1111], [-1, 0, 0, 1112], [-1, 0, 0, 1113], [-1, 0, 0, 1114], [-1, 0, 0, 1115], [-1, 0, 0, 1116], [-1, 0, 0, 1117], [-1, 0, 0, 1118], [-1, 0, 0, 1119], [-1, 0, 0, 1120], [-1, 0, 0, 1121], [-1, 0, 0, 1122], [-1, 0, 0, 1123]],
            [[-1, 0, 0, 1211], [-1, 0, 0, 1212], [1, 0, 0, 1213], [1, 0, 0, 1214], [1, 0, 0, 1215], [1, 0, 0, 1216], [1, 0, 0, 1217], [1, 0, 0, 1218], [1, 0, 0, 1219], [1, 0, 0, 1220], [1, 0, 0, 1221], [-1, 0, 0, 1222], [-1, 0, 0, 1223]],
            [[-1, 0, 0, 1311], [1, 0, 0, 1312], [1, 0, 0, 1313], [1, 0, 0, 1314], [1, 0, 0, 1315], [1, 0, 0, 1316], [1, 0, 0, 1317], [1, 0, 0, 1318], [1, 0, 0, 1319], [1, 0, 0, 1320], [1, 0, 0, 1321], [1, 0, 0, 1322], [-1, 0, 0, 1323]],
            [[-1, 0, 0, 1411], [1, 0, 0, 1412], [1, 0, 0, 1413], [1, 0, 0, 1414], [1, 0, 0, 1415], [1, 0, 0, 1416], [1, 0, 0, 1417], [1, 0, 0, 1418], [1, 0, 0, 1419], [1, 0, 0, 1420], [1, 0, 0, 1421], [1, 0, 0, 1422], [-1, 0, 0, 1423]],
            [[-1, 0, 0, 1511], [1, 0, 0, 1512], [1, 0, 0, 1513], [1, 0, 0, 1514], [1, 0, 0, 1515], [1, 0, 0, 1516], [1, 0, 0, 1517], [1, 0, 0, 1518], [1, 0, 0, 1519], [1, 0, 0, 1520], [1, 0, 0, 1521], [1, 0, 0, 1522], [-1, 0, 0, 1523]],
            [[-1, 0, 0, 1611], [1, 0, 0, 1612], [1, 0, 0, 1613], [1, 0, 0, 1614], [1, 0, 0, 1615], [1, 0, 0, 1616], [1, 0, 0, 1617], [1, 0, 0, 1618], [1, 0, 0, 1619], [1, 0, 0, 1620], [1, 0, 0, 1621], [1, 0, 0, 1622], [-1, 0, 0, 1623]],
            [[-1, 0, 0, 1711], [1, 0, 0, 1712], [1, 0, 0, 1713], [1, 0, 0, 1714], [1, 0, 0, 1715], [1, 0, 0, 1716], [1, 0, 0, 1717], [1, 0, 0, 1718], [1, 0, 0, 1719], [1, 0, 0, 1720], [1, 0, 0, 1721], [1, 0, 0, 1722], [-1, 0, 0, 1723]],
            [[-1, 0, 0, 1811], [1, 0, 0, 1812], [1, 0, 0, 1813], [1, 0, 0, 1814], [1, 0, 0, 1815], [1, 0, 0, 1816], [1, 0, 0, 1817], [1, 0, 0, 1818], [1, 0, 0, 1819], [1, 0, 0, 1820], [1, 0, 0, 1821], [1, 0, 0, 1822], [-1, 0, 0, 1823]],
            [[-1, 0, 0, 1911], [1, 0, 0, 1912], [1, 0, 0, 1913], [1, 0, 0, 1914], [1, 0, 0, 1915], [1, 0, 0, 1916], [1, 0, 0, 1917], [1, 0, 0, 1918], [1, 0, 0, 1919], [1, 0, 0, 1920], [1, 0, 0, 1921], [1, 0, 0, 1922], [-1, 0, 0, 1923]],
            [[-1, 0, 0, 2011], [1, 0, 0, 2012], [1, 0, 0, 2013], [1, 0, 0, 2014], [1, 0, 0, 2015], [1, 0, 0, 2016], [1, 0, 0, 2017], [1, 0, 0, 2018], [1, 0, 0, 2019], [1, 0, 0, 2020], [1, 0, 0, 2021], [1, 0, 0, 2022], [-1, 0, 0, 2023]],
            [[-1, 0, 0, 2111], [1, 0, 0, 2112], [1, 0, 0, 2113], [1, 0, 0, 2114], [1, 0, 0, 2115], [1, 0, 0, 2116], [1, 0, 0, 2117], [1, 0, 0, 2118], [1, 0, 0, 2119], [1, 0, 0, 2120], [1, 0, 0, 2121], [1, 0, 0, 2122], [-1, 0, 0, 2123]],
            [[-1, 0, 0, 2211], [-1, 0, 0, 2212], [1, 0, 0, 2213], [1, 0, 0, 2214], [1, 0, 0, 2215], [1, 0, 0, 2216], [1, 0, 0, 2217], [1, 0, 0, 2218], [1, 0, 0, 2219], [1, 0, 0, 2220], [1, 0, 0, 2221], [-1, 0, 0, 2222], [-1, 0, 0, 2223]],
            [[-1, 0, 0, 2311], [-1, 0, 0, 2312], [-1, 0, 0, 2313], [-1, 0, 0, 2314], [-1, 0, 0, 2315], [-1, 0, 0, 2316], [-1, 0, 0, 2317], [-1, 0, 0, 2318], [-1, 0, 0, 2319], [-1, 0, 0, 2320], [-1, 0, 0, 2321], [-1, 0, 0, 2322], [-1, 0, 0, 2323]],
        ]

        # Set list of tiles
        tiles = [
            1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, # 18 empty tiles
            2, 2, 2, # 3 horizontal arrows {4 options}
            3, 3, 3, # 3 diagonal arrows {4 options}
            4, 4, 4, # 3 horizontal both arrows {2 options}
            5, 5, 5, # 3 diagonal both arrows {2 options}
            6, 6, 6, # 3 3-way arrows {4 options}
            7, 7, 7, # 3 4-way horizontal arrows
            8, 8, 8, # 3 4-way diagonal arrows
            9, 9, # 2 horse
            10, 10, 10, 10, 10, # 5 jungle-go
            11, 11, 11, 11, # 4 desert-go
            12, 12, # 2 swamp-go
            13, # 1 waterfall-go
            14, 14, 14, 14, 14, 14, # 6 Ice
            15, 15, 15, # 3 pit
            16, 16, 16, 16, # 4 crocs
            17, # 1 cannibal
            18, 18, # 2 fortress
            19, #1 ressurect
            20, 20, 20, 20, 20, # 5 gold (1 coin)
            21, 21, 21, 21, 21, # 5 gold (2 coin)
            22, 22, 22, # 3 gold (3 coin)
            23, 23, # 2 gold (4 coin)
            24, # 1 gold (5 coin)
            25, # 1 treasure
            26, # 1 airplane
            27, # 1 carramba
            28, 28, # 2 balloons
            29, 29, # 2 cannons
            30, # 1 lighthouse
            31, # 1 Ben Gan
            32, # 1 missioner
            33, # 1 Friday
            34, 34, 34, # 3 Rum1
            35, 35, # 2 Rum2
            36, # 1 Rum3
            37, 37, 37, 37, # 4 barrel of rum
            38, 38, 38, 38, # 4 cave
            39, # 1 earthquake
            40, 40, 40, # 3 jungle
            41, 41 # 2 cannabis
        ]

        # Randomly fill the board
        for i in range(len(new_board)):
            for j in range(len(new_board[i])):
                if new_board[i][j][0] > 0:
                    new_board[i][j][1], tiles = random_choise(tiles)
                    # Randomly choose direction (4 options)
                    if new_board[i][j][1] == 1 or new_board[i][j][1] == 2 or new_board[i][j][1] == 3 or new_board[i][j][1] == 6 or new_board[i][j][1] == 29:
                        new_board[i][j][2] = randrange(1, 4)
                    # Randomly choose direction (2 options)
                    elif new_board[i][j][1] == 4 or new_board[i][j][1] == 5:
                        new_board[i][j][2] = randrange(1, 2)
        
        # Save the board
        board.board = json.dumps(new_board)     
        board.save()

        return HttpResponseRedirect(reverse('board', args=(),
            kwargs={'board_id': board.id}))


def random_choise(tiles):
    '''
    Function take list of tiles and chose one randomly, the remove it and return as a choise
    Return: one tile (number of tile) and list with that tile excluded
    '''

    # Get random number from list
    get = randrange(len(tiles))
    choise = tiles[get]

    # Find this number in list - remove it and stop searching
    for ii in range(len(tiles)):
        if choise == tiles[ii]:
            tiles.pop(ii)
            break

    # Return found number
    return choise, tiles


def index(request):
    '''
    Function takes all boards and return boards that player is playing in
    Return: render lobby page
    '''

    boards = Board.objects.filter(Q(user1=request.user.id) | Q(user2=request.user.id) | Q(user3=request.user.id) | Q(user4=request.user.id)).filter(play=True).order_by('pk')

    return render(request, "game/index.html", {
        'index': 1,
        'boards': boards
        })


def finished(request):
    '''
    Function takes all boards and return boards that player is finish
    Return: render lobby page
    '''

    boards = Board.objects.filter(Q(user1=request.user.id) | Q(user2=request.user.id) | Q(user3=request.user.id) | Q(user4=request.user.id)).filter(play=False).order_by('pk')

    return render(request, "game/index.html", {
        'boards': boards
        })


def login_view(request):
    '''
    Function make User log-in
    Return: render login page
    '''

    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "game/login.html", {
                "message": "Неверное имя пользователя и\или пароль."
            })
    else:
        return render(request, "game/login.html")


@login_required
def logout_view(request):
    '''
    Function make User log-out
    Return: render index page
    Login required
    '''
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    '''
    Function register new User
    Return: render register page
    '''

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "game/register.html", {
                "message": "Пароль должен совпадать."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "game/register.html", {
                "message": "Имя уже занято."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "game/register.html")


@login_required
def board(request, board_id):
    '''
    Function calculate information and render board
    Return: render board HTML page
    Login required
    '''

    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    rum_to_find = jsonDec.decode(get_board.rum) # Load rum
    coins = jsonDec.decode(get_board.coins) # Load coins
    pirats = jsonDec.decode(get_board.pirats) # Load pirats

    # Check who's turn is now
    turn = what_turn(board_id)

    # if cannabis - need previos user
    pr_user = getattr(get_board, ('user' + str(turn)))

    # Look for cannabis
    if int(get_board.cannabis) != 1:
        pl_turn = what_turn(board_id) + 1
        if pl_turn > 4:
            pl_turn = 1
    else:
        pl_turn = turn

    # Check if it is turn of logged user 
    current_user = 'user' + str(pl_turn)
    current_turn = getattr(get_board, current_user)
    if current_turn.id == request.user.id:
        user_turn = 1
    else:
        user_turn = 0

    # return only team what turn it is
    team_pirats = pirats[turn - 1]

    ships = load_ships_p(board_id)

    # Pirats: 1-team, 2-id of tile, 3-drunk, 4-pit, 5-layer, 6-name of tile
    for p in range(len(team_pirats)):
        if team_pirats[p][0] > 100:
            if board[int(str(team_pirats[p][0])[0:2]) - 11][int(str(team_pirats[p][0])[2:4]) - 11][0] == -1 and board[int(str(team_pirats[p][0])[0:2]) - 11][int(str(team_pirats[p][0])[2:4]) - 11][3] not in ships:
                tile_name = 'water'
            elif board[int(str(team_pirats[p][0])[0:2]) - 11][int(str(team_pirats[p][0])[2:4]) - 11][0] == -1 and board[int(str(team_pirats[p][0])[0:2]) - 11][int(str(team_pirats[p][0])[2:4]) - 11][3] in ships:
                tile_name = 'ship' + str(turn)
            elif board[int(str(team_pirats[p][0])[0:2]) - 11][int(str(team_pirats[p][0])[2:4]) - 11][2] == 0:
                tile_name = 'tile_' + str(board[int(str(team_pirats[p][0])[0:2]) - 11][int(str(team_pirats[p][0])[2:4]) - 11][1])
            else:
                tile_name = 'tile_' + str(board[int(str(team_pirats[p][0])[0:2]) - 11][int(str(team_pirats[p][0])[2:4]) - 11][1]) + '_' + str(board[int(str(team_pirats[p][0])[0:2]) - 11][int(str(team_pirats[p][0])[2:4]) - 11][2])
        else:
            tile_name = ''
        
        team_pirats[p] = [p + 1, team_pirats[p][0], team_pirats[p][1], team_pirats[p][2], team_pirats[p][3], tile_name]

    # Look for other persons
    bengan = get_board.bengan
    missioner = get_board.missioner
    friday = get_board.friday

    others = []

    if int(bengan[0]) == 2 and int(bengan[8]) == int(turn): # If BenGan is found and current team found him - print him
        if int(bengan[1:5]) > 100:
            if board[int(bengan[1:3]) - 11][int(bengan[3:5]) - 11][0] == -1 and board[int(bengan[1:3]) - 11][int(bengan[3:5]) - 11][3] not in ships:
                tile_name = 'water'
            elif board[int(bengan[1:3]) - 11][int(bengan[3:5]) - 11][0] == -1 and board[int(bengan[1:3]) - 11][int(bengan[3:5]) - 11][3] in ships:
                tile_name = 'ship' + str(turn)
            elif board[int(bengan[1:3]) - 11][int(bengan[3:5]) - 11][2] == 0:
                tile_name = 'tile_' + str(board[int(bengan[1:3]) - 11][int(bengan[3:5]) - 11][1])
            else:
                tile_name = 'tile_' + str(board[int(bengan[1:3]) - 11][int(bengan[3:5]) - 11][1]) + '_' + str(board[int(bengan[1:3]) - 11][int(bengan[3:5]) - 11][2])
        else:
            tile_name = ''
        others.append([4, int(bengan[1:5]), int(bengan[5]), int(bengan[6]), int(bengan[7]), 'BenGan', tile_name])

    if int(friday[0]) == 2 and int(friday[5]) == int(turn): # If friday is found and current team found him - print him
        if int(friday[1:5]) > 100:
            if board[int(friday[1:3]) - 11][int(friday[3:5]) - 11][0] == -1 and board[int(friday[1:3]) - 11][int(friday[3:5]) - 11][3] not in ships:
                tile_name = 'water'
            elif board[int(friday[1:3]) - 11][int(friday[3:5]) - 11][0] == -1 and board[int(friday[1:3]) - 11][int(friday[3:5]) - 11][3] in ships:
                tile_name = 'ship' + str(turn)
            elif board[int(friday[1:3]) - 11][int(friday[3:5]) - 11][2] == 0:
                tile_name = 'tile_' + str(board[int(friday[1:3]) - 11][int(friday[3:5]) - 11][1])
            else:
                tile_name = 'tile_' + str(board[int(friday[1:3]) - 11][int(friday[3:5]) - 11][1]) + '_' + str(board[int(friday[1:3]) - 11][int(friday[3:5]) - 11][2])
        else:
            tile_name = ''
        others.append([5, int(friday[1:5]), 0, 0, int(friday[6]), 'friday', tile_name])

    if int(missioner[0]) == 2 and int(missioner[8]) == int(turn) and int(missioner[9]) == 0: # If missioner is found and current team found him - print him
        if int(missioner[1:5]) > 100:
            if board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][0] == -1 and board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][3] not in ships:
                tile_name = 'water'
            elif board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][0] == -1 and board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][3] in ships:
                tile_name = 'ship' + str(turn)
            elif board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][2] == 0:
                tile_name = 'tile_' + str(board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][1])
            else:
                tile_name = 'tile_' + str(board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][1]) + '_' + str(board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][2])
        else:
            tile_name = ''
        others.append([6, int(missioner[1:5]), int(missioner[5]), int(missioner[6]), int(missioner[7]), 'missioner', tile_name])

    if int(missioner[0]) == 2 and int(missioner[8]) == int(turn) and int(missioner[9]) == 1: # If missioner is found and current team found him - print him
        if int(missioner[1:5]) > 100:
            if board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][0] == -1 and board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][3] not in ships:
                tile_name = 'water'
            elif board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][0] == -1 and board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][3] in ships:
                tile_name = 'ship' + str(turn)
            elif board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][2] == 0:
                tile_name = 'tile_' + str(board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][1])
            else:
                tile_name = 'tile_' + str(board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][1]) + '_' + str(board[int(missioner[1:3]) - 11][int(missioner[3:5]) - 11][2])
        else:
            tile_name = ''
        others.append([6, int(missioner[1:5]), int(missioner[5]), int(missioner[6]), int(missioner[7]), 'missioner-pirat', tile_name])

    # Rum
    rum = []

    # Calculate number of rum
    for i in range(len(rum_to_find)):
        if int(turn) == int(rum_to_find[i]):
            rum.append(int(turn))

    with_coin = int(get_board.with_coin)

    team_coins = []

    # Calculate coins
    count = 6
    for ii in range(len(coins)):
        if int(turn) == int(coins[ii][0]):
            team_coins.append(count)
            count += 2

    tr_pos = count + 16

    # Calculate treasure
    if int(get_board.treasure) == int(turn):
        treasure = 1
    else:
        treasure = 0
    
    all_points = calculate_points(board_id)

    # Load persons for stats: 1-in game or not, 2-team, 3-missioner-pirat
    persons = [[bengan[0], bengan[8]], [friday[0], friday[5]], [missioner[0], missioner[8], missioner[9]]]

    # Make list of last turns
    last_turns = lastTurns(board_id)

    # Calculate persentage of opened tiles
    opened = 0

    for b in range(len(board)):
        for v in range(len(board[b])):
            if board[b][v][0] == 2:
                opened += 1

    opened = (int((opened / 117) * 1000)) / 10

    return render(request, "game/board.html", {
         'board': board,
         'get_board': get_board,
         'turn': turn,
         'current_turn': current_turn,
         'user_turn': user_turn,
         'pirats': team_pirats,
         'others': others,
         'persons': persons,
         'rum': rum,
         'with_coin': with_coin,
         'coins': team_coins,
         'treasure': treasure,
         'tr_position': tr_pos,
         'pr_user': pr_user,
         'all_points': all_points,
         'last_turns': last_turns,
         'opened': opened
         })


def lastTurns(board_id):
    '''
    Take last turns from each player and pack them into list
    Return: list of last turns
    '''

    # Get board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Get all last turns (by 5 on player)
    try:
        last_turns = Turns.objects.filter(board=get_board).order_by('-pk')[:20]
    except:
        return []

    # Make empty list
    turns = [[], [], [], []]

    current = 0
    count = 0

    # take current team
    if len(last_turns) > 0:
        current = last_turns[0].team

    # calculate only last turns of each team
    for turn in last_turns:
        if current == turn.team and count == 1: # if count goes to second try - stop it
            break
        result = []
        result.append(turn.team)
        if turn.from_id == 'water':
            result.append('water')
        elif turn.from_id == 'ship':
            result.append('ship' + str(turn.team))
        elif board[int(str(turn.from_id)[0:2]) - 11][int(str(turn.from_id)[2:4]) - 11][2] == 0:
            result.append('tile_' + str(board[int(str(turn.from_id)[0:2]) - 11][int(str(turn.from_id)[2:4]) - 11][1]))
        else:
            result.append('tile_' + str(board[int(str(turn.from_id)[0:2]) - 11][int(str(turn.from_id)[2:4]) - 11][1]) + '_' + str(board[int(str(turn.from_id)[0:2]) - 11][int(str(turn.from_id)[2:4]) - 11][2]))
        if turn.target_id == 'water':
            result.append('water')
        elif turn.target_id == 'ship':
            result.append('ship' + str(turn.team))
        elif turn.target_id == 'closed_tile':
            result.append('tile_closed')
        elif board[int(str(turn.target_id)[0:2]) - 11][int(str(turn.target_id)[2:4]) - 11][2] == 0:
            result.append('tile_' + str(board[int(str(turn.target_id)[0:2]) - 11][int(str(turn.target_id)[2:4]) - 11][1]))
        else:
            result.append('tile_' + str(board[int(str(turn.target_id)[0:2]) - 11][int(str(turn.target_id)[2:4]) - 11][1]) + '_' + str(board[int(str(turn.target_id)[0:2]) - 11][int(str(turn.target_id)[2:4]) - 11][2]))
        if turn.pirat[1] == '6' and get_board.missioner[9] == '0':
            result.append('7')
        else:
            result.append(turn.pirat[1])
        result.append(turn.with_coin)
        result.append(turn.with_treasure)
        look = getattr(get_board, ('user' + str(turn.pirat[0])))
        result.append(look.username)

        turns[int(turn.team) - 1].append(result)

        if current != turn.team:
            count = 1

    # Sort list
    new_turns = []

    for i in range(4):
        new_turns.append(turns[(int(current) - i - 1) % 4])

    return new_turns


def win(board_id):
    '''
    Function calculate number of coins left an treasure to find winner or tie
    Return: boolean
    '''

    # Get board
    get_board = Board.objects.get(pk=board_id)

    # Calculate win-points of each player
    user1_win, user2_win, user3_win, user4_win, total_coins = calculate_points(board_id)

    if user1_win > 20:
        get_board.winner = 'user1'
        get_board.save()
        return True
    elif user2_win > 20:
        get_board.winner = 'user2'
        get_board.save()
        return True
    elif user3_win > 20:
        get_board.winner = 'user3'
        get_board.save()
        return True
    elif user4_win > 20:
        get_board.winner = 'user4'
        get_board.save()
        return True
    elif total_coins == 40:
        look_for_winner = {
            'user1': user1_win,
            'user2': user2_win,
            'user3': user3_win,
            'user4': user4_win,
        }
        s_winners = dict(sorted(look_for_winner.items(), key=lambda item: item[1], reverse=True))
        temp = 0
        count = 0
        for item in s_winners.values():
            if count == 0:
                temp = item
                count = 1
            else:
                if temp == item:
                    get_board.winner = 'Tie'
                    get_board.save()
                    return True

    return False


def calculate_points(board_id):
    '''
    Function calculate 
    Return: list of points for each player
    '''
    
    # Get board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    coins = jsonDec.decode(get_board.coins) # Load coins

    # Calculate win-points of each player
    user1_win = 0
    user2_win = 0
    user3_win = 0
    user4_win = 0

    # look for total coins 
    total_coins = 0

    if int(get_board.treasure) == 1:
        user1_win += 3
        total_coins += 3
    elif int(get_board.treasure) == 2:
        user2_win += 3
        total_coins += 3
    elif int(get_board.treasure) == 3:
        user3_win += 3
        total_coins += 3
    elif int(get_board.treasure) == 4:
        user4_win += 3
        total_coins += 3
    elif int(get_board.treasure) == 5:
        total_coins += 3

    for coin in coins:
        if coin[0] == 1:
            user1_win += 1
            total_coins += 1
        elif coin[0] == 2:
            user2_win += 1
            total_coins += 1
        elif coin[0] == 3:
            user3_win += 1
            total_coins += 1
        elif coin[0] == 4:
            user4_win += 1
            total_coins += 1
        elif coin[0] == 5:
            total_coins += 1

    all_users = [user1_win, user2_win, user3_win, user4_win, total_coins]
    return all_users


def events(request, board_id):
    '''
    Function return number of current event
    Return: number of event in JSON
    '''

    # Get board
    get_board = Board.objects.get(pk=board_id)

    return JsonResponse({
        "event": int(get_board.event)
    })


def return_moves_or_not(request, board_id):
    '''
    Function looks if there is pirat that has been chosen for move or not
    Return: availability to move in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    if get_board.chosen == "":
        moves = 0
    else:
        moves = 1

    # return number of event
    return JsonResponse({
        "moves": moves
    })


def find_to_go_pirats(request, id, board_id):
    '''
    Function looks for pirats (and persons) that is on to-go tiles
    Return: pirats (and persons), coins, treasure in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    coins_decode = jsonDec.decode(get_board.coins) # Load coins
    bengan = get_board.bengan # Load bengan
    friday = get_board.friday # Load friday
    missioner = get_board.missioner # Load missioner

    # Make persons list: 1-team 2-number_of_pirat 3-layer
    # Make coins list: 1-layer 2-number of coins
    persons = []
    coins = []

    # Find tile
    tile_id = board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3]

    # Find all pirats and layers
    for i in range(len(pirats)):
        for j in range(len(pirats[i])):
            if pirats[i][j][0] == tile_id:
                persons.append([i + 1, 1, pirats[i][j][3]])

    if int(bengan[0]) == 2 and int(bengan[1:5]) == tile_id: # Bengan
        persons.append([0, 4, int(bengan[7])])
    if int(friday[0]) == 2 and int(friday[1:5]) == tile_id: # Friday
        persons.append([0, 5, int(friday[6])])
    if int(missioner[0]) == 2 and int(missioner[1:5]) == tile_id and int(missioner[9]) == 0: # Missioner
        persons.append([0, 6, int(missioner[7])])
    if int(missioner[0]) == 2 and int(missioner[1:5]) == tile_id and int(missioner[9]) == 1: # Missioner-pirat
        persons.append([0, 7, int(missioner[7])])

    # Make new list for calculation
    to_count_coins = []

    for b in coins_decode:
        to_count_coins.append(int(str(b[0]) + str(b[1])))

    coins_set = set(to_count_coins)
    coins_set.remove(0)

    # Sort list and finds all coins on layers
    for n in coins_set:
        if int(str(n)[0:4]) == int(id):
            coins.append([int(str(n)[4]), to_count_coins.count(n)])

    # Find treasure
    treasure = 200
    if int(get_board.treasure[0:4]) == id:
        treasure = int(get_board.treasure[4])

    return JsonResponse({
        "persons": persons,
        "coins": coins,
        "treasure": treasure
    })


def pirats_that_can_move(request, board_id):
    '''
    Function looks for pirats (and persons) that can move
    Return: pirats (and persons) in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan # Load bengan
    friday = get_board.friday # Load friday
    missioner = get_board.missioner # Load missioner

    live = []

    if get_board.mover != '':

        # if there is mover - only he can move
        live.append('pirat' + str(get_board.mover))

    else:

        # Load pirats that can move into list (except pit)
        for i in range(len(pirats[int(what_turn(board_id)) - 1])):
            if pirats[int(what_turn(board_id)) - 1][i][0] != 0 and pirats[int(what_turn(board_id)) - 1][i][1] == 0 and get_board.first_cave != ('pirat' + str(what_turn(board_id)) + str(i + 1)):
                live.append('pirat' + str(what_turn(board_id)) + str(i + 1))

        # Look for other persons
        if int(bengan[0]) == 2 and int(bengan[5]) == 0 and int(bengan[8]) == int(what_turn(board_id)) and get_board.first_cave != ('pirat' + str(what_turn(board_id)) + '4'):
            live.append('pirat' + str(what_turn(board_id)) + '4')

        if int(friday[0]) == 2 and int(friday[5]) == int(what_turn(board_id)) and get_board.first_cave != ('pirat' + str(what_turn(board_id)) + '5'):
            live.append('pirat' + str(what_turn(board_id)) + '5')

        if int(missioner[0]) == 2 and int(missioner[5]) == 0 and int(missioner[8]) == int(what_turn(board_id)) and get_board.first_cave != ('pirat' + str(what_turn(board_id)) + '6'):
            live.append('pirat' + str(what_turn(board_id)) + '6')

    return JsonResponse({
        "live": live
    })


def is_mover(request, board_id):
    '''
    Function looks for mover
    Return: mover in JSON (boolean)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    if get_board.mover != '':
        there_is_mover = True
    else:
        there_is_mover = False

    # return mover or not
    return JsonResponse({
        "mover": there_is_mover
    })


def make_mover(request, pirat, board_id):
    '''
    Function makes current pirat (or person) mover
    Return: nothing (status 200)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    # Make pirat - chosen pirat
    get_board.chosen = pirat[5:7]
    get_board.save()

    return HttpResponse(status=200)


def with_coin_change(request, board_id):
    '''
    Function change movement with coin or not
    Return: nothing (status 200)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    if get_board.mover == '':
        if int(get_board.with_coin) == 0:
            get_board.with_coin = 1
            get_board.with_treasure = 0
        else:
            get_board.with_coin = 0

        get_board.save()

    return HttpResponse(status=200)


def with_coin_return(request, board_id):
    '''
    Function looks if movement is with coin or not
    Return: with coin in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    # return with coin or not
    return JsonResponse({
        "with_coin": get_board.with_coin
    })


def with_treasure_return(request, board_id):
    '''
    Function looks if movement is with treasure or not
    Return: with treasure in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    # return with coin or not
    return JsonResponse({
        "with_treasure": get_board.with_treasure
    })


def with_treasure_change(request, board_id):
    '''
    Function change movement with treasure or not
    Return: nothing (status 200)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    if get_board.mover == '':
        if int(get_board.with_treasure) == 0:
            get_board.with_treasure = 1
            get_board.with_coin = 0
        else:
            get_board.with_treasure = 0

        get_board.save()

    return HttpResponse(status=200)


def have_coin(request, target, board_id):
    '''
    Function looks if mover have coin or treasure
    Return: coin and treasure in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    coins = jsonDec.decode(get_board.coins) # Load coins
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    missioner = get_board.missioner
    friday = get_board.friday

    coin = 0
    treasure = 0

    # Look for coins and treasure (including layer)
    for i in range(len(coins)):
        if int(get_board.chosen[1]) <= 3: # Pirats
            if int(target) == coins[i][0] and coins[i][1] == pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][3]:
                coin = 1
            if int(target) == int(get_board.treasure[0:4]) and int(get_board.treasure[4]) == pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][3]:
                treasure = 1

        # Look for coins and treasure (including layer) for BenGan
        if int(bengan[0]) == 2 and int(bengan[8]) == int(what_turn(board_id)):
            if int(target) == coins[i][0] and coins[i][1] == int(bengan[7]):
                coin = 1
            if int(target) == int(get_board.treasure[0:4]) and int(get_board.treasure[4]) == int(bengan[7]):
                treasure = 1

        # Look for coins and treasure (including layer) for missioner
        if int(missioner[0]) == 2 and int(missioner[8]) == int(what_turn(board_id)) and int(missioner[9]) == 1:
            if int(target) == coins[i][0] and coins[i][1] == int(missioner[7]):
                coin = 1
            if int(target) == int(get_board.treasure[0:4]) and int(get_board.treasure[4]) == int(missioner[7]):
                treasure = 1

        # Look for coins and treasure (not including layer) for friday
        if int(friday[0]) == 2 and int(friday[5]) == int(what_turn(board_id)):
            if int(target) == coins[i][0] and coins[i][1] == int(friday[6]):
                coin = 1
            if int(target) == int(get_board.treasure[0:4]) and int(get_board.treasure[4]) == int(friday[6]):
                treasure = 1

    # If mover is missioner - he can't take coins and treasure
    if int(missioner[0]) == 2 and int(missioner[8]) == int(what_turn(board_id)) and int(missioner[9]) == 0 and int(get_board.chosen[1]) == 6:
        coin = 0
        treasure = 0

    # return with coin or not
    return JsonResponse({
        "coin": coin,
        "treasure": treasure
    })


def remove_mover(request, board_id):
    '''
    Function make mover empty
    Return: nothing (status 200)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    if get_board.mover == '':
        get_board.with_coin = 0
        get_board.with_treasure = 0
    get_board.chosen = ""
    get_board.save()

    return HttpResponse(status=200)


def lighthouse_event(request, board_id):
    '''
    Function looks for all closed tiles and make User open 4 tiles
    Return: closed tiles in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    closed_tiles = []

    if int(get_board.event) >= 1 and int(get_board.event) <= 4:

        # Find all closed tiles
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j][0] == 1: # if tile is closed
                    closed_tiles.append(board[i][j][3])

    else:
        print('Something go wrong (Lighthouse event)')

    # return possible moves
    return JsonResponse({
        "closed_tiles": closed_tiles
    })


def open_tile_light(request, id, board_id):
    '''
    Function open chosen tile (add coins, treasure, rum, persons if found)
    Return: nothing (status 200)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Open tile and add items on it (if needed)
    board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][0] = 2 # open tile
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (20, 21, 22, 23, 24): # add gold if opened tile is coins
        coins = add_coins(id, board, board_id)
        get_board.coins = json.dumps(coins)
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 25: # add treasure is opened tile is treasure
        get_board.treasure = str(id) + '0'
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (34, 35, 36): # add rum to open tile
        rum = add_rum_to_tile(id, board, board_id)
        get_board.rum = json.dumps(rum)
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 31: # BenGan
        bengan = bengan[0] + str(id) + bengan[5:]
        get_board.bengan = bengan
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 32: # Missioner
        missioner = missioner[0] + str(id) + missioner[5:]
        get_board.missioner = missioner
    elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 33: # Friday
        friday = friday[0] + str(id) + friday[5]
        get_board.friday = friday

    get_board.event = int(get_board.event) + 1
    get_board.board = json.dumps(board)
    get_board.save()

    return HttpResponse(status=200)


def end_lighthouse(request, board_id):
    '''
    Function ends lighthouse event and make it inactive
    Return: nothing (status 200)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    get_board.event = 0
    get_board.lighthouse = False
    get_board.save()

    change_turn(0, 0, board_id)

    return HttpResponse(status=200)


def earthquake_event(request, board_id):
    '''
    Function make player that found earthquake change 2 tiles
    Return: empty tiles in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    rum = jsonDec.decode(get_board.rum) # Load rum
    old_coins = jsonDec.decode(get_board.coins) # Load coins
    old_pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    missioner = get_board.missioner
    friday = get_board.friday

    coins = []
    for i in old_coins:
        coins.append(i[0])

    pirats = []
    for j in range(len(old_pirats)):
        for k in range(len(old_pirats[j])):
            pirats.append(old_pirats[j][k][0])

    empty_tiles = []

    if int(get_board.event) == 6 or int(get_board.event) == 7:

        # Find all empty tiles
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j][0] == 1 or board[i][j][0] == 2: # if tile is not water
                    if get_board.earthquake_tile != '' and int(board[i][j][3]) == int(get_board.earthquake_tile):
                        pass
                    elif board[i][j][3] in rum:
                        pass
                    elif board[i][j][3] in coins:
                        pass
                    elif board[i][j][3] in pirats:
                        pass
                    elif board[i][j][3] == int(bengan[1:5]) or board[i][j][3] == int(missioner[1:5]) or board[i][j][3] == int(friday[1:5]):
                        pass
                    else:
                        empty_tiles.append(board[i][j][3])

    else:
        print('Something go wrong !!! (Earthquake event)')

    # return possible moves
    return JsonResponse({
        "empty_tiles": empty_tiles
    })


def change_tile_earth(request, id, board_id):
    '''
    Function get two tiles and swap them
    Return: nothing (status 200)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Choose first tile
    if get_board.earthquake_tile == '':
        get_board.earthquake_tile = id
    else:
        # Choose second tile and swap them (not swap ID of tile)
        # Calculate 'old' board
        old = board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][0:3]
        old.append(board[int(get_board.earthquake_tile[0:2]) - 11][int(get_board.earthquake_tile[2:4]) - 11][3])
        # Calculate 'new' board
        new = board[int(get_board.earthquake_tile[0:2]) - 11][int(get_board.earthquake_tile[2:4]) - 11][0:3]
        new.append(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3])

        board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11] = new
        board[int(get_board.earthquake_tile[0:2]) - 11][int(get_board.earthquake_tile[2:4]) - 11] = old

    get_board.event = int(get_board.event) + 1
    get_board.board = json.dumps(board)
    get_board.save()

    return HttpResponse(status=200)


def end_earthquake(request, board_id): # Make earthquake inactive
    '''
    Function ends earthquake event and make it inactive
    Return: nothing (status 200)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    get_board.event = 0
    get_board.earthquake = False
    get_board.earthquake_tile = ''
    get_board.save()

    change_turn(0, 0, board_id)

    return HttpResponse(status=200)


def load_treasure(request, board_id):
    '''
    Function looks for treasure and calculate where it is
    Return: location of treasure in JSON
    '''

    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    treasure = int(get_board.treasure[0:4])
    if int(get_board.treasure) > 10:
        tile = board[(int(str(get_board.treasure)[0:2]) - 11)][(int(str(get_board.treasure)[2:4]) - 11)][1]
        layer = int(get_board.treasure[4])
    else:
        tile = 0
        layer = 0

    # return loaded list
    return JsonResponse({
        "treasure": treasure,
        "tile": tile,
        "layer": layer
    })


def add_coins(target, board, board_id): # Add coins to tile
    '''
    Function calculate how many coins to add to tile
    Return: list of coins
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    coins = jsonDec.decode(get_board.coins) # Load coins

    # Check how many coins to drop
    coins_to_drop = int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) - 19

    # Add coins to list
    for k in range(len(coins)):
        if coins[k][0] == 0 and coins_to_drop != 0:
            coins[k][0] = int(target)
            coins_to_drop -= 1

    return coins


def load_coins(request, board_id):
    '''
    Function looks for coins and calculate where they are
    Return: location of coins in JSON
    '''

    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    coins_list = jsonDec.decode(get_board.coins) # Load coins

    # Make new list for calculation
    to_count_coins = []

    for i in coins_list:
        to_count_coins.append(int(str(i[0]) + str(i[1])))

    coins_set = set(to_count_coins)
    coins = []

    # Sort list
    for j in coins_set:
        if j > 100:
            coins.append([int(str(j)[0:4]), to_count_coins.count(j), board[(int(str(j)[0:2]) - 11)][(int(str(j)[2:4]) - 11)][1], int(str(j)[4])])

    # return loaded list
    return JsonResponse({
        "coins": coins
    })


def add_rum(target, board, board_id):
    '''
    Function calculate how many rum to add to tile
    Return: list of rum
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    rum = jsonDec.decode(get_board.rum) # Load rum

    # Take team number
    turn = what_turn(board_id)

    # Check how many rum to add
    rum_to_add = int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) - 33

    # Add rum to team
    for k in range(len(rum)):
        if rum[k] == 0 and rum_to_add != 0:
            rum[k] = int(turn)
            rum_to_add -= 1

    return rum


def load_rum(request, board_id):
    '''
    Function looks for rum and calculate where they are
    Return: location of rum in JSON
    '''

    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    rum_list = jsonDec.decode(get_board.rum) # Load rum

    # Make new set for calculation
    new_set = set(rum_list)

    # make empty list to fill
    rum = []

    # load list with id number and number of coins on that ID
    for i in new_set:
        if int(i) > 5:
            rum.append([i, rum_list.count(i)])

    # return loaded list
    return JsonResponse({
        "rum": rum
    })


def add_rum_to_tile(target, board, board_id):
    '''
    Function add rum to tile, that is opened with lighthouse
    Return: list of rum
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    rum = jsonDec.decode(get_board.rum) # Load rum

    # Check how many rum to add
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j][3] == int(target):
                rum_to_add = int(board[i][j][1]) - 33

    # Add rum to tile
    for k in range(len(rum)):
        if rum[k] == 0 and rum_to_add != 0:
            rum[k] = int(target)
            rum_to_add -= 1

    return rum


def take_rum_from_ground(target, board_id):
    '''
    Function looks if there is rum on tile - and give it to the player that found it
    Return: list of rum
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    rum = jsonDec.decode(get_board.rum) # Load rum

    # Take team number
    turn = what_turn(board_id)

    # Add rum to team
    for i in range(len(rum)):
        if rum[i] == int(target):
            rum[i] = int(turn)

    return rum


def load_ships(request, board_id):
    '''
    Function load ships
    Return: list of ships in JSON
    '''

    # Load ships
    ships = load_ships_p(board_id)

    # return loaded list
    return JsonResponse({
        "ships": ships
    })


def load_pirats(request, board_id):
    '''
    Function load pirats and persons
    Return: list of pirats (and persons) in JSON
    '''

    # Get board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats

    if int(get_board.bengan[0]) == 2:
        bengan = int(get_board.bengan[1:5])
    else:
        bengan = 0

    if int(get_board.friday[0]) == 2:
        friday = int(get_board.friday[1:5])
    else:
        friday = 0

    if int(get_board.missioner[0]) == 2 and int(get_board.missioner[9]) == 0:
        missioner = int(get_board.missioner[1:5])
    else:
        missioner = 0

    if int(get_board.missioner[0]) == 2 and int(get_board.missioner[9]) == 1:
        missioner_pirat = int(get_board.missioner[1:5])
    else:
        missioner_pirat = 0

    # return loaded list
    return JsonResponse({
        "pirats": pirats,
        "bengan": bengan,
        "friday": friday,
        "missioner": missioner,
        "missioner_pirat": missioner_pirat
    })


def load_pirats_turn(request, board_id):
    '''
    Function looks who is now mover and what is his name
    Return: id of pirat (or person) and name in JSON
    '''

    # Get board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Find pirat or other person
    if int(get_board.chosen[1]) <= 3: # Pirats
        turn_pirat = pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][0]
    elif int(get_board.chosen[1]) == 4: # BenGan
        turn_pirat = bengan[1:5]
    elif int(get_board.chosen[1]) == 5: # Friday
        turn_pirat = friday[1:5]
    elif int(get_board.chosen[1]) == 6: # Missioner
        turn_pirat = missioner[1:5]

    # Find pirats name
    name = 'pirat' + get_board.chosen

    return JsonResponse({
        "pirat": turn_pirat,
        "name": name
    })


def can_ressurect(request, board_id):
    '''
    Function looks if selected pirat can ressurect teammate
    Return: can-ressurect in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    pirats = jsonDec.decode(get_board.pirats) # Load pirats

    pirat = 0
    # Find pirat
    try:
        if int(get_board.chosen[1]) <= 3: # Pirats
            pirat = pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][0]
    except:
        pirat = 0

    # Find ressurect tile
    res = 0
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j][1] == 19:
                res = board[i][j][3]

    can = 0
    # Look for pirats to be ressurected
    for i in range(len(pirats[int(what_turn(board_id)) - 1])):
        if pirats[int(what_turn(board_id)) - 1][i][0] == 0:
            can = 1

    if int(pirat) == int(res) and can == 1:
        ressurect = 1
    else:
        ressurect = 0

    return JsonResponse({
        "ressurect": ressurect
    })


def can_drink_rum(request, id, board_id):
    '''
    Function looks if selected pirat can drink rum
    Return: can-drink in JSON
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    rum = jsonDec.decode(get_board.rum) # Load rum
    bengan = get_board.bengan
    missioner = get_board.missioner

    drink = 0

    if int(get_board.chosen[1]) <= 3: # Pirats
        if int(pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][0]) == board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3] and int(get_board.chosen[0]) in rum:
            if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 15 and int(pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][2]) == 1:
                drink = 1
            elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (10, 11, 12, 13):
                if int(pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][3]) != (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8):
                    drink = 1
    elif int(get_board.chosen[1]) == 4: # BenGan
        if int(bengan[1:5]) == board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3] and int(get_board.chosen[0]) in rum:
            if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 15 and int(bengan[6]) == 1:
                drink = 1
            elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (10, 11, 12, 13):
                if int(bengan[7]) != (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8):
                    drink = 1
    elif int(get_board.chosen[1]) == 6: # Missioner pirat
        if int(missioner[1:5]) == board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3] and int(missioner[9]) == 1 and int(get_board.chosen[0]) in rum:
            if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 15 and int(missioner[6]) == 1:
                drink = 1
            elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (10, 11, 12, 13):
                if int(missioner[7]) != (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8):
                    drink = 1

    return JsonResponse({
        "drink": drink
    })


def drink(request, id, board_id):
    '''
    Function make pirat drink rum and if pirat is on to-go tile - go up with coin and kill enemy on top level
    Return: nothing (status 200)
    '''

    if request.method == 'PUT':

        # Load board
        get_board = Board.objects.get(pk=board_id)
        jsonDec = json.decoder.JSONDecoder()
        board = jsonDec.decode(get_board.board) # Load board
        pirats = jsonDec.decode(get_board.pirats) # Load pirats
        rum = jsonDec.decode(get_board.rum) # Load rum
        coins = jsonDec.decode(get_board.coins) # Load coins
        bengan = get_board.bengan
        missioner = get_board.missioner

        if int(get_board.chosen[1]) <= 3: # Pirats
            if int(pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][0]) == board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3] and int(get_board.chosen[0]) in rum:
                layer = pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][3]
                if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 15:
                    pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][2] = 0
                elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (10, 11, 12, 13):
                    if int(pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][3]) != (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8):
                        pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][3] = (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8)
                        if int(get_board.with_coin) == 1:
                            for t, r in enumerate(coins):
                                if int(r[0]) == id and int(r[1]) == int(layer):
                                    coins[t][1] = (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8)
                            get_board.coins = json.dumps(coins)
                        elif int(get_board.with_treasure) == 1:
                            get_board.treasure = get_board.treasure[0:4] + str(int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8)
        elif int(get_board.chosen[1]) == 4: # BenGan
            if int(bengan[1:5]) == board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3] and int(get_board.chosen[0]) in rum:
                if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 15:
                    get_board.bengan = bengan[0:6] + '0' + bengan[7:]
                elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (10, 11, 12, 13):
                    if int(bengan[7]) != (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8):
                        get_board.bengan = bengan[0:7] + str(int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8) + bengan[8:]
                        if int(get_board.with_coin) == 1:
                            for t, r in enumerate(coins):
                                if int(r[0]) == id and int(r[1]) == int(layer):
                                    coins[t][1] = (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8)
                            get_board.coins = json.dumps(coins)
                        elif int(get_board.with_treasure) == 1:
                            get_board.treasure = get_board.treasure[0:4] + str(int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8)
        elif int(get_board.chosen[1]) == 6: # Missioner pirat
            if int(missioner[1:5]) == board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][3] and int(missioner[9]) == 1 and int(get_board.chosen[0]) in rum:
                if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 15:
                    get_board.missioner = missioner[0:6] + '0' + missioner[7:]
                elif board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (10, 11, 12, 13):
                    if int(missioner[7]) != (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8):
                        get_board.missioner = missioner[0:7] + str(int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8) + missioner[8:]
                        if int(get_board.with_coin) == 1:
                            for t, r in enumerate(coins):
                                if int(r[0]) == id and int(r[1]) == int(layer):
                                    coins[t][1] = (int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8)
                            get_board.coins = json.dumps(coins)
                        elif int(get_board.with_treasure) == 1:
                            get_board.treasure = get_board.treasure[0:4] + str(int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 8)

        # remove 1 rum from team
        for i in range(len(rum)):
            if rum[i] == int(get_board.chosen[0]):
                rum[i] = 0
                break

        # Save results
        get_board.rum = json.dumps(rum)
        get_board.pirats = json.dumps(pirats)
        get_board.mover = get_board.chosen
        get_board.save()
        get_board = kill_enemy(id, board_id) # Look is there is someone on the top of layers
        get_board.save()

        return HttpResponse(status=200)

def ressurect(request, board_id):
    '''
    Function ressurect teammate
    Return: nothing (status 200)
    '''

    if request.method == 'PUT':

        # Load board
        get_board = Board.objects.get(pk=board_id)
        jsonDec = json.decoder.JSONDecoder()
        board = jsonDec.decode(get_board.board) # Load board
        pirats = jsonDec.decode(get_board.pirats) # Load pirats

        # Find ressurect tile
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j][1] == 19:
                    res = board[i][j][3]

        # Find pirat and ressurect him
        for i in range(len(pirats[int(what_turn(board_id)) - 1])):
            if pirats[int(what_turn(board_id)) - 1][i][0] == 0:
                pirats[int(what_turn(board_id)) - 1][i][0] = res
                get_board.pirats = json.dumps(pirats)
                get_board.save()
                break

        change_turn(0, 0, board_id)

        return HttpResponse(status=200)


def possible_moves(request, id, board_id, python, chosen):
    '''
    Function take possible moves for tile and removes ones that is not available
    Return: list of possible moves in JSON
    '''

    print(chosen)

    # Look for friday
    try:
        if chosen[6] == '5':
            chosen = 5
    except:
        pass

    # Create variables to calculate to-go tiles
    to_go = 0
    to_go_layers = []

    if len(str(id)) != 4:
        to_go = int(str(id)[4])
        id = int(str(id)[0:4])

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    friday = get_board.friday
    missioner = get_board.missioner

    # Add numbers to calculate possible to-go moves
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] in (10, 11, 12, 13):
        layers = int(board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1]) - 9
        for layer in range(layers):
            to_go_layers.append(layer + 1)

    # If mover is in pit - no moves then
    if board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 15 and is_mover_in_pit(id, board_id):
        moves = []

    # Look if there is move from ice
    elif get_board.ice != '' and board[int(str(id)[0:2]) - 11][int(str(id)[2:4]) - 11][1] == 14:

        move_id = int(get_board.ice[:2])
        tile_id = int(get_board.ice[2:])

        if move_id == 26: # airplane
            new_moves = Every(tile_id, board_id, move_id)
        elif move_id == 99: # horse
            move_id = 9
            new_moves = Every(tile_id, board_id, move_id)
        else:
            print('Something goes wrong (Possible moves)')
            new_moves = Every(id, board_id)

        moves = []

        for h in new_moves:
            moves.append(h)

        # Check for available moves with coin
        for i in new_moves:
            stop = 0
            if int(get_board.with_coin) == 1 or int(get_board.with_treasure) == 1:
                if not check_for_moves_with_coin(i, to_go, board_id):
                    moves.remove(i)
                    stop = 1
            else:
                if not check_for_moves(i, to_go, board_id):
                    moves.remove(i)
                    stop = 1

            if int(missioner[1:5]) == int(id) and int(missioner[9]) == 0 and stop == 0: # If missioner is on tile - can't attack other pirats
                if not check_for_other_pirats(i, board_id):
                    moves.remove(i)

    elif int(get_board.cave) == 1: # Look for cave

        # Get possible moves
        new_moves = Cave(id, board_id)

        moves = []

        for h in new_moves:
            moves.append(h)

        # Check for available moves with coin
        for i in new_moves:
            if not check_for_moves_with_coin(i, to_go, board_id):
                moves.remove(i)
            elif int(friday[0]) == 2 and int(friday[1:5]) == i and int(friday[5]) != int(what_turn(board_id)):
                moves.remove(i)


    elif id in get_all_to_go_tiles(board_id) and to_go in to_go_layers: # if target is to-go tile and not the last layer

        # Possible move = tile id
        if int(get_board.with_coin) == 1 or int(get_board.with_treasure) == 1:
            if check_for_moves_with_coin(id, to_go, board_id):
                moves = [id]
        else:
            if check_for_moves(id, to_go, board_id):
                moves = [id]

    else: # Any other move

        # Get possible moves
        new_moves = Every(id, board_id)

        moves = []

        for h in new_moves:
            moves.append(h)

        # Check for available moves with coin
        for i in new_moves:
            stop = 0
            if int(get_board.with_coin) == 1 or int(get_board.with_treasure) == 1:
                if not check_for_moves_with_coin(i, to_go, board_id):
                    moves.remove(i)
                    stop = 1
            else:
                if not check_for_moves(i, to_go, board_id):
                    moves.remove(i)
                    stop = 1

            if int(missioner[1:5]) == int(id) and int(missioner[9]) == 0 and stop == 0: # If missioner is on tile - can't attack other pirats
                if not check_for_other_pirats(i, board_id):
                    moves.remove(i)
                    stop = 1

            try:
                if chosen == 5 and stop == 0:
                    if enemy_on_tile(i, board_id):
                        moves.remove(i)
            except:
                pass

    if python == 1:
        moves.append(id)
        return moves
    else:
        # return possible moves
        return JsonResponse({
            "moves": moves,
            "from": id
        })


def is_mover_in_pit(id, board_id):
    '''
    Function looks if pirat (or person) is fallen into pit
    Return: boolean
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    missioner = get_board.missioner

    for i in range(len(pirats)):
        for j in range(len(pirats[i])):
            if pirats[i][j][0] == id and pirats[i][j][2] == 1:
                return True
    if int(bengan[1:5]) == id and int(bengan[6]) == 1: # BenGan
        return True
    if int(missioner[1:5]) == id and int(missioner[6]) == 1: # Missioner
        return True

    return False

def get_all_to_go_tiles(board_id):
    '''
    Function looks for all to-go tiles 
    Return: list of to-go tiles
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    id_tiles = []

    # Look for to-go tiles
    for i in range(len(board)):
        for j in range(len(board[i])):
            if int(board[i][j][1]) in (10, 11, 12, 13):
                id_tiles.append(board[i][j][3])

    return id_tiles


def check_for_moves(target, to_go, board_id):
    '''
    Function check if move is valid 
    Return: boolean
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Take current team
    team = what_turn(board_id)

    # Check for valid move
    if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) in (18, 19): # Check if target is in fortress
        for s in range(len(pirats)):
            if s != int(team) - 1:
                for d in range(len(pirats[s])):
                    if int(pirats[s][d][0]) == int(target):
                        return False

                # Look for BenGan
                if int(bengan[0]) == 2 and int(bengan[8]) == int(s) + 1:
                    if int(target) == int(bengan[1:5]):
                        return False

                # Look for Friday
                if int(friday[0]) == 2 and int(friday[5]) == int(s) + 1:
                    if int(target) == int(friday[1:5]):
                        return False

                # Look for missioner-pirat
                if int(missioner[0]) == 2 and int(missioner[8]) == int(s) + 1 and int(missioner[9]) == 1:
                    if int(target) == int(missioner[1:5]):
                        return False

    # Look for missioner 
    if int(missioner[0]) == 2 and int(missioner[8]) != int(team) and int(missioner[9]) == 0:
        if int(target) == int(missioner[1:5]):
            if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) not in (10, 11, 12, 13): # Check for to-go tiles
                return False
            elif int(to_go) == 0 and int(missioner[7]) == 1:
                return False
            elif int(to_go) != 0:
                if int(missioner[7]) == int(to_go) + 1:
                    return False

    return True


def check_for_other_pirats(target, board_id):
    '''
    Function check if on target there is enemy
    Return: boolean
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday

    # Take current team
    team = what_turn(board_id)

    # Check for valid move with coin
    for s in range(len(pirats)):# Check if target is pirat from another team
        if s != int(team) - 1:
            for d in range(len(pirats[s])):
                if int(pirats[s][d][0]) == int(target):
                    return False

            # Look for BenGan
            if int(bengan[0]) == 2 and int(bengan[8]) == int(s) + 1:
                if int(target) == int(bengan[1:5]):
                    return False

            # Look for Friday
            if int(friday[0]) == 2 and int(friday[5]) == int(s) + 1:
                if int(target) == int(friday[1:5]):
                    return False

    return True


def check_for_moves_with_coin(target, to_go, board_id):
    '''
    Function check if move can be made with coin or treasure
    Return: boolean
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Take current team
    team = what_turn(board_id)

    # Check for valid move with coin
    if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) in (18, 19, 40): # Check if target is fortress, ressurect or jungle
        return False
    elif int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][0]) == 1: # Check if tile is closed
        return False
    for s in range(len(pirats)):# Check if target is pirat from another team (including layers)
        if s != int(team) - 1:
            for d in range(len(pirats[s])):
                if int(pirats[s][d][0]) == int(target):
                    if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) not in (10, 11, 12, 13): # Check for to-go tiles
                        return False
                    elif int(to_go) == 0 and int(pirats[s][d][3]) == 1:
                        return False
                    elif int(to_go) != 0:
                        if int(pirats[s][d][3]) == int(to_go) + 1:
                            return False

            # Look for BenGan
            if int(bengan[0]) == 2 and int(bengan[8]) == int(s) + 1:
                if int(target) == int(bengan[1:5]):
                    if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) not in (10, 11, 12, 13): # Check for to-go tiles
                        return False
                    elif int(to_go) == 0 and int(bengan[7]) == 1:
                        return False
                    elif int(to_go) != 0:
                        if int(bengan[7]) == int(to_go) + 1:
                            return False

            # Look for Friday
            if int(friday[0]) == 2 and int(friday[5]) == int(s) + 1:
                if int(target) == int(friday[1:5]):
                    if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) not in (10, 11, 12, 13): # Check for to-go tiles
                        return False
                    elif int(to_go) == 0 and int(friday[6]) == 1:
                        return False
                    elif int(to_go) != 0:
                        if int(friday[6]) == int(to_go) + 1:
                            return False

            # Look for missioner-pirat
            if int(missioner[0]) == 2 and int(missioner[8]) == int(s) + 1 and int(missioner[9]) == 1:
                if int(target) == int(missioner[1:5]):
                    if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) not in (10, 11, 12, 13): # Check for to-go tiles
                        return False
                    elif int(to_go) == 0 and int(missioner[7]) == 1:
                        return False
                    elif int(to_go) != 0:
                        if int(missioner[7]) == int(to_go) + 1:
                            return False

    # Look for missioner
    if int(missioner[0]) == 2 and int(missioner[8]) != int(team) and int(missioner[9]) == 0:
        if int(target) == int(missioner[1:5]):
            if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) not in (10, 11, 12, 13): # Check for to-go tiles
                return False
            elif int(to_go) == 0 and int(missioner[7]) == 1:
                return False
            elif int(to_go) != 0:
                if int(missioner[7]) == int(to_go) + 1:
                    return False

    return True


def pass_turn(request, board_id):
    '''
    Function make turn pass and kill mover (with alert)
    Return: nothing (status 200)
    '''

    if request.method == 'PUT':

        # Load board
        get_board = Board.objects.get(pk=board_id)
        jsonDec = json.decoder.JSONDecoder()
        coin = jsonDec.decode(get_board.coins)
        pirats = jsonDec.decode(get_board.pirats)

        # Look for active event
        if get_board.event != 0:
            if get_board.event == 1 or get_board.event == 2 or get_board.event == 3 or get_board.event == 4:
                get_board.event = 0
                get_board.lighthouse = False
                get_board.save()
            if get_board.event == 6 or get_board.event == 7:
                get_board.event = 0
                get_board.earthquake = False
                get_board.save()

        # kill mover
        if get_board.mover != '':
            # Get mover's tile id
            if int(get_board.chosen[1]) <= 3: # Pirats
                from_id = int(pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][0])
            elif int(get_board.chosen[1]) == 4: # BenGan
                from_id = int(get_board.bengan[1:5])
            elif int(get_board.chosen[1]) == 5: # Friday
                from_id = int(get_board.friday[1:5])
            elif int(get_board.chosen[1]) == 6: # Missioner
                from_id = int(get_board.missioner[1:5])
            # Destroy coin or treasure if there is one
            if get_board.with_coin == '1':
                for t, r in enumerate(coin):
                    if int(r[0]) == from_id:
                        coin[t][0] = 5
                        coin[t][1] = 0
                        get_board.coins = json.dumps(coin)
                        break
            if get_board.with_treasure == '1':
                get_board.with_treasure = 5
            get_board.save()
            loop(board_id)
        else:
            change_turn(0, 0, board_id)

        return HttpResponse(status=200)


def change_turn(from_id, target_id, board_id, v=0):
    '''
    Function change turn to next user
    Return: nothing 
    '''

    # Check for infinite loop
    if v != 5:

        # Get board from database
        get_board = Board.objects.get(pk=board_id)
        jsonDec = json.decoder.JSONDecoder()
        pirats = jsonDec.decode(get_board.pirats)
        bengan = get_board.bengan
        friday = get_board.friday
        missioner = get_board.missioner

        # Kill enemy if there is one (do not kill if there is swap in caves)
        if target_id != 0:
            if get_board.first_cave != 'nokill' or get_board.impossible != '1':
                if v == 0:
                    get_board.save()
                    get_board = kill_enemy(target_id, board_id)
                    get_board.save()
            elif v != 0:
                pass
            else:
                get_board.first_cave = 'none'
                get_board.impossible = ''
                get_board.save()

        # Get board from database
        get_board = Board.objects.get(pk=board_id)
        jsonDec = json.decoder.JSONDecoder()
        pirats = jsonDec.decode(get_board.pirats)
        bengan = get_board.bengan
        friday = get_board.friday
        missioner = get_board.missioner

        # Look for impossible (Friday and missioner is on one tile)
        if int(get_board.missioner[0]) == 2 and int(get_board.friday[0]) == 2 and int(get_board.missioner[1:5]) == int(get_board.friday[1:5]):
            get_board.missioner = '0000000000'
            get_board.friday = '0000000'
            get_board.save()

        # Remove movement with coin (if not mover)
        get_board.with_coin = 0
        get_board.with_treasure = 0

        get_board.ice = ''

        # Remove events
        get_board.event = 0
        get_board.cave = 0
        get_board.earthquake_tile = ''

        # Make cannabis event 1 less (if it is active)
        if int(get_board.cannabis) != 1:
            get_board.cannabis = int(get_board.cannabis) - 1

        # Remove mover
        get_board.mover = ''
        get_board.chosen = ''
        
        if win(board_id):
            get_board.play = False
            get_board.cannabis = 1
            get_board.save()
            return None

        # Change turn, 1 to 2, 2 to 3, 3 to 4, 4 to 1
        turn = int(get_board.turn)
        if turn == 4:
            get_board.turn = 1
            get_board.save()
        else:
            get_board.turn = int(get_board.turn) + 1
            get_board.save()

        # decrease by 1 rum effect from next team
        turn = int(what_turn(board_id))
        for i in range(len(pirats[turn - 1])):
            if int(pirats[turn - 1][i][1]) != 0:
                pirats[turn - 1][i][1] -= 1
        if int(bengan[0]) == 2 and int(bengan[8]) == int(turn):
            if int(bengan[5]) != 0:
                bengan = bengan[:5] + str(int(bengan[5]) - 1) + bengan[6:]
        if int(missioner[0]) == 2 and int(missioner[8]) == int(turn) and int(missioner[9]) == 1:
            if int(missioner[5]) != 0:
                missioner = missioner[:5] + str(int(missioner[5]) - 1) + missioner[6:]

        get_board.bengan = bengan
        get_board.missioner = missioner
        get_board.pirats = json.dumps(pirats)
        get_board.save()

        # Check if next pirats are all dead - change turn
        turn = int(what_turn(board_id))
        if pirats[turn - 1][0][0] == 0 and pirats[turn - 1][1][0] == 0 and pirats[turn - 1][2][0] == 0: # all dead
            if int(bengan[0]) != 2 and int(bengan[8]) == int(turn):
                pass
            elif int(missioner[0]) != 2 and int(missioner[8]) == int(turn):
                pass
            elif int(friday[0]) != 2 and int(friday[5]) == int(turn):
                pass
            else:
                change_turn(from_id, target_id, board_id, v + 1)

    else:
        print('Something go wrong, DO magic !!!!!!!!!')


def enemy_ship(tile, board_id):
    '''
    Function check if there is enemy ship on tile
    Return: boolean 
    '''

    # This function take current turn and ID of target tile (ship) and if ship is enemy - return true (then pirat will die)
    turn = int(what_turn(board_id))

    # Load ships
    ships = load_ships_p(board_id)

    # Find your ship
    if ships[turn - 1] == tile:
        return False
    return True


def kill_enemy(target, board_id):
    '''
    Function kill enemy if there is one
    Return: board 
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # if mover is friday - don't kill
    if get_board.mover[1] == '5':
        return get_board

    # Check who's turn is now
    turn = what_turn(board_id)

    # Look for jungle
    jungle = 0
    if int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) == 40:
        jungle = 1

    # Look for enemies and kill them
    for i in range(len(pirats)):
        if int(turn) - 1 != i:
            ship_found = getattr(get_board, ('ship' + str(i + 1)))
            for j in range(len(pirats[i])):
                if int(pirats[i][j][0]) == int(target) and jungle == 0 and int(pirats[i][j][3]) == get_movers_layer(board_id):
                    pirats[i][j][0] = int(ship_found)
                    pirats[i][j][1] = 0
                    pirats[i][j][2] = 0
                    pirats[i][j][3] = 0
                    get_board.pirats = json.dumps(pirats)

            if int(bengan[0]) == 2 and int(bengan[8]) == i + 1 and int(bengan[1:5]) == int(target) and jungle == 0 and int(bengan[7]) == get_movers_layer(board_id):
                bengan = bengan[0] + str(ship_found) + '000' + bengan[8]
                get_board.bengan = bengan
            if int(missioner[0]) == 2 and int(missioner[8]) == i + 1 and int(missioner[9]) == 1 and int(missioner[1:5]) == int(target) and jungle == 0 and int(missioner[7]) == get_movers_layer(board_id):
                missioner = missioner[0] + str(ship_found) + '000' + missioner[8:]
                get_board.missioner = missioner
            if int(friday[0]) == 2 and int(friday[5]) == i + 1 and int(friday[1:5]) == int(target) and int(board[int(str(target)[0:2]) - 11][int(str(target)[2:4]) - 11][1]) != 17 and get_movers_layer(board_id) == 0:
                friday = friday[0:5] + str(turn) + '0'
                get_board.friday = friday

    get_board.save()

    return get_board


def get_movers_layer(board_id):
    '''
    Function return the layer of the mover
    Return: layer (int) 
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats

    # Look for mover
    if int(get_board.chosen[1]) <= 3: # Pirats
        return int(pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][3])
    elif int(get_board.chosen[1]) == 4: # BenGan
        return int(get_board.bengan[7])
    elif int(get_board.chosen[1]) == 5: # Friday
        return int(get_board.friday[6])
    elif int(get_board.chosen[1]) == 6: # Missioner
        return int(get_board.missioner[7])


def loop(board_id): 
    '''
    Function Kill pirat if he make in infinite loop, impossible move or goes to cannibal
    Return: nothing
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # make pirat die
    if int(get_board.chosen[1]) <= 3: # Pirats
        pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][0] = 0
        get_board.pirats = json.dumps(pirats)
    elif int(get_board.chosen[1]) == 4: # BenGan
        bengan = '00000' + bengan[5:]
        get_board.bengan = bengan
    elif int(get_board.chosen[1]) == 5: # Friday
        friday = '0000000'
        get_board.friday = friday
    elif int(get_board.chosen[1]) == 6: # Missioner
        missioner = '00000' + missioner[5:]
        get_board.missioner = missioner

    get_board.save()

    change_turn(0, 0, board_id)


def from_air(source, board_id):
    '''
    Function check if source tile is airplane
    Return: boolean
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # Find tile
    if int(board[int(str(source)[0:2]) - 11][int(str(source)[2:4]) - 11][1]) == 26:
        return True

    return False


def enemy_on_tile(target, board_id):
    '''
    Function check if there is enemy on tile
    Return: boolean
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Check who's turn is now
    turn = what_turn(board_id)

    for i in range(len(pirats)):
        if i != int(turn) - 1:
            for j in range(len(pirats[i])):
                if int(target) == pirats[i][j][0]:
                    return True
            if int(bengan[0]) == 2 and int(bengan[8]) == i + 1 and int(bengan[1:5]) == int(target):
                return True
            if int(missioner[0]) == 2 and int(missioner[8]) == i + 1 and int(missioner[1:5]) == int(target):
                return True
            if int(friday[0]) == 2 and int(friday[5]) == i + 1 and int(friday[1:5]) == int(target):
                return True

    return False


def write_turn(from_id, target_id, board_id, check_turn):
    '''
    Function will write in database current turn
    Return: nothing
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)

    # Load ships
    ships = load_ships_p(board_id)

    # Write turn into database
    if from_id != 0 and target_id != 0:
        
        this_turn = Turns()

        try:
            last_turn = Turns.objects.filter(board=get_board).order_by('-pk')[:1]
            this_turn.turn_number = int(last_turn[0].turn_number) + 1
        except:
            this_turn.turn_number = 1

        this_turn.board = get_board
        if is_water(from_id, board_id):
            if from_id in ships:
                this_turn.from_id = 'ship'
            else:
                this_turn.from_id = 'water'
        else:
            this_turn.from_id = from_id
        if is_water(target_id, board_id):
            if target_id in ships:
                this_turn.target_id = 'ship'
            else:
                this_turn.target_id = 'water'
        elif check_turn == 'impossible':
            this_turn.target_id = 'closed_tile'
        else:
            this_turn.target_id = target_id
        this_turn.team = what_turn(board_id)
        this_turn.pirat = get_board.mover
        this_turn.with_coin = get_board.with_coin
        this_turn.with_treasure = get_board.with_treasure

        this_turn.save()


def impossible(from_id, target_id, board_id):
    '''
    Function looks for moves that can't be done
    Return: Boolean
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # make variables
    tile_from = 0
    tile_to = 0

    # if going from one-point arrow or ice
    if int(board[int(str(from_id)[0:2]) - 11][int(str(from_id)[2:4]) - 11][1]) in (2, 3, 14):
        tile_from = 1

    # if going to fortress
    if int(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][1]) in (18, 19):
        tile_to = 1

    # if goint to fortress with enemy
    if tile_from == 1 and tile_to == 1 and enemy_on_tile(target_id, board_id):
        return True

    # if going with coin or treasure
    if get_board.with_coin == '1' or get_board.with_treasure == '1':
        # if going to tile where is enemy
        if enemy_on_tile(target_id, board_id):
            return True
        # if going to closed tile
        if int(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][0]) == 1:
            return True
        # if going to jungle
        if int(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][1]) == 40:
            return True
        # if going to fortress
        if int(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][1]) in (18, 19):
            return True

    # if going to tile where missioner is
    if get_board.missioner[0] == '2' and get_board.missioner[9] == '0' and (get_board.missioner[1-5]) == target_id and int(get_board.missioner[8]) != what_turn(board_id):
        return True
    
    return False


def move_pirat(request, from_to_id, board_id, v=0):
    '''
    Function make move
    Return: nothing (status 200)
    '''

    # This function will take ID of tile and ID of target and move pirat to new location

    if request.method == 'PUT':

        # Get board from database
        get_board = Board.objects.get(pk=board_id)
        jsonDec = json.decoder.JSONDecoder()
        board = jsonDec.decode(get_board.board) # Load board
        coin = jsonDec.decode(get_board.coins) # Load coins
        rum_decode = jsonDec.decode(get_board.rum) # Load rum
        pirats = jsonDec.decode(get_board.pirats) # Load pirats
        bengan = get_board.bengan
        friday = get_board.friday
        missioner = get_board.missioner

        # Load ships
        ships = load_ships_p(board_id)

        # Get from ID and target ID
        from_id = int(str(from_to_id)[0:4])
        target_id = int(str(from_to_id)[4:8])
        team_index = int(what_turn(board_id)) - 1
        team = int(what_turn(board_id))

        # Check for impossible move (cheating)
        # Not working (need more to code function possible moves)
        #if int(target_id) not in possible_moves(request, from_id, board_id, 1):
            #print('Cheat!!')
            #return render(request, "game/cheat.html")

        # Check for impossible moves
        if impossible(from_id, target_id, board_id):
            get_board.impossible = 1
            get_board.save() # Make change turn() - don't kill if there is someone on the target tile
            get_board = Board.objects.get(pk=board_id)
            write_turn(from_id, target_id, board_id, 'impossible') # write down this turn
            get_board = Board.objects.get(pk=board_id)
            # Destroy coin or treasure if there is one
            if get_board.with_coin == '1':
                for t, r in enumerate(coin):
                    if int(r[0]) == from_id:
                        coin[t][0] = 5
                        coin[t][1] = 0
                        get_board.coins = json.dumps(coin)
                        break
            if get_board.with_treasure == '1':
                get_board.with_treasure = 5
            get_board.save()
            get_board = Board.objects.get(pk=board_id)
            loop(board_id) # kill mover
            print('impossible move detected')
            return HttpResponse(status=200)

        # Check for ship movement
        if from_id == ships[team_index]:
            if is_water(target_id, board_id):
                # Move ship with all pirats on-board
                ship_found = 'ship' + str(team)
                setattr(get_board, ship_found, target_id)
                for j in range(len(pirats[team_index])):
                    if pirats[team_index][j][0] == from_id: # Try to find pirats
                        pirats[team_index][j][0] = target_id
                if int(bengan[0]) == 2 and int(bengan[8]) == int(team) and int(bengan[1:5]) == from_id:
                    bengan = bengan[0] + str(target_id) + bengan[5:]
                    get_board.bengan = bengan
                if int(missioner[0]) == 2 and int(missioner[8]) == int(team) and int(missioner[1:5]) == from_id:
                    missioner = missioner[0] + str(target_id) + missioner[5:]
                    get_board.missioner = missioner
                if int(friday[0]) == 2 and int(friday[5]) == int(team) and int(friday[1:5]) == from_id:
                    friday = friday[0] + str(target_id) + friday[5:]
                    get_board.friday = friday
                # If there is enemies in water - kill them
                for i in range(len(pirats)):
                    if i != team_index:
                        for j in range(len(pirats[i])):
                            if int(pirats[i][j][0]) == target_id:
                                pirats[i][j][0] = 0
                if int(bengan[1:5]) == target_id and int(bengan[8]) != team: # BenGan
                    bengan = '00000' + bengan[5:]
                    get_board.bengan = bengan
                if int(friday[1:5]) == target_id and int(friday[5]) != team: # Friday
                    friday = '0000000'
                    get_board.friday = friday
                if int(missioner[1:5]) == target_id and int(missioner[8]) != team: # Missioner
                    missioner = '00000' + missioner[5:]
                    get_board.missioner = missioner

                get_board.pirats = json.dumps(pirats)
                get_board.save()
            else:
                # Remove one pirat from ship and move it to target
                if int(get_board.chosen[1]) <= 3: # Pirats
                    pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][0] = target_id
                    get_board.pirats = json.dumps(pirats)
                elif int(get_board.chosen[1]) == 4: # BenGan
                    bengan = bengan[0] + str(target_id) + bengan[5:]
                    get_board.bengan = bengan
                elif int(get_board.chosen[1]) == 5: # Friday
                    friday = friday[0] + str(target_id) + friday[5:]
                    get_board.friday = friday
                elif int(get_board.chosen[1]) == 6:
                    missioner = missioner[0] + str(target_id) + missioner[5:]
                    get_board.missioner = missioner
                get_board.save()

        else:
            remove_layer = 0
            # If moving from to-go tile = remove layer
            if from_id in get_all_to_go_tiles(board_id) and from_id != target_id:
                remove_layer = 1
            # Remove one pirat from that tile and move it to target
            if int(get_board.chosen[1]) <= 3: # Pirats
                pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][0] = target_id
                if remove_layer == 1:
                    pirats[int(get_board.chosen[0]) - 1][int(get_board.chosen[1]) - 1][3] = 0
                get_board.pirats = json.dumps(pirats)
            elif int(get_board.chosen[1]) == 4: # BenGan
                if remove_layer == 1:
                    bengan = bengan[0] + str(target_id) + bengan[5:7] + '0' + bengan[8:]
                else:
                    bengan = bengan[0] + str(target_id) + bengan[5:]
                get_board.bengan = bengan
            elif int(get_board.chosen[1]) == 5: # Friday
                friday = friday[0] + str(target_id) + friday[5:]
                get_board.friday = friday
            elif int(get_board.chosen[1]) == 6: # Missioner
                if remove_layer == 1:
                    missioner = missioner[0] + str(target_id) + missioner[5:7] + '0' + missioner[8:]
                else:
                    missioner = missioner[0] + str(target_id) + missioner[5:]
                get_board.missioner = missioner

            get_board.save()
            if from_air(from_id, board_id):
                get_board.airplane = False
                get_board.save()

        # Make current pirat mover
        get_board.mover = get_board.chosen
        get_board.save()

        closed = 0

        # Check for target tile
        if board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][0] == 1: # Open tile if tile is closed
            closed = 1
            if board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][1] in (20, 21, 22, 23, 24): # add gold if opened tile is coins
                coins = add_coins(target_id, board, board_id)
                get_board.coins = json.dumps(coins)
            elif board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][1] == 25: # add treasure if opened tile is treasure
                get_board.treasure = str(target_id) + '0'
            elif board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][1] in (34, 35, 36): # add rum to team count if opened tile is rum
                rum = add_rum(target_id, board, board_id)
                get_board.rum = json.dumps(rum)
            board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][0] = 2
            get_board.board = json.dumps(board)
        target = [int(str(target_id)[0:2]) - 11, int(str(target_id)[2:4]) - 11]
        if int(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][3]) in rum_decode:
            rum = take_rum_from_ground(target_id, board_id)
            get_board.rum = json.dumps(rum)
        get_board.save()

        # Move coin
        stop_coin = 0
        if int(get_board.with_coin) == 1:
            if board[(int(str(target_id)[0:2]) - 11)][(int(str(target_id)[2:4]) - 11)][1] in (10, 11, 12, 13) and target_id != from_id: # If target is to-go, coin goes to lowest layer
                for t, r in enumerate(coin):
                    if int(r[0]) == from_id:
                        coin[t][0] = target_id
                        coin[t][1] = 1
                        get_board.coins = json.dumps(coin)
                        break
            elif target_id in ships: # If target is ship - give coin to team
                stop_ship_coin = 0
                for t, r in enumerate(coin):
                    if int(r[0]) == from_id and stop_ship_coin == 0:
                        for p in range(len(ships)):
                            if target_id == int(ships[p]):
                                coin[t][0] = p + 1
                                coin[t][1] = 0
                                get_board.coins = json.dumps(coin)
                                stop_ship_coin = 1
                                break
            elif board[(int(str(from_id)[0:2]) - 11)][(int(str(from_id)[2:4]) - 11)][1] in (10, 11, 12, 13) and from_id == target_id: # if pirat is going throught layers
                for t, r in enumerate(coin):
                    if int(r[0]) == from_id and int(r[1]) == get_movers_layer(board_id):
                        coin[t][1] = get_movers_layer(board_id) + 1
                        get_board.coins = json.dumps(coin)
                        break
            elif board[(int(str(from_id)[0:2]) - 11)][(int(str(from_id)[2:4]) - 11)][1] in (10, 11, 12, 13) and target_id != from_id: # if going out of layer - coin goes to ground
                for t, r in enumerate(coin):
                    if int(r[0]) == from_id and int(r[1]) == (int(board[(int(str(from_id)[0:2]) - 11)][(int(str(from_id)[2:4]) - 11)][1]) - 8):
                        coin[t][0] = target_id
                        coin[t][1] = 0
                        get_board.coins = json.dumps(coin)
                        break
            else:
                for t, r in enumerate(coin):
                    if int(r[0]) == from_id:
                        if stop_coin == 0 and is_water(target_id, board_id): # Destroy coin if it goes in water
                            coin[t][0] = 5
                            coin[t][1] = 0
                        elif stop_coin == 0:
                            coin[t][0] = target_id
                        get_board.coins = json.dumps(coin)
                        break

        # Move treasure
        stop_treasure = 0
        if int(get_board.with_treasure) == 1:
            if board[(int(str(target_id)[0:2]) - 11)][(int(str(target_id)[2:4]) - 11)][1] in (10, 11, 12, 13) and target_id != from_id: # If target is to-go, treasure goes to lowest layer
                get_board.treasure = str(target_id) + str(1)
            elif target_id in ships: # If target is ship - give treasure to team
                for o in range(len(ships)):
                    if target_id == int(ships[o]):
                        get_board.treasure = o + 1
                        get_board.with_treasure = 0
            elif board[(int(str(from_id)[0:2]) - 11)][(int(str(from_id)[2:4]) - 11)][1] in (10, 11, 12, 13) and from_id == target_id: # if pirat is going throught layers
                get_board.treasure = str(target_id) + str(get_movers_layer(board_id) + 1)
            elif board[(int(str(from_id)[0:2]) - 11)][(int(str(from_id)[2:4]) - 11)][1] in (10, 11, 12, 13) and from_id != target_id: # if going out of layer - treasure goes to ground
                get_board.treasure = str(target_id) + '0'
            else:
                if int(get_board.treasure) > 10:
                    if int(str(get_board.treasure)[0:4]) == from_id:
                        if stop_treasure == 0 and is_water(target_id, board_id): # Destroy treasure if it goes in water
                            get_board.treasure = 5
                        elif stop_treasure == 0:
                            get_board.treasure = str(target_id) + '0'

        get_board.save()
        write_turn(from_id, target_id, board_id, 'turn')

        # load available movement (due to tile)
        function_name = globals()[MOVES[board[target[0]][target[1]][1]]]
        function_name(request, from_id, target_id, v, board_id, closed)

    return HttpResponse(status=200)


def move_stop(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    make mover stop and change turn
    '''

    # Change turn
    change_turn(source_id, target_id, board_id)


def move_next(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    make another move
    '''
    pass


def move_lighthouse(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    First time get on tile - open 4 tile
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)

    if not get_board.lighthouse:
        move_stop(request, source_id, target_id, v, board_id, closed=0)
    else:
        get_board.event = 1
        get_board.save()


def move_earthquake(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    First time get on tile - change 2 tiles
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)

    if not get_board.earthquake:
        move_stop(request, source_id, target_id, v, board_id, closed=0)
    else:
        get_board.event = 6
        get_board.save()


def move_bengan(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    First time get on tile - get bengan
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)

    bengan = get_board.bengan

    team = what_turn(board_id)

    if int(bengan[0]) == 1: # if BenGan is not yet found - he goes to first pirat that find him
        bengan = '2' + str(target_id) + '000' + str(team)
        get_board.bengan = bengan
        get_board.save()

    move_stop(request, source_id, target_id, v, board_id)


def move_friday(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    First time get on tile - get Friday
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)

    friday = get_board.friday

    team = what_turn(board_id)

    if int(friday[0]) == 1: # if Friday is not yet found - he goes to first pirat that find him
        friday = '2' + str(target_id) + str(team) + '0'
        get_board.friday = friday
        get_board.save()

    move_stop(request, source_id, target_id, v, board_id)


def move_missioner(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    First time get on tile - get missioner
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)

    missioner = get_board.missioner

    team = what_turn(board_id)

    if int(missioner[0]) == 1: # if Missioner is not yet found - he goes to first pirat that find him
        missioner = '2' + str(target_id) + '000' + str(team) + '0'
        get_board.missioner = missioner
        get_board.save()

    move_stop(request, source_id, target_id, v, board_id)


def move_airplane(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    First time get on tile - go by airplane
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)

    if not get_board.airplane:
        move_stop(request, source_id, target_id, v, board_id)


def move_water(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    movement in water - check for enemy ship and change turn after move
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats

    # Load ships
    ships = load_ships_p(board_id)

    if target_id in ships:
        if enemy_ship(target_id, board_id):
            if int(get_board.mover[1]) <= 3: # Pirats
                pirats[int(get_board.mover[0]) - 1][int(get_board.mover[1]) - 1][0] = 0 # Pirat die
                get_board.pirats = json.dumps(pirats)
            elif int(get_board.mover[1]) == 4: # BenGan die
                bengan = '00000000'
                get_board.bengan = bengan
            elif int(get_board.mover[1]) == 5: # Friday die
                friday = '0000000'
                get_board.friday = friday
            elif int(get_board.mover[1]) == 6: # Missioner die
                missioner = '000000000'
                get_board.missioner = missioner

    get_board.save()
    change_turn(source_id, target_id, board_id)


def move_auto(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    Make auto move if target tile is auto-move (like one point arrow)
    '''

    new_target_id = Every(int(target_id), board_id) # Get new target to make auto-move
    if len(new_target_id) != 1:
        print("Something goes wrong!")
    result = str(target_id) + str(new_target_id[0])
    if v < 5: # Try to find infinite loop (pirat death)
        move_pirat(request, result, board_id, v + 1)
    else:
        loop(board_id)
        print('Infinite Loop found! (auto)')


def move_pit(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    Make pirat fall or take teammate from pit
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Get current team
    team_index = int(what_turn(board_id)) - 1
    team = int(what_turn(board_id))

    fallen = 0

    # if there is a friendly pirat in pit - don't fall and uplift him
    for i in range(len(pirats[team_index])):
        if pirats[team_index][i][0] == int(target_id) and (str(team) + str(i + 1)) != get_board.mover:
            pirats[team_index][i][2] = 0
            get_board.pirats = json.dumps(pirats)
            get_board.save()
            fallen = 1
    if int(bengan[0]) == 2 and int(bengan[8]) == team and int(bengan[1:5]) == int(target_id) and (str(team) + str(4)) != get_board.mover:
        bengan = bengan[0:6] + '0' + bengan[7:]
        get_board.bengan = bengan
        get_board.save()
        fallen = 1
    if int(missioner[0]) == 2 and int(missioner[8]) == team and int(missioner[1:5]) == int(target_id) and (str(team) + str(6)) != get_board.mover:
        missioner = missioner[0:6] + '0' + missioner[7:]
        get_board.missioner = missioner
        get_board.save()
        fallen = 1
    if int(friday[0]) == 2 and int(friday[1:5]) == int(target_id):
        fallen = 1

    if fallen == 0: # pirat fall into pit
        if int(get_board.mover[1]) <= 3: # Pirat
            pirats[int(get_board.mover[0]) - 1][int(get_board.mover[1]) - 1][2] = 1
            get_board.pirats = json.dumps(pirats)
        elif int(get_board.mover[1]) == 4: # BenGan
            bengan = bengan[0:6] + '1' + bengan[7:]
            get_board.bengan = bengan
        elif int(get_board.mover[1]) == 6: # Missioner
            missioner = missioner[0:6] + '1' + missioner[7:]
            get_board.missioner = missioner
        get_board.save()

    # Change turn
    change_turn(source_id, target_id, board_id)


def move_ice(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    make another auto-move
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    check = 0
    if get_board.ice != '':
        check = int(get_board.ice[0:2])

    if board[int(str(source_id)[0:2]) - 11][int(str(source_id)[2:4]) - 11][1] == 9 or check == 99: # If source tile: horse - choose another move
        get_board.ice = str(99) + str(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][3])
        get_board.save()
    elif board[int(str(source_id)[0:2]) - 11][int(str(source_id)[2:4]) - 11][1] == 26 or check == 26: # If source tile: airplane - choose another move
        get_board.ice = str(26) + str(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][3])
        get_board.save()
    else: # else: auto_move
        new_target_id = int(target_id) + (int(target_id) - int(source_id))
        result = str(target_id) + str(new_target_id)
        if v < 5: # Try to find infinite loop (pirat death)
            move_pirat(request, result, board_id, v + 1)
        else:
            loop(board_id)
            print('Infinite Loop found! (ice)')


def move_rum(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is rum and mover is friday or missioner - get drunk or die
    '''

    # Get board from database
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    rum = jsonDec.decode(get_board.rum) # Load rum
    missioner = get_board.missioner

    if closed == 1:
        if int(get_board.mover[1]) == 5: # if mover is friday - he die
            for i in rum:
                if i == int(get_board.mover[0]):
                    rum[i] = 0
                    get_board.rum = json.dumps(rum)
                    get_board.save()
                    break
            get_board.friday = '0000000'
            get_board.save()
            change_turn(source_id, target_id, board_id)
        elif int(get_board.mover[1]) == 6 and int(missioner[9]) == 0: # if mover is missioner and he is not a pirat he bacame pirat
            for i in rum:
                if i == int(get_board.mover[0]):
                    rum[i] = 0
                    get_board.rum = json.dumps(rum)
                    get_board.save()
                    break
            get_board.missioner = missioner[:9] + '1'
            get_board.save()
            change_turn(source_id, target_id, board_id)
        else:
            change_turn(source_id, target_id, board_id)
    else:
        change_turn(source_id, target_id, board_id)


def move_croc(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is croc - return to last tile
    '''

    # Reverse target and source and make another move
    result = str(target_id) + str(source_id)
    if v < 5: # Try to find infinite loop (pirat death)
        move_pirat(request, result, board_id, v + 1)
    else:
        loop(board_id)
        print('Infinite Loop found! (croc)')


def move_cannibal(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is cannibal - eat pirat
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)

    # Look for friday
    if int(get_board.mover[1]) == 5:
        change_turn(source_id, target_id, board_id)
    else:
        # Pirat die
        loop(board_id)


def move_barrel(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    make pirat drunk for 1 turn
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Increase drunk effect by 1
    if int(get_board.mover[1]) <= 3: # Pirat
        pirats[int(get_board.mover[0]) - 1][int(get_board.mover[1]) - 1][1] = 2
        get_board.pirats = json.dumps(pirats)
    elif int(get_board.mover[1]) == 4: # BenGan
        bengan = bengan[0:5] + '2' + bengan[6:]
        get_board.bengan = bengan
    elif int(get_board.mover[1]) == 5: # Friday die
        friday = '0000000'
        get_board.friday = friday
    elif int(get_board.mover[1]) == 6 and int(missioner[9]) == 1: # If missioner is pirat - he get drunk
        missioner = missioner[0:5] + '2' + missioner[6:]
        get_board.missioner = missioner
    elif int(get_board.mover[1]) == 6 and int(missioner[9]) == 0: # If missioner is not a pirat - became pirat
        missioner = missioner[0:9] + '1'
        get_board.missioner = missioner
    get_board.save()

    # Change turn
    change_turn(source_id, target_id, board_id)

def move_cave(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is cave - go to another cave, if there is no opened cave - pirat will wait (like pit)
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Kill enemy if there is one
    if get_board.first_cave ==  'none':
        get_board = kill_enemy(target_id, board_id)

    cave = []

    # count of opened caves
    count_opened = 0
    count_with_pirats = 0
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j][1] == 38 and board[i][j][0] == 2:
                count_opened += 1
                cave.append(int(board[i][j][3]))
                if enemy_on_tile(board[i][j][3], board_id):
                    count_with_pirats += 1

    if count_opened == 1 and get_board.first_cave == '': # if there is first cave opened - pirat fall into cave and can't move(only first pirat)
        if int(get_board.mover[1]) <= 3: # Pirat
            pirats[int(get_board.mover[0]) - 1][int(get_board.mover[1]) - 1][2] = 1
            get_board.first_cave = 'pirat' + str(get_board.mover)
        elif int(get_board.mover[1]) == 4 and get_board.first_cave ==  '': # BenGan
            bengan = bengan[0:6] + '1' + bengan[7:]
            get_board.bengan = bengan
            get_board.first_cave = 'pirat' + str(get_board.mover)
        elif int(get_board.mover[1]) == 6 and get_board.first_cave ==  '': # Missioner
            missioner = missioner[0:6] + '1' + missioner[7:]
            get_board.missioner = missioner
            get_board.first_cave = 'pirat' + str(get_board.mover)

        get_board.pirats = json.dumps(pirats)
        get_board.save()
    elif count_opened == 1 and get_board.first_cave != '': # if second pirat going to pit - just stop
        move_stop(request, source_id, target_id, v, board_id)
    elif count_opened == 2 and get_board.cave_in: # if there is second cave opened - swap pirats (only first time)
        mover_from = cave[0]
        mover_to = cave[1]
        for i in range(len(pirats)): # swap pirats
            for j in range(len(pirats[i])):
                if int(pirats[i][j][0]) == mover_from:
                    pirats[i][j][0] = mover_to
                    pirats[i][j][2] = 0
                elif int(pirats[i][j][0]) == mover_to:
                    pirats[i][j][0] = mover_from
                    pirats[i][j][2] = 0
        get_board.pirats = json.dumps(pirats)
        if int(bengan[0]) == 2 and int(bengan[1:5]) == mover_from: # swap bengan
            bengan = bengan[0] + str(mover_to) + bengan[5] + '0' + bengan[7:]
            get_board.bengan = bengan
        elif int(bengan[0]) == 2 and int(bengan[1:5]) == mover_to:
            bengan = bengan[0] + str(mover_from) + bengan[5] + '0' + bengan[7:]
            get_board.bengan = bengan
        if int(friday[0]) == 2 and int(friday[1:5]) == mover_from: # swap friday
            friday = friday[0] + str(mover_to) + friday[5:]
            get_board.friday = friday
        elif int(friday[0]) == 2 and int(friday[1:5]) == mover_to:
            friday = friday[0] + str(mover_from) + friday[5:]
            get_board.friday = friday
        if int(missioner[0]) == 2 and int(missioner[1:5]) == mover_from: # swap missioner
            missioner = missioner[0] + str(mover_to) + missioner[5] + '0' + missioner[7:]
            get_board.missioner = missioner
        elif int(missioner[0]) == 2 and int(missioner[1:5]) == mover_to:
            missioner = missioner[0] + str(mover_from) + missioner[5] + '0' + missioner[7:]
            get_board.missioner = missioner
        get_board.cave_in = False
        get_board.first_cave = 'nokill'
        get_board.save()
        change_turn(source_id, target_id, board_id)
        return 1

    # Change turn if pirat is out of cave
    if int(get_board.cave) == 1:
        change_turn(source_id, target_id, board_id)
    else:
        get_board.cave = 1
        get_board.save()
        if count_with_pirats == count_opened - 1: # if there is no empty caves - change turn
            get_board.cave = 0
            get_board.save()
            change_turn(source_id, target_id, board_id)


def move_jungle(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is jungle-to-go - go to lowest layer, if already there - go 1 layer up
    '''

    # go throught layers
    go_layer(2, board_id)

    # Change turn
    change_turn(source_id, target_id, board_id)


def move_desert(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is desert-to-go - go to lowest layer, if already there - go 1 layer up
    '''

    # go throught layers
    go_layer(3, board_id)

    # Change turn
    change_turn(source_id, target_id, board_id)


def move_swamp(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is swamp-to-go - go to lowest layer, if already there - go 1 layer up
    '''

    # go throught layers
    go_layer(4, board_id)

    # Change turn
    change_turn(source_id, target_id, board_id)


def move_waterfall(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is waterfall-to-go - go to lowest layer, if already there - go 1 layer up
    '''

    # go throught layers
    go_layer(5, board_id)

    # Change turn
    change_turn(source_id, target_id, board_id)

def go_layer(layer, board_id):
    '''
    Function-move
    go throught layers
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    pirats = jsonDec.decode(get_board.pirats) # Load pirats
    bengan = get_board.bengan
    friday = get_board.friday
    missioner = get_board.missioner

    # Go to the lowest layer
    if int(get_board.mover[1]) <= 3: # Pirat
        if pirats[int(get_board.mover[0]) - 1][int(get_board.mover[1]) - 1][3] == 0:
            pirats[int(get_board.mover[0]) - 1][int(get_board.mover[1]) - 1][3] = 1
        else:
            pirats[int(get_board.mover[0]) - 1][int(get_board.mover[1]) - 1][3] += 1
        get_board.pirats = json.dumps(pirats)
    elif int(get_board.mover[1]) == 4: # BenGan
        if int(bengan[7]) == 0:
            bengan = bengan[:7] + str(1) + bengan[8]
        else:
            bengan = bengan[:7] + str(int(bengan[7]) + 1) + bengan[8]
        get_board.bengan = bengan
    elif int(get_board.mover[1]) == 5: # friday
        friday = friday[:6] + str(layer)
        get_board.friday = friday
    elif int(get_board.mover[1]) == 6: # missioner
        if int(missioner[7]) == 0:
            missioner = missioner[:7] + str(1) + missioner[8:]
        else:
            missioner = missioner[:7] + str(int(missioner[7]) + 1) + missioner[8:]
        get_board.missioner = missioner

    get_board.save()

def move_cannabis(request, source_id, target_id, v, board_id, closed=0):
    '''
    Function-move
    if target is cannabis - make next pirat other turn
    '''

    # Load board
    get_board = Board.objects.get(pk=board_id)
    jsonDec = json.decoder.JSONDecoder()
    board = jsonDec.decode(get_board.board) # Load board

    # start cannabis event
    if int(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][3]) == int(get_board.cannabis_open[0:4]) or int(board[int(str(target_id)[0:2]) - 11][int(str(target_id)[2:4]) - 11][3]) == int(get_board.cannabis_open[4:8]):
        pass
    else:
        if int(get_board.cannabis_open[0:4]) == 9999:
            get_board.cannabis_open = str(target_id) + get_board.cannabis_open[4:8]
        else:
            get_board.cannabis_open = get_board.cannabis_open[0:4] + str(target_id)
        get_board.cannabis = 6
        get_board.save()

    move_stop(request, source_id, target_id, v, board_id)
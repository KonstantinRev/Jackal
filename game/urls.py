
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("finished", views.finished, name="finished"),
    path("create_board", views.create_board, name="create_board"),
    path("pre_create_board", views.pre_create_board, name="pre_create_board"),
    path("board/<int:board_id>", views.board, name="board"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("find_to_go_pirats/<int:id>/<int:board_id>", views.find_to_go_pirats, name="find_to_go_pirats"),
    path("events/<int:board_id>", views.events, name="events"),
    path("pass_turn/<int:board_id>", views.pass_turn, name="pass_turn"),
    path("pirats_that_can_move/<int:board_id>", views.pirats_that_can_move, name="pirats_that_can_move"),
    path("return_moves_or_not/<int:board_id>", views.return_moves_or_not, name="return_moves_or_not"),
    path("make_mover/<str:pirat>/<int:board_id>", views.make_mover, name="make_mover"),
    path("remove_mover/<int:board_id>", views.remove_mover, name="remove_mover"),
    path("lighthouse_event/<int:board_id>", views.lighthouse_event, name="lighthouse_event"),
    path("open_tile_light/<int:id>/<int:board_id>", views.open_tile_light, name="open_tile_light"),
    path("end_lighthouse/<int:board_id>", views.end_lighthouse, name="end_lighthouse"),
    path("earthquake_event/<int:board_id>", views.earthquake_event, name="earthquake_event"),
    path("change_tile_earth/<int:id>/<int:board_id>", views.change_tile_earth, name="change_tile_earth"),
    path("end_earthquake/<int:board_id>", views.end_earthquake, name="end_earthquake"),
    path("have_coin/<int:target>/<int:board_id>", views.have_coin, name="have_coin"),
    path("is_mover/<int:board_id>", views.is_mover, name="is_mover"),
    path("with_coin_return/<int:board_id>", views.with_coin_return, name="with_coin_return"),
    path("with_coin_change/<int:board_id>", views.with_coin_change, name="with_coin_change"),
    path("with_treasure_return/<int:board_id>", views.with_treasure_return, name="with_treasure_return"),
    path("with_treasure_change/<int:board_id>", views.with_treasure_change, name="with_treasure_change"),
    path("can_drink_rum/<int:id>/<int:board_id>", views.can_drink_rum, name="can_drink_rum"),
    path("drink/<int:id>/<int:board_id>", views.drink, name="drink"),
    path("ressurect/<int:board_id>", views.ressurect, name="ressurect"),
    path("can_ressurect/<int:board_id>", views.can_ressurect, name="can_ressurect"),
    path("load_coins/<int:board_id>", views.load_coins, name="load_coins"),
    path("load_treasure/<int:board_id>", views.load_treasure, name="load_treasure"),
    path("load_rum/<int:board_id>", views.load_rum, name="load_rum"),
    path("load_ships/<int:board_id>", views.load_ships, name="load_ships"),
    path("load_pirats/<int:board_id>", views.load_pirats, name="load_pirats"),
    path("load_pirats_turn/<int:board_id>", views.load_pirats_turn, name="load_pirats_turn"),
    path("possible_moves/<int:id>/<int:board_id>/<int:python>/<str:chosen>", views.possible_moves, name="possible_moves"),
    path("move_pirat/<int:from_to_id>/<int:board_id>", views.move_pirat, name="move_pirat")
]
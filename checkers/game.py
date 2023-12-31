from tkinter import Canvas, Event, messagebox
from PIL import Image, ImageTk
from random import choice
from pathlib import Path
from math import inf

from checkers.field import Field
from checkers.move import Move
from checkers.constants import *
from checkers.enums import CheckerType, SideType

class Game:
    def __init__(self, canvas: Canvas, x_field_size: int, y_field_size: int):
        self._canvas = canvas
        self._field = Field(x_field_size, y_field_size)

        self.__player_turn = True

        self.__hovered_cell = Point()
        self._selected_cell = Point()
        self.__animated_cell = Point()

        self.__init_images()
        
        self.__draw()

        # Если игрок играет за чёрных, то совершить ход противника
        if (player_side == SideType.BLACK):
            self.__handle_enemy_turn()

    def __init_images(self):
        '''Инициализация изображений'''
        self.__images = {
            CheckerType.WHITE_REGULAR: ImageTk.PhotoImage(Image.open(Path('assets', 'white-regular.png')).resize((cell_size, cell_size), Image.ANTIALIAS)),
            CheckerType.BLACK_REGULAR: ImageTk.PhotoImage(Image.open(Path('assets', 'black-regular.png')).resize((cell_size, cell_size), Image.ANTIALIAS)),
            CheckerType.WHITE_QUEEN: ImageTk.PhotoImage(Image.open(Path('assets', 'white-queen.png')).resize((cell_size, cell_size), Image.ANTIALIAS)),
            CheckerType.BLACK_QUEEN: ImageTk.PhotoImage(Image.open(Path('assets', 'black-queen.png')).resize((cell_size, cell_size), Image.ANTIALIAS)),
        }


    def __draw(self):
        '''Отрисовка сетки поля и шашек'''
        self._canvas.delete('all')
        self._draw_field_grid()
        self._draw_checkers()

    def _draw_field_grid(self):
        '''Отрисовка сетки поля'''
        for y in range(self._field.y_size):
            for x in range(self._field.x_size):
                self._canvas.create_rectangle(x * cell_size, y * cell_size, x * cell_size + cell_size, y * cell_size + cell_size, fill=f_colors[(y + x) % 2], width=0, tag='boards')

                # Отрисовка рамок у необходимых клеток
                if (x == self._selected_cell.x and y == self._selected_cell.y):
                    self._canvas.create_rectangle(x * cell_size + border_width // 2, y * cell_size + border_width // 2, x * cell_size + cell_size - border_width // 2, y * cell_size + cell_size - border_width // 2, outline=SELECT_BORDER_COLOR, width=border_width, tag='border')
                elif (x == self.__hovered_cell.x and y == self.__hovered_cell.y):
                    self._canvas.create_rectangle(x * cell_size + border_width // 2, y * cell_size + border_width // 2, x * cell_size + cell_size - border_width // 2, y * cell_size + cell_size - border_width // 2, outline=HOVER_BORDER_COLOR, width=border_width, tag='border')

                # Отрисовка возможных точек перемещения, если есть выбранная ячейка
                if (self._selected_cell):
                    player_moves_list = self.__get_moves_list(player_side)
                    for move in player_moves_list:
                        if (self._selected_cell.x == move.from_x and self._selected_cell.y == move.from_y):
                            self._canvas.create_oval(move.to_x * cell_size + cell_size / 3, move.to_y * cell_size + cell_size / 3, move.to_x * cell_size + (cell_size - cell_size / 3), move.to_y * cell_size + (cell_size - cell_size / 3), fill=POSIBLE_MOVE_CIRCLE_COLOR, width=0, tag='posible_move_circle')

    def _draw_checkers(self):
        '''Отрисовка шашек'''
        for y in range(self._field.y_size):
            for x in range(self._field.x_size):
                # Не отрисовывать пустые ячейки и анимируемую шашку
                if (self._field.type_at(x, y) != CheckerType.NONE):
                    self._canvas.create_image(x * cell_size, y * cell_size, image=self.__images.get(self._field.type_at(x, y)), anchor='nw', tag='checkers')

    def mouse_move(self, event: Event):
        '''Событие перемещения мышки'''
        x, y = (event.x) // cell_size, (event.y) // cell_size
        if (x != self.__hovered_cell.x or y != self.__hovered_cell.y):
            self.__hovered_cell = Point(x, y)

            # Если ход игрока, то перерисовать
            if (self.__player_turn):
                self.__draw()

    def mouse_down(self, event: Event):
        '''Событие нажатия мышки'''
        if not (self.__player_turn): return

        x, y = (event.x) // cell_size, (event.y) // cell_size

        # Если точка не внутри поля
        if not (self._field.is_within(x, y)): return

        if (player_side == SideType.WHITE):
            player_checkers = WHITE_CHECKERS
        elif (player_side == SideType.BLACK):
            player_checkers = BLACK_CHECKERS
        else: return

        # Если нажатие по шашке игрока, то выбрать её
        if (self._field.type_at(x, y) in player_checkers):
            self._selected_cell = Point(x, y)
            self.__draw()
        elif (self.__player_turn):
            move = Move(self._selected_cell.x, self._selected_cell.y, x, y)

            # Если нажатие по ячейке, на которую можно походить
            if (move in self.__get_moves_list(player_side)):
                self.__handle_player_turn(move)

                # Если не ход игрока, то ход противника
                if not (self.__player_turn):
                    self.__handle_enemy_turn()

    def __handle_move(self, move: Move, draw: bool = True) -> bool:
        '''Совершение хода'''

        # Изменение типа шашки, если она дошла до края
        if (move.to_y == 0 and self._field.type_at(move.from_x, move.from_y) == CheckerType.WHITE_REGULAR):
            self._field.at(move.from_x, move.from_y).change_type(CheckerType.WHITE_QUEEN)
        elif (move.to_y == self._field.y_size - 1 and self._field.type_at(move.from_x, move.from_y) == CheckerType.BLACK_REGULAR):
            self._field.at(move.from_x, move.from_y).change_type(CheckerType.BLACK_QUEEN)

        # Изменение позиции шашки
        self._field.at(move.to_x, move.to_y).change_type(self._field.type_at(move.from_x, move.from_y))
        self._field.at(move.from_x, move.from_y).change_type(CheckerType.NONE)

        # Вектора движения
        dx = -1 if move.from_x < move.to_x else 1
        dy = -1 if move.from_y < move.to_y else 1

        # Удаление съеденных шашек
        has_captured_checked = False
        x, y = move.to_x, move.to_y
        while (x != move.from_x or y != move.from_y):
            x += dx
            y += dy
            if (self._field.type_at(x, y) != CheckerType.NONE):
                self._field.at(x, y).change_type(CheckerType.NONE)
                has_captured_checked = True

        if (draw): self.__draw()

        return has_captured_checked

    def __handle_player_turn(self, move: Move):
        '''Обработка хода игрока'''
        self.__player_turn = False

        has_killed_checker = self.__handle_move(move)
        required_moves_list = list(filter(lambda required_move: move.to_x == required_move.from_x and move.to_y == required_move.from_y, self.__get_required_moves_list(player_side)))

        if (has_killed_checker and required_moves_list):
            self.__player_turn = True

        self._selected_cell = Point()

    def __handle_enemy_turn(self):
        self.__player_turn = False

        optimal_moves_list = self.__predict_optimal_moves(SideType.opposite(player_side))

        for move in optimal_moves_list:
            self.__handle_move(move)
            
        self.__player_turn = True
        self.__check_for_game_over()

    def __check_for_game_over(self):
        '''Проверка на конец игры'''
        game_over = False

        white_moves_list = self.__get_moves_list(SideType.WHITE)
        if not (white_moves_list):
            answer = messagebox.showinfo('Конец игры', 'Белые выиграли')
            game_over = True

        black_moves_list = self.__get_moves_list(SideType.BLACK)
        if not (black_moves_list):
            answer = messagebox.showinfo('Конец игры', 'Черные выиграли')
            game_over = True

        if (game_over):
            # Новая игра
            self.__init__(self._canvas, self._field.x_size, self._field.y_size)

    def __predict_optimal_moves(self, side: SideType) -> list[Move]:
        '''Предсказать оптимальный ход'''
        best_result = 0
        optimal_moves = []
        predicted_moves_list = self.__get_predicted_moves_list(side)

        if (predicted_moves_list):
            field_copy = Field.copy(self._field)
            for moves in predicted_moves_list:
                for move in moves:
                    self.__handle_move(move, draw=False)

                try:
                    if (side == SideType.WHITE):
                        result = self._field.black_score / self._field.black_score
                    elif (side == SideType.BLACK):
                        result = self._field.white_score / self._field.black_score
                except ZeroDivisionError:
                        result = inf
                
                if (result > best_result):
                    best_result = result
                    optimal_moves.clear()
                    optimal_moves.append(moves)
                elif (result == best_result):
                    optimal_moves.append(moves)

                self._field = Field.copy(field_copy)

        optimal_move = []
        if (optimal_moves):
            # Фильтрация хода
            for move in choice(optimal_moves):
                if   (side == SideType.WHITE and self._field.type_at(move.from_x, move.from_y) in BLACK_CHECKERS): break
                elif (side == SideType.BLACK and self._field.type_at(move.from_x, move.from_y) in WHITE_CHECKERS): break

                optimal_move.append(move)

        return optimal_move

    def __get_predicted_moves_list(self, side: SideType, current_prediction_depth: int = 0, all_moves_list: list[Move] = [], current_moves_list: list[Move] = [], required_moves_list: list[Move] = []) -> list[Move]:
        '''Предсказать все возможные ходы'''

        if (current_moves_list):
            all_moves_list.append(current_moves_list)
        else:
            all_moves_list.clear()

        if (required_moves_list):
            moves_list = required_moves_list
        else:
            moves_list = self.__get_moves_list(side)

        if (moves_list and current_prediction_depth < MAX_PREDICTION_DEPTH):
            field_copy = Field.copy(self._field)
            for move in moves_list:
                has_killed_checker = self.__handle_move(move, draw=False)

                required_moves_list = list(filter(lambda required_move: move.to_x == required_move.from_x and move.to_y == required_move.from_y, self.__get_required_moves_list(side)))

                # Если есть ещё ход этой же шашкой
                if (has_killed_checker and required_moves_list):
                    self.__get_predicted_moves_list(side, current_prediction_depth, all_moves_list, current_moves_list + [move], required_moves_list)
                else:
                    self.__get_predicted_moves_list(SideType.opposite(side), current_prediction_depth + 1, all_moves_list, current_moves_list + [move])

                self._field = Field.copy(field_copy)

        return all_moves_list

    def __get_moves_list(self, side: SideType) -> list[Move]:
        '''Получение списка ходов'''
        moves_list = self.__get_required_moves_list(side)
        if not (moves_list):
            moves_list = self._get_optional_moves_list(side)
        return moves_list

    def __get_required_moves_list(self, side: SideType) -> list[Move]:
        '''Получение списка обязательных ходов'''
        moves_list = []

        # Определение типов шашек
        if (side == SideType.WHITE):
            friendly_checkers = WHITE_CHECKERS
            enemy_checkers = BLACK_CHECKERS
        elif (side == SideType.BLACK):
            friendly_checkers = BLACK_CHECKERS
            enemy_checkers = WHITE_CHECKERS
        else: return moves_list

        for y in range(self._field.y_size):
            for x in range(self._field.x_size):

                # Для обычной шашки
                if (self._field.type_at(x, y) == friendly_checkers[0]):
                    for offset in MOVE_OFFSETS:
                        if not (self._field.is_within(x + offset.x * 2, y + offset.y * 2)): continue

                        if self._field.type_at(x + offset.x, y + offset.y) in enemy_checkers and self._field.type_at(x + offset.x * 2, y + offset.y * 2) == CheckerType.NONE:
                            moves_list.append(Move(x, y, x + offset.x * 2, y + offset.y * 2))

                # Для дамки
                elif (self._field.type_at(x, y) == friendly_checkers[1]):
                    for offset in MOVE_OFFSETS:
                        if not (self._field.is_within(x + offset.x * 2, y + offset.y * 2)): continue

                        has_enemy_checker_on_way = False

                        for shift in range(1, self._field.size):
                            if not (self._field.is_within(x + offset.x * shift, y + offset.y * shift)): continue

                            if (not has_enemy_checker_on_way):
                                if (self._field.type_at(x + offset.x * shift, y + offset.y * shift) in enemy_checkers):
                                    has_enemy_checker_on_way = True
                                    continue

                                elif (self._field.type_at(x + offset.x * shift,
                                                           y + offset.y * shift) in friendly_checkers):
                                    break

                            if (has_enemy_checker_on_way):
                                if (self._field.type_at(x + offset.x * shift,
                                                         y + offset.y * shift) == CheckerType.NONE):
                                    moves_list.append(Move(x, y, x + offset.x * shift, y + offset.y * shift))
                                else:
                                    break

                                break
                            
        return moves_list

    def _get_optional_moves_list(self, side: SideType) -> list[Move]:

        moves_list = []
        # Определение типов шашек
        if (side == SideType.WHITE):
            friendly_checkers = WHITE_CHECKERS
        elif (side == SideType.BLACK):
            friendly_checkers = BLACK_CHECKERS
        else: return moves_list

        for y in range(self._field.y_size):
            for x in range(self._field.x_size):

                if (self._field.type_at(x, y) == friendly_checkers[0]):
                    for offset in MOVE_OFFSETS[:2] if side == SideType.WHITE else MOVE_OFFSETS[2:]:
                        if not (self._field.is_within(x + offset.x, y + offset.y)): continue

                        if (self._field.type_at(x + offset.x, y + offset.y) == CheckerType.NONE):
                            moves_list.append(Move(x, y, x + offset.x, y + offset.y))

                elif (self._field.type_at(x, y) == friendly_checkers[1]):
                    for offset in MOVE_OFFSETS:
                        if not (self._field.is_within(x + offset.x, y + offset.y)): continue

                        for shift in range(1, self._field.size):
                            if not (self._field.is_within(x + offset.x * shift, y + offset.y * shift)): continue

                            if (self._field.type_at(x + offset.x * shift, y + offset.y * shift) == CheckerType.NONE):
                                moves_list.append(Move(x, y, x + offset.x * shift, y + offset.y * shift))
                            else:
                                break
        return moves_list
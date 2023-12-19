from checkers.enums import CheckerType, SideType

class Point:
    def __init__(self, x: int = -1, y: int = -1):
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    def __eq__(self, other):
        if isinstance(other, Point):
            return (
                    self.x == other.x and
                    self.y == other.y
            )

        return NotImplemented

# Сторона за которую играет игрок
player_side = SideType.WHITE

# Размер поля
X_SIZE = Y_SIZE = 8
# Размер ячейки (в пикселях)
cell_size = 75

# Скорость анимации (больше = быстрее)
ANIMATION_SPEED = 20

# Количество ходов для предсказания
MAX_PREDICTION_DEPTH = 3

# Ширина рамки (Желательно должна быть чётной)
border_width = 2 * 2

# Цвета игровой доски
f_colors = ['#E7CFA9', '#927456']
# Цвет рамки при наведении на ячейку мышкой
HOVER_BORDER_COLOR = '#54b346'
# Цвет рамки при выделении ячейки
SELECT_BORDER_COLOR = '#944444'
# Цвет кружков возможных ходов
POSIBLE_MOVE_CIRCLE_COLOR = '#944444'

# Возможные смещения ходов шашек
MOVE_OFFSETS = [
    Point(-1, -1),
    Point(1, -1),
    Point(-1, 1),
    Point(1, 1)
]

# Массивы типов белых и чёрных шашек [Обычная пешка, дамка]
WHITE_CHECKERS = [CheckerType.WHITE_REGULAR, CheckerType.WHITE_QUEEN]
BLACK_CHECKERS = [CheckerType.BLACK_REGULAR, CheckerType.BLACK_QUEEN]



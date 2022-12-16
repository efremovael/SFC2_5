from random import randint
class BoardException(Exception):
    pass
class OutBoardException(BoardException):
    def __str__(self):
        return 'Вы стреляете мимо доски, скорректируйте прицел'

class BusyCellException(BoardException):
    def __str__(self):
        return 'Снаряд дважды в одну воронку не падает. Найдите другую'

class ShipIsOutBoardException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, orientation, length,):
        self.bow = bow
        self.orientation = orientation
        self.length = length
        self.lives = length

    @property
    def dots(self):
        ship_dots, x, y = [], self.bow.x, self.bow.y
        for i in range (self.length):
            if self.orientation == 0:
                ship_dots.append(Dot(x+i, y))
            else:
                ship_dots.append(Dot(x, y+i))
        return ship_dots

    def shot(self, shot_dot):
        return shot_dot in self.dots

# test
s = Ship(Dot(1, 2), 1, 3)
print(s.shot(Dot(1, 2)))


class Board:
    def __init__(self, visible = True, size = 6):
        self.visible = visible
        self.size = size
        self.cells = [["O"] * self.size for _ in range(self.size)]
        self.busy_cells = []
        self.ships = []
        self.count = 0

    def __str__(self):
        field = '   '
        for i in range(1, self.size+1):
            field += ' ' + str(i) + ' |'
        for i, j in enumerate(self.cells):
            field += f'\n{i + 1} | ' + ' | '.join(j) + ' |'
        if self.visible == False:
            field = field.replace('■', 'O')
        return field

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy_cells:
                raise ShipIsOutBoardException()
        for dot in ship.dots:
            self.cells[dot.x][dot.y] = "■"
            self.busy_cells.append(dot)
        self.ships.append(ship)
        self.area(ship)
    def out (self, dot):
        return not((0<= dot.x < self.size) and (0<= dot.y < self.size))

    def area(self, ship, ship_is_killed = False):
        area_staff_list= [[-1, 0], [0, -1], [0, 1], [0,1], [-1, -1], [1, -1], [1, 1], [-1, 1]]
        for ship_dot in ship.dots:
            for area_dot_x, area_dot_y in area_staff_list:
                cur_dot = Dot(ship_dot.x + area_dot_x, ship_dot.y + area_dot_y)
                if not self.out(cur_dot) and cur_dot not in self.busy_cells:
                    if ship_is_killed:
                        self.cells[cur_dot.x][cur_dot.y] = 'X'
                    self.busy_cells.append(cur_dot)

    def shot(self, shot_dot):
        if self.out(shot_dot):
            raise OutBoardException()
        if shot_dot in self.busy_cells:
            raise BusyCellException()
        for ship in self.ships:
            if shot_dot in ship.dots:
                self.cells[shot_dot.x][shot_dot.y] = '*'
                self.busy_cells.append(shot_dot)
                ship.lives -= 1
                if ship.lives == 0:
                    self.area(ship, ship_is_killed = True)
                    print('Корабль убит')
                    return True
                else:
                    print('Корабль ранен')
                    return True
        self.busy_cells.append(shot_dot)
        self.cells[shot_dot.x][shot_dot.y] = 'X'
        return False
    def begin(self):
        self.busy_cells = []

class Player:
    def __init__(self, player_board, enemy_board):
        self.player_board = player_board
        self.enemy_board = enemy_board
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.visible = False

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        ships_length = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        for l in ships_length:
            while True:
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1), l)
                try:
                    board.add_ship(ship)
                    break
                except ShipIsOutBoardException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Ваша доска")
            print(self.us.player_board)
            print("-" * 20)
            print("Доска компьютера")
            print(self.ai.player_board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ваш ход, ждем")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.player_board.count == 7:
                print("-" * 20)
                print("Вы выиграли!")
                break

            if self.us.player_board.count == 7:
                print("-" * 20)
                print("Вы проиграли компьютерному интеллекту")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()


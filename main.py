import random
import curses

class RabbitGame:
    def __init__(self, stdscr, map_size, num_carrots, num_rabbit_holes):
        self.stdscr = stdscr
        self.map_size = map_size
        self.num_carrots = num_carrots
        self.num_rabbit_holes = num_rabbit_holes
        self.map = []
        self.rabbit_pos = None
        self.carrot_pos = []
        self.rabbit_hole_pos = []
        self.carrot_held = False

    def generate_map(self):
        self.map = [['-' for _ in range(self.map_size)] for _ in range(self.map_size)]
        self.rabbit_pos = (random.randint(0, self.map_size - 1), random.randint(0, self.map_size - 1))
        self.map[self.rabbit_pos[0]][self.rabbit_pos[1]] = 'r'
        for _ in range(self.num_carrots):
            while True:
                x, y = random.randint(0, self.map_size - 1), random.randint(0, self.map_size - 1)
                if self.map[x][y] == '-':
                    self.map[x][y] = 'c'
                    self.carrot_pos.append((x, y))
                    break

        for _ in range(self.num_rabbit_holes):
            while True:
                x, y = random.randint(0, self.map_size - 1), random.randint(0, self.map_size - 1)
                if self.map[x][y] == '-':
                    self.map[x][y] = 'O'
                    self.rabbit_hole_pos.append((x, y))
                    break

    def display_map(self):
        self.stdscr.clear()
        for row in range(self.map_size):
            for col in range(self.map_size):
                self.stdscr.addch(row, col, self.map[row][col])
        self.stdscr.addstr(self.map_size + 1, 0, "Use 'w', 'a', 's', 'd' to move, 'p' to pick up carrots, 'j' to jump over holes, and 'q' to quit.")
        self.stdscr.refresh()

    def move_rabbit(self, direction):
        dx, dy = 0, 0

        if direction == 'w':
            dx = -1
        elif direction == 's':
            dx = 1
        elif direction == 'a':
            dy = -1
        elif direction == 'd':
            dy = 1
        elif direction == 'wa':
            dx = -1
            dy = -1
        elif direction == 'wd':
            dx = -1
            dy = 1
        elif direction == 'sa':
            dx = 1
            dy = -1
        elif direction == 'sd':
            dx = 1
            dy = 1

        new_x, new_y = self.rabbit_pos[0] + dx, self.rabbit_pos[1] + dy

        if (
            0 <= new_x < self.map_size
            and 0 <= new_y < self.map_size
            and (new_x, new_y) not in self.rabbit_hole_pos
        ):
            if self.map[new_x][new_y] == '-':
                if self.carrot_held:
                    self.map[self.rabbit_pos[0]][self.rabbit_pos[1]] = '-'
                    self.rabbit_pos = (new_x, new_y)
                    self.map[new_x][new_y] = 'R'
                else:
                    self.map[self.rabbit_pos[0]][self.rabbit_pos[1]] = '-'
                    self.rabbit_pos = (new_x, new_y)
                    self.map[new_x][new_y] = 'r'
            elif self.map[new_x][new_y] == 'c':
                self.stdscr.addstr(self.map_size + 2, 0, "You need to pick up the carrot ('p') first!")
            elif self.map[new_x][new_y] == 'O':
                self.stdscr.addstr(self.map_size + 2, 0, "You cannot move across a rabbit hole. Press 'j' to jump.")
        else:
            self.stdscr.addstr(self.map_size + 2, 0, "Invalid move!")


    def jump_over_hole(self):
        hole_found = False
        for x, y in self.rabbit_hole_pos:
            if (
                abs(x - self.rabbit_pos[0]) <= 1
                and abs(y - self.rabbit_pos[1]) <= 1
                and not (x == self.rabbit_pos[0] and y == self.rabbit_pos[1])
            ):
                hole_found = True
                if self.rabbit_pos[0] == x:
                    if self.rabbit_pos[1] < y:
                        new_x, new_y = x, y + 1
                    else:
                        new_x, new_y = x, y - 1
                else:
                    if self.rabbit_pos[0] < x:
                        new_x, new_y = x + 1, y
                    else:
                        new_x, new_y = x - 1, y

                if (
                    0 <= new_x < self.map_size
                    and 0 <= new_y < self.map_size
                    and self.map[new_x][new_y] == 'c'
                ):
                    self.carrot_held = True
                    self.map[new_x][new_y] = '-'

                if (
                    0 <= new_x < self.map_size
                    and 0 <= new_y < self.map_size
                ):
                    self.map[self.rabbit_pos[0]][self.rabbit_pos[1]] = '-'
                    self.rabbit_pos = (new_x, new_y)
                    self.map[new_x][new_y] = 'r'
                    break

        if not hole_found:
            self.stdscr.addstr(self.map_size + 2, 0, "No hole nearby!")



    def pick_up_carrot(self):
        if self.carrot_held:
            for x, y in self.rabbit_hole_pos:
                if (
                    abs(x - self.rabbit_pos[0]) <= 1
                    and abs(y - self.rabbit_pos[1]) <= 1
                    and self.map[x][y] == 'O'
                ):
                    self.stdscr.addstr(self.map_size + 2, 0, "You dropped the carrot in a hole. You win!")
                    print("You dropped the carrot in a hole. You win!")
                    self.stdscr.refresh()
                    return True
            self.stdscr.addstr(self.map_size + 2, 0, "You already have a carrot!")
        else:
            for x, y in self.carrot_pos:
                if (
                    abs(x - self.rabbit_pos[0]) <= 1
                    and abs(y - self.rabbit_pos[1]) <= 1
                    and self.map[x][y] == 'c'
                ):
                    self.carrot_held = True
                    self.map[x][y] = '-'
                    self.stdscr.addstr(self.map_size + 2, 0, "Carrot picked up!")
                    return False
            self.stdscr.addstr(self.map_size + 2, 0, "No carrot nearby!")

    def run_game(self):
        curses.curs_set(0)  # Hide the cursor
        self.generate_map()
        while True:
            self.display_map()
            user_input = self.stdscr.getch()
            if user_input == ord('q'):
                self.stdscr.addstr(self.map_size + 2, 0, "You quit the game.")
                self.stdscr.refresh()
                break
            elif user_input in (ord('w'), ord('s'), ord('a'), ord('d')):
                self.move_rabbit(chr(user_input))
            elif user_input == ord('p'):
                if self.pick_up_carrot():
                    break
            elif user_input == ord('j'):
                self.jump_over_hole()
            else:
                self.stdscr.addstr(self.map_size + 2, 0, "Invalid input!")
            self.stdscr.refresh()

if __name__ == "__main__":
    map_size = int(input("Enter map size: "))
    num_carrots = int(input("Enter the number of carrots: "))
    num_rabbit_holes = int(input("Enter the number of rabbit holes: "))
    curses.wrapper(lambda stdscr: RabbitGame(stdscr, map_size, num_carrots, num_rabbit_holes).run_game())

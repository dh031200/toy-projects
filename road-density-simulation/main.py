from random import random, randint
from time import time
import cv2
import numpy as np

# CONFIG
# Grid 1 : 0.41mm Read-world

RANDOM_EPSILON = 0.1
GENERATE_FREQUENCY = 0.6
STOP_EPSILON = 0.2
RIGHT_SIDE_WALK = True

FRAME_SPEED = 4
VIS_SCALE = 20
STUCK_LINE_LIMIT = 6
END_COUNT = 1
VISUALIZE = True

X = 80
Y = 12
WALL_WIDTH = 12
WALL_HEIGHT = 5

VIS_COLOR = (0, (255, 0, 0), (0, 255, 0)) # 1번, 2번 인덱스 사용
WALL_COLOR = (150, 150, 150)
STUCK_COLOR = (0, 0, 255)
BORDER = (20, 20, 20)
TXT_COLOR = (255, 255, 255)


ELAPSED_COUNT = 0
ID = 1


def coord_to_canvas(coord):
    return coord[0] * VIS_SCALE + VIS_SCALE // 2, coord[1] * VIS_SCALE + VIS_SCALE // 2


def reset_canvas():
    return np.full((Y * VIS_SCALE, X * VIS_SCALE, 3), (0, 0, 0), dtype=np.uint8)


class Board:
    def __init__(self):
        self.board = np.zeros((Y, X), dtype=int)
        self.stucked = []

        canvas = np.full((VIS_SCALE * Y + 180, VIS_SCALE * X, 3), (0, 0, 0), dtype=np.uint8)
        for x in range(X):
            cv2.line(canvas, (x * VIS_SCALE, 0), (x * VIS_SCALE, VIS_SCALE * Y), BORDER)
            cv2.line(canvas, (x * VIS_SCALE + VIS_SCALE - 1, 0), (x * VIS_SCALE + VIS_SCALE - 1, VIS_SCALE * Y),
                     BORDER)
        for y in range(Y):
            cv2.line(canvas, (0, y * VIS_SCALE + VIS_SCALE - 1), (VIS_SCALE * X, y * VIS_SCALE + VIS_SCALE - 1),
                     BORDER)
            cv2.line(canvas, (0, y * VIS_SCALE), (VIS_SCALE * X, y * VIS_SCALE), BORDER)

        # Init wall
        if WALL_HEIGHT > 0 and WALL_WIDTH > 0:
            self.board[:WALL_HEIGHT, -WALL_WIDTH:] = -1
            canvas[:WALL_HEIGHT * VIS_SCALE, -WALL_WIDTH * VIS_SCALE:] = WALL_COLOR
            cv2.putText(canvas, 'WALL',
                        ((X - WALL_WIDTH + int(WALL_WIDTH * 0.4)) * VIS_SCALE, WALL_HEIGHT * VIS_SCALE // 2 - 15),
                        cv2.FONT_HERSHEY_TRIPLEX, 0.8,
                        TXT_COLOR)
            cv2.putText(canvas, f'Width : {WALL_WIDTH * 0.41:.1f}m',
                        ((X - WALL_WIDTH + int(WALL_WIDTH * 0.2)) * VIS_SCALE, WALL_HEIGHT * VIS_SCALE // 2 + 10),
                        cv2.FONT_HERSHEY_TRIPLEX, 0.7,
                        TXT_COLOR)
            cv2.putText(canvas, f'Height : {WALL_HEIGHT * 0.41:.1f}m',
                        ((X - WALL_WIDTH + int(WALL_WIDTH * 0.2)) * VIS_SCALE, WALL_HEIGHT * VIS_SCALE // 2 + 30),
                        cv2.FONT_HERSHEY_TRIPLEX, 0.7,
                        TXT_COLOR)

        self.canvas = canvas

    def check(self):
        self.stucked = []
        r = False
        for l in range(X):
            if self.board[:, l].all() != 0:
                self.stucked.append(l)

            if l < X - STUCK_LINE_LIMIT and self.board[:, l:l + STUCK_LINE_LIMIT].all() != 0:
                r = True

        return r

    def count(self):
        return np.count_nonzero(self.board) - WALL_WIDTH * WALL_HEIGHT


class Agent:
    def __init__(self, a_id, epsilon=RANDOM_EPSILON):
        self.id = a_id
        self.direction = d if (d := randint(0, 1)) else -1
        self.epsilon = epsilon
        self.coord = [randint(1, Y - 1), (X - 1) * (not d)]
        self.term = randint(2, 5)
        self.interval = 0
        self.active = True
        self.speed = [0] * 10
        self.speed_idx = 0
        self.stop_time = 0

    def calc(self):
        if random() < STOP_EPSILON:
            return self.coord[0], self.coord[1]
        new_y = self.coord[0]
        if random() < self.epsilon and 0 <= (z := self.coord[0] + (1 if randint(0, 1) else -1)) < Y:
            new_y = z
        new_x = self.coord[1] + self.direction

        return new_y, new_x

    def move(self, _y, _x):
        self.coord[0] = _y
        self.coord[1] = _x


class AgentPool:
    def __init__(self, board):
        self.pool = []
        self.board = board.board
        self.In = 0
        self.Out = 0

    def append(self, _agent):
        self.pool.append(_agent)

    def tic(self):
        global ID
        if random() < GENERATE_FREQUENCY:
            for _ in range(randint(1, 3)):
                agent = Agent(ID)
                y, x = agent.coord
                if not self.board[y][x]:
                    self.board[y][x] = ID
                    self.append(agent)
                    self.In += 1
                    ID += 1

        for agent in self.pool:
            agent.interval += 1
            if agent.interval >= agent.term:
                if agent.interval > agent.term:
                    agent.epsilon += 0.4
                y, x = agent.calc()
                if 0 <= x < X:
                    if self.board[y][x] == -1 and agent.epsilon > 0.5:
                        y += 1
                        x = agent.coord[1]
                    elif x + agent.direction < X and self.board[y][x + agent.direction] == -1:
                        y += 1
                    elif x + (agent.direction * 2) < X and self.board[y][x + (agent.direction * 2)] == -1:
                        y += 1
                    elif x + (agent.direction * 3) < X and self.board[y][x + (agent.direction * 3)] == -1:
                        y += 1
                    elif x + (agent.direction * 4) < X and self.board[y][x + (agent.direction * 4)] == -1:
                        y += 1
                    elif self.board[y][x] and random() < (2 * agent.epsilon):
                        if RIGHT_SIDE_WALK and 0 <= (z := y + agent.direction) < Y:
                            y=z
                        elif 0 <= (z := y + (1 if randint(0, 1) else -1)) < Y:
                            y=z
                    # elif x + agent.direction < X and self.board[y][x + agent.direction] != 0:
                    # elif self.board[y][x] and random() < (2 * agent.epsilon) and 0 <= (z := y + agent.direction) < Y:
                    #     y = z
                    # elif self.board[y][x] and random() < (2 * agent.epsilon) and 0 <= (z := y + (1 if randint(0, 1) else -1)) < Y:
                    #     y = z
                    if not self.board[y][x]:
                        old_y, old_x = agent.coord
                        self.board[old_y][old_x] = 0
                        agent.move(y, x)
                        agent.speed[agent.speed_idx] = 1
                        self.board[y][x] = agent.id
                        agent.interval = 0
                        agent.epsilon = RANDOM_EPSILON
                    else:
                        agent.speed[agent.speed_idx] = 0
                    agent.speed_idx = (agent.speed_idx + 1) % 10
                else:
                    self.Out += 1
                    y, x = agent.coord
                    agent.active = False
                    self.board[y][x] = 0
        self.pool = [a for a in self.pool if a.active]

    def __len__(self):
        return len(self.pool)


def draw(_pool, _board):
    canvas = _board.canvas.copy()
    speed_left_cluster = 0
    speed_right_cluster = 0
    count_left = 0
    count_right = 0
    speed = 0

    for s in _board.stucked:
        if _board.board[0, s] == -1:
            offset = WALL_HEIGHT
        else:
            offset = 0
        cv2.rectangle(canvas, (s * VIS_SCALE, offset * VIS_SCALE),
                      ((s + 1) * VIS_SCALE, VIS_SCALE * Y),
                      STUCK_COLOR, -1)

    for agent in _pool.pool:
        if agent.direction > 0:
            speed_left_cluster += 1 / agent.term * (0.5 if agent.interval else 1)
            count_left += 1
        else:
            speed_right_cluster += 1 / agent.term * (0.5 if agent.interval else 1)
            count_right += 1
        speed += sum(agent.speed)
        _y, _x = coord_to_canvas(agent.coord)
        cv2.circle(canvas, (_x, _y), VIS_SCALE // 3, VIS_COLOR[agent.direction], -1)

    total_count = count_left + count_right
    cv2.putText(canvas, f'Count', (20, Y * VIS_SCALE + 40),
                cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)
    cv2.putText(canvas, f'Left  : {count_left}',
                (20, Y * VIS_SCALE + 80), cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)
    cv2.putText(canvas, f'Right : {count_right}', (20, Y * VIS_SCALE + 120), cv2.FONT_HERSHEY_TRIPLEX, 1,
                TXT_COLOR)
    cv2.putText(canvas, f'Total : {total_count}', (20, Y * VIS_SCALE + 160), cv2.FONT_HERSHEY_TRIPLEX, 1,
                TXT_COLOR)
    try:
        io_ratio = _pool.In / _pool.Out
    except:
        io_ratio = 0

    if count_left > 0 and count_right > 0:
        cv2.putText(canvas, f'Cluster velocity', (240, Y * VIS_SCALE + 40), cv2.FONT_HERSHEY_TRIPLEX, 1,
                    TXT_COLOR)
        cv2.putText(canvas, f'Left  : {speed_left_cluster / count_left * (speed / total_count):.2f}',
                    (240, Y * VIS_SCALE + 80),
                    cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)
        cv2.putText(canvas, f'Right : {speed_right_cluster / count_right * (speed / total_count):.2f}',
                    (240, Y * VIS_SCALE + 120),
                    cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)
        cv2.putText(canvas, f'I/O ratio : {io_ratio:.1f}',
                    (240, Y * VIS_SCALE + 160),
                    cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)

    cv2.putText(canvas, f'Width : {X * 0.41}m', (550, Y * VIS_SCALE + 40), cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)
    cv2.putText(canvas, f'Height : {Y * 0.41}m', (550, Y * VIS_SCALE + 80), cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)
    cv2.putText(canvas, f'Input-likelihood(sec) : {GENERATE_FREQUENCY * 2 * 10}', (550, Y * VIS_SCALE + 120),
                cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)
    # cv2.putText(canvas, f'Simulator Speed : x{100 / FRAME_SPEED:.0f}', (550, Y * VIS_SCALE + 160),
    #             cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)
    cv2.putText(canvas, f'Simulator Speed : x3', (550, Y * VIS_SCALE + 160),
                cv2.FONT_HERSHEY_TRIPLEX, 1, TXT_COLOR)

    cv2.putText(canvas, f'Elapsed time(sec) : {ELAPSED_COUNT / 10:.1f}', (1100, Y * VIS_SCALE + 40),
                cv2.FONT_HERSHEY_TRIPLEX,
                1, TXT_COLOR)
    if total_count > 0:
        occupancy = (X * 0.41 * Y * 0.41) / total_count
        walking_rate = total_count * 60 / X * 0.41
        if occupancy >= 3.5 and walking_rate <= 20:
            los = 'A'
        elif occupancy > 2.5 and walking_rate < 30:
            los = 'B'
        elif occupancy > 1.5 and walking_rate < 45:
            los = 'C'
        elif occupancy > 1.0 and walking_rate < 60:
            los = 'D'
        elif occupancy > 0.5 and walking_rate < 80:
            los = 'E'
        else:
            los = 'F'

        cv2.putText(canvas, f'Walking rate : {walking_rate:.1f}', (1100, Y * VIS_SCALE + 80),
                    cv2.FONT_HERSHEY_TRIPLEX,
                    1, TXT_COLOR)
        cv2.putText(canvas, f'Walking Occupancy : {occupancy:.2f}', (1100, Y * VIS_SCALE + 120),
                    cv2.FONT_HERSHEY_TRIPLEX,
                    1, TXT_COLOR)
        cv2.putText(canvas, f'Level Of Service : {los}', (1100, Y * VIS_SCALE + 160),
                    cv2.FONT_HERSHEY_TRIPLEX,
                    1, TXT_COLOR)
    return canvas


def main():
    global END_COUNT
    global ELAPSED_COUNT
    board = Board()
    agent_pool = AgentPool(board=board)
    vid_writer = cv2.VideoWriter('result.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, board.canvas.shape[:2][::-1])
    start_time = time()
    while True:
        ELAPSED_COUNT += 1
        if board.check():
            END_COUNT -= 1
        if END_COUNT < 0:
            break
        if VISUALIZE:
            vis = draw(agent_pool, board)
            if cv2.waitKey(FRAME_SPEED) & 0xFF == ord('q'):
                break
            cv2.imshow('canvas', vis)
            vid_writer.write(vis)
        agent_pool.tic()
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    vid_writer.release()
    elapsed_time = time() - start_time
    print(f'Elapsed time : {elapsed_time}')
    print(f'Count : {ELAPSED_COUNT}')


if __name__ == '__main__':
    main()

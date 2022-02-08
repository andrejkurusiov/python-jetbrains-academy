"""Tic-tac-toe game implementation"""

# Game grid from initial input

X_LEN = 9  # length of field with all borders
ROW_LEN = 3  # length of a row
GAME_STATE_CODES = {-1: 'Impossible', 0: 'Game not finished', 1: 'X wins', 2: 'O wins', 3: 'Draw'}


def create_matrix() -> list[list]:
    """Input game data, return game matrix
    """
    game_matrix = []
    initial_grid = '_' * X_LEN  # input('Enter cells: ')
    # form game matrix of '_'s, 'X's and 'O's, 3x3
    for i in range(0, X_LEN, ROW_LEN):
        row = []
        for j in range(i, i + ROW_LEN):
            row.append(initial_grid[j])
        game_matrix.append(row)
    return game_matrix


def print_gamefield(game_matrix: list) -> None:
    """Print game matrix with borders and spaces around values
    """
    # print game field with borders
    print('-' * X_LEN)
    for row in game_matrix:
        print('| ' + ' '.join(row) + ' |')
    print('-' * X_LEN)


def has_three(game_matrix: list, symbol: str) -> bool:
    """Whether player with 'symbol' ('X' or 'O') has 3 rows/columns/diagonal full.
    """
    for i in range(ROW_LEN):
        # check columns
        if game_matrix[0][i] == game_matrix[1][i] == game_matrix[2][i] == symbol:
            return True
        # check rows
        if game_matrix[i] == symbol * ROW_LEN:
            return True
    # check diagonals
    if game_matrix[0][0] == game_matrix[1][1] == game_matrix[2][2] == symbol or \
            game_matrix[0][2] == game_matrix[1][1] == game_matrix[2][0] == symbol:
        return True
    return False


def xo_diff_correct(game_matrix: list) -> bool:
    """Return True if X's and O's difference 0 or 1; otherwise return False."""
    x, o = 0, 0
    for row in game_matrix:
        x += row.count('X')
        o += row.count('O')
    return abs(x - o) <= 1


def no_empty_cells(game_matrix: list) -> bool:
    """Return True is game field has no empty cells ('_'); otherwise False."""
    for row in game_matrix:
        if row.count('_') > 0:
            return False
    return True


def get_game_state(game_matrix: list) -> int:
    """Analyse game state and return possible result:
    Game not finished when neither side has three in a row but the grid still has empty cells.
    Draw when no side has a three in a row and the grid has no empty cells.
    X wins when the grid has three X’s in a row.
    O wins when the grid has three O’s in a row.
    Impossible  when the grid has three X’s in a row as well as three O’s in a row,
                or there are a lot more X's than O's or vice versa
                (the difference should be 1 or 0; if the difference is 2 or more, then the game state is impossible).
    Result encoding according to GAME_STATE_CODES.
    """
    x_three = has_three(game_matrix, 'X')
    o_three = has_three(game_matrix, 'O')
    xo_diff_ok = xo_diff_correct(game_matrix)
    no_empty = no_empty_cells(game_matrix)
    if (x_three and o_three) or not xo_diff_ok:
        return -1  # 'Impossible'
    elif x_three:
        return 1  # 'X wins'
    elif o_three:
        return 2  # 'O wins'
    elif no_empty:
        return 3  # 'Draw'
    else:
        return 0  # 'Game not finished'


def get_user_move(matrix: list) -> tuple[int, int]:
    """Prompts for user input as coordinates and returns coordinated where to place a player mark.
    """
    while True:
        user_input = input('Enter the coordinates: ')
        try:
            n1, n2 = (int(x) for x in user_input.split())
        except ValueError:
            print('You should enter numbers!')
            continue
        # print(n1, n2)
        if (n1 not in range(1, ROW_LEN + 1)) or (n2 not in range(1, ROW_LEN + 1)):
            print('Coordinates should be from 1 to 3!')
            continue
        if matrix[n1 - 1][n2 - 1] in 'XO':
            print('This cell is occupied! Choose another one!')
            continue
        # if no errors, return the coordinates in [0, 2] range as defined in game matrix
        return n1 - 1, n2 - 1


if __name__ == '__main__':
    """The first player has to play as X and their opponent plays as O."""
    matrix = create_matrix()  # 3x3 game matrix with starting index 0
    print_gamefield(matrix)
    game_state = 0
    # start playing from 'X' player
    player = 'X'
    while game_state == 0:
        row, column = get_user_move(matrix)  # check if user input is correct and obtain coordinates
        matrix[row][column] = player  # make move
        print_gamefield(matrix)
        game_state = get_game_state(matrix)
        player = 'O' if player == 'X' else 'X'  # change player 'X' <-> 'O'
    print(GAME_STATE_CODES.get(game_state))

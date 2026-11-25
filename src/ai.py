import copy
import random

from const import ROWS, COLS
from piece import Pawn, Knight, Bishop, Rook, Queen, King

# Piece-square tables from white's point of view (row 0 = black's back rank).
# Black reads them mirrored. Values are in pawns.
PAWN_T = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [.5, .5, .5, .5, .5, .5, .5, .5],
    [.1, .1, .2, .3, .3, .2, .1, .1],
    [.05, .05, .1, .25, .25, .1, .05, .05],
    [0, 0, 0, .2, .2, 0, 0, 0],
    [.05, -.05, -.1, 0, 0, -.1, -.05, .05],
    [.05, .1, .1, -.2, -.2, .1, .1, .05],
    [0, 0, 0, 0, 0, 0, 0, 0],
]
KNIGHT_T = [
    [-.5, -.4, -.3, -.3, -.3, -.3, -.4, -.5],
    [-.4, -.2, 0, 0, 0, 0, -.2, -.4],
    [-.3, 0, .1, .15, .15, .1, 0, -.3],
    [-.3, .05, .15, .2, .2, .15, .05, -.3],
    [-.3, 0, .15, .2, .2, .15, 0, -.3],
    [-.3, .05, .1, .15, .15, .1, .05, -.3],
    [-.4, -.2, 0, .05, .05, 0, -.2, -.4],
    [-.5, -.4, -.3, -.3, -.3, -.3, -.4, -.5],
]
CENTER_T = [[.1 - .03 * (abs(3.5 - r) + abs(3.5 - c)) for c in range(8)] for r in range(8)]
KING_T = [
    [-.3, -.4, -.4, -.5, -.5, -.4, -.4, -.3],
    [-.3, -.4, -.4, -.5, -.5, -.4, -.4, -.3],
    [-.3, -.4, -.4, -.5, -.5, -.4, -.4, -.3],
    [-.3, -.4, -.4, -.5, -.5, -.4, -.4, -.3],
    [-.2, -.3, -.3, -.4, -.4, -.3, -.3, -.2],
    [-.1, -.2, -.2, -.2, -.2, -.2, -.2, -.1],
    [.2, .2, 0, 0, 0, 0, .2, .2],
    [.2, .3, .1, 0, 0, .1, .3, .2],
]


def _positional(piece, row, col):
    r = row if piece.color == 'white' else 7 - row
    if isinstance(piece, Pawn):
        return PAWN_T[r][col]
    if isinstance(piece, Knight):
        return KNIGHT_T[r][col]
    if isinstance(piece, King):
        return KING_T[r][col]
    return CENTER_T[r][col]


def evaluate(board):
    """Positive favours white, negative favours black."""
    score = 0.0
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.squares[row][col].piece
            if piece is None:
                continue
            sign = 1 if piece.color == 'white' else -1
            score += piece.value + sign * _positional(piece, row, col)
    return score


def _moves(board, color, legal):
    """All (row, col, move) for color. legal=True filters moves that leave the king in check."""
    out = []
    for row in range(ROWS):
        for col in range(COLS):
            sq = board.squares[row][col]
            if sq.has_team_piece(color):
                piece = sq.piece
                piece.clear_moves()
                board.calc_moves(piece, row, col, bool=legal)
                for m in piece.moves:
                    out.append((row, col, m))
                piece.clear_moves()
    # castling generation adds moves to rooks after they were cleared; reset everything
    for row in range(ROWS):
        for col in range(COLS):
            if board.squares[row][col].has_piece():
                board.squares[row][col].piece.clear_moves()
    # captures first: better alpha-beta pruning
    out.sort(key=lambda t: -(abs(t[2].final.piece.value) if t[2].final.piece else 0))
    return out


def _apply(board, row, col, move):
    child = copy.deepcopy(board)
    piece = child.squares[row][col].piece
    child.move(piece, move, testing=True)
    return child


def _search(board, color, depth, alpha, beta):
    if depth == 0:
        return evaluate(board)
    moves = _moves(board, color, legal=False)
    if not moves:
        return evaluate(board)
    other = 'black' if color == 'white' else 'white'
    if color == 'white':
        best = float('-inf')
        for row, col, m in moves:
            if isinstance(m.final.piece, King):
                return 10000
            best = max(best, _search(_apply(board, row, col, m), other, depth - 1, alpha, beta))
            alpha = max(alpha, best)
            if alpha >= beta:
                break
        return best
    best = float('inf')
    for row, col, m in moves:
        if isinstance(m.final.piece, King):
            return -10000
        best = min(best, _search(_apply(board, row, col, m), other, depth - 1, alpha, beta))
        beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def legal_moves(board, color):
    return _moves(board, color, legal=True)


def best_move(board, color, depth=2):
    """Pick a move for color with alpha-beta search. Returns (row, col, move) or None."""
    moves = legal_moves(board, color)
    if not moves:
        return None
    random.shuffle(moves)  # vary play between equal moves
    moves.sort(key=lambda t: -(abs(t[2].final.piece.value) if t[2].final.piece else 0))
    other = 'black' if color == 'white' else 'white'
    best, best_score = moves[0], None
    alpha, beta = float('-inf'), float('inf')
    for row, col, m in moves:
        score = _search(_apply(board, row, col, m), other, depth - 1, alpha, beta)
        if color == 'white' and (best_score is None or score > best_score):
            best, best_score = (row, col, m), score
            alpha = max(alpha, score)
        elif color == 'black' and (best_score is None or score < best_score):
            best, best_score = (row, col, m), score
            beta = min(beta, score)
    return best

import pygame

from const import *
from board import Board
from dragger import Dragger
from config import Config
from square import Square
import ai

class Game:

    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.ai_enabled = False
        self.status = None

    # blit methods

    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                # color
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                # rect
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

                # row coordinates
                if col == 0:
                    # color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 7:
                    # color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    # label
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                # piece ?
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    # all pieces except dragger piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all valid moves
            for move in piece.moves:
                # color
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                # rect
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                # color
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                # rect
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                # blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            # color
            color = (180, 180, 180)
            # rect
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    # other methods

    def next_turn(self):
        self.next_player = 'white' if self.next_player == 'black' else 'black'

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        ai_enabled = self.ai_enabled
        self.__init__()
        self.ai_enabled = ai_enabled

    # ai and game state

    def toggle_ai(self):
        self.ai_enabled = not self.ai_enabled

    def ai_turn(self):
        """Let the computer play one move for the side to move."""
        choice = ai.best_move(self.board, self.next_player)
        if choice is None:
            return
        row, col, _ = choice
        piece = self.board.squares[row][col].piece
        piece.clear_moves()
        self.board.calc_moves(piece, row, col, bool=True)
        move = next(m for m in piece.moves if m == choice[2])
        captured = self.board.squares[move.final.row][move.final.col].has_piece()
        self.board.move(piece, move)
        self.board.set_true_en_passant(piece)
        self.play_sound(captured)
        self.next_turn()

    def update_status(self):
        """Detect checkmate or stalemate for the side to move."""
        if ai.legal_moves(self.board, self.next_player):
            self.status = None
            return
        if self.board.king_attacked(self.next_player):
            winner = 'White' if self.next_player == 'black' else 'Black'
            self.status = f'Checkmate - {winner} wins'
        else:
            self.status = 'Stalemate'

    def show_status(self, surface):
        mode = 'vs AI' if self.ai_enabled else '2 players'
        lbl = self.config.font.render(f'{mode}  (a: toggle AI)', 1, (40, 40, 40))
        surface.blit(lbl, (WIDTH - lbl.get_width() - 8, 6))
        if self.status:
            big = pygame.font.SysFont('monospace', 40, bold=True)
            text = big.render(self.status, 1, (255, 255, 255))
            box = text.get_rect(center=(WIDTH // 2, HEIGHT // 2)).inflate(40, 30)
            overlay = pygame.Surface(box.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            surface.blit(overlay, box)
            surface.blit(text, text.get_rect(center=box.center))
            hint = self.config.font.render('press r to restart', 1, (230, 230, 230))
            surface.blit(hint, hint.get_rect(center=(WIDTH // 2, box.bottom + 18)))
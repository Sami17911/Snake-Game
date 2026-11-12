import random
import sys

import pygame


pygame.init()

WIDTH = 1000
HEIGHT = 700
CELL_SIZE = 24
BOARD_COLUMNS = 26
BOARD_ROWS = 22
BOARD_X = 36
BOARD_Y = 104
BOARD_WIDTH = BOARD_COLUMNS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE
PANEL_X = 700
FPS = 60
START_SPEED = 0.14
MIN_SPEED = 0.065

COLORS = {
	"background": (17, 25, 28),
	"surface": (25, 36, 39),
	"surface_light": (34, 48, 50),
	"grid": (39, 53, 54),
	"text": (236, 240, 226),
	"muted": (145, 163, 153),
	"green": (167, 215, 113),
	"green_dark": (100, 151, 82),
	"coral": (240, 126, 101),
	"gold": (242, 194, 99),
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE / FIELD NOTES")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("segoeui", 16)
font_body = pygame.font.SysFont("segoeui", 20)
font_heading = pygame.font.SysFont("segoeui", 30, bold=True)
font_title = pygame.font.SysFont("segoeui", 48, bold=True)
font_score = pygame.font.SysFont("segoeui", 42, bold=True)


def draw_text(text, font, color, position, center=False):
	image = font.render(text, True, color)
	rect = image.get_rect()
	if center:
		rect.center = position
	else:
		rect.topleft = position
	screen.blit(image, rect)
	return rect


def new_food(snake):
	available = [
		(column, row)
		for column in range(BOARD_COLUMNS)
		for row in range(BOARD_ROWS)
		if (column, row) not in snake
	]
	return random.choice(available) if available else None


def reset_game():
	center_column = BOARD_COLUMNS // 2
	center_row = BOARD_ROWS // 2
	snake = [(center_column - offset, center_row) for offset in range(4)]
	return snake, (1, 0), (1, 0), new_food(snake), 0


def cell_rect(position, inset=2):
	column, row = position
	return pygame.Rect(
		BOARD_X + column * CELL_SIZE + inset,
		BOARD_Y + row * CELL_SIZE + inset,
		CELL_SIZE - inset * 2,
		CELL_SIZE - inset * 2,
	)


def draw_board(snake, food):
	board = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
	pygame.draw.rect(screen, COLORS["surface"], board, border_radius=8)
	for column in range(1, BOARD_COLUMNS):
		x = BOARD_X + column * CELL_SIZE
		pygame.draw.line(screen, COLORS["grid"], (x, BOARD_Y), (x, BOARD_Y + BOARD_HEIGHT))
	for row in range(1, BOARD_ROWS):
		y = BOARD_Y + row * CELL_SIZE
		pygame.draw.line(screen, COLORS["grid"], (BOARD_X, y), (BOARD_X + BOARD_WIDTH, y))

	if food is not None:
		food_rect = cell_rect(food, 5)
		pygame.draw.circle(screen, COLORS["coral"], food_rect.center, CELL_SIZE // 2 - 4)
		pygame.draw.circle(screen, (255, 207, 177), (food_rect.centerx - 2, food_rect.centery - 3), 2)

	for index, segment in enumerate(reversed(snake)):
		color = COLORS["green_dark"] if index == 0 and len(snake) > 1 else COLORS["green"]
		pygame.draw.rect(screen, color, cell_rect(segment), border_radius=6)

	if snake:
		head_rect = cell_rect(snake[0], 2)
		eye_color = COLORS["background"]
		if abs(direction[0]) > abs(direction[1]):
			eye_x = head_rect.centerx + direction[0] * 5
			pygame.draw.circle(screen, eye_color, (eye_x, head_rect.centery - 4), 2)
			pygame.draw.circle(screen, eye_color, (eye_x, head_rect.centery + 4), 2)
		else:
			eye_y = head_rect.centery + direction[1] * 5
			pygame.draw.circle(screen, eye_color, (head_rect.centerx - 4, eye_y), 2)
			pygame.draw.circle(screen, eye_color, (head_rect.centerx + 4, eye_y), 2)


def draw_hud(score, best_score):
	draw_text("SNAKE", font_heading, COLORS["text"], (36, 32))
	draw_text("FIELD NOTES  /  01", font_small, COLORS["muted"], (PANEL_X, 43))
	pygame.draw.line(screen, COLORS["surface_light"], (36, 80), (964, 80), 1)

	draw_text("CURRENT RUN", font_small, COLORS["muted"], (PANEL_X, 116))
	draw_text(f"{score:03d}", font_score, COLORS["text"], (PANEL_X, 137))
	pygame.draw.line(screen, COLORS["surface_light"], (PANEL_X, 202), (964, 202), 1)

	draw_text("SESSION BEST", font_small, COLORS["muted"], (PANEL_X, 224))
	draw_text(f"{best_score:03d}", font_heading, COLORS["green"], (PANEL_X, 248))

	draw_text("HOW TO PLAY", font_small, COLORS["muted"], (PANEL_X, 318))
	draw_text("Move", font_body, COLORS["text"], (PANEL_X, 349))
	draw_text("ARROWS  /  WASD", font_small, COLORS["muted"], (PANEL_X, 377))
	draw_text("Pause", font_body, COLORS["text"], (PANEL_X, 417))
	draw_text("SPACE  /  P", font_small, COLORS["muted"], (PANEL_X, 445))
	draw_text("Restart", font_body, COLORS["text"], (PANEL_X, 485))
	draw_text("ENTER", font_small, COLORS["muted"], (PANEL_X, 513))
	draw_text("Collect. Grow. Don't collide.", font_small, COLORS["muted"], (PANEL_X, 615))


def draw_button(label, rect, hovered):
	fill = COLORS["green"] if hovered else COLORS["green_dark"]
	text_color = COLORS["background"] if hovered else COLORS["text"]
	pygame.draw.rect(screen, fill, rect, border_radius=6)
	draw_text(label, font_body, text_color, rect.center, center=True)


def draw_overlay(title, subtitle, button_label, button_rect, mouse_position):
	overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
	overlay.fill((11, 17, 18, 205))
	screen.blit(overlay, (BOARD_X, BOARD_Y))
	draw_text(title, font_title, COLORS["text"], (BOARD_X + BOARD_WIDTH // 2, 278), center=True)
	draw_text(subtitle, font_body, COLORS["muted"], (BOARD_X + BOARD_WIDTH // 2, 332), center=True)
	draw_button(button_label, button_rect, button_rect.collidepoint(mouse_position))


snake, direction, next_direction, food, score = reset_game()
best_score = 0
state = "ready"
move_timer = 0.0
button_rect = pygame.Rect(BOARD_X + BOARD_WIDTH // 2 - 90, 382, 180, 48)
running = True

while running:
	delta_time = clock.tick(FPS) / 1000
	mouse_position = pygame.mouse.get_pos()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
			if state in ("ready", "game_over") and button_rect.collidepoint(event.pos):
				snake, direction, next_direction, food, score = reset_game()
				move_timer = 0.0
				state = "playing"
			elif state == "paused" and button_rect.collidepoint(event.pos):
				state = "playing"
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False
			elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
				if state in ("ready", "game_over"):
					snake, direction, next_direction, food, score = reset_game()
					move_timer = 0.0
					state = "playing"
			elif event.key in (pygame.K_SPACE, pygame.K_p):
				if state == "playing":
					state = "paused"
				elif state == "paused":
					state = "playing"
			elif state == "playing":
				requested_direction = {
					pygame.K_UP: (0, -1),
					pygame.K_w: (0, -1),
					pygame.K_DOWN: (0, 1),
					pygame.K_s: (0, 1),
					pygame.K_LEFT: (-1, 0),
					pygame.K_a: (-1, 0),
					pygame.K_RIGHT: (1, 0),
					pygame.K_d: (1, 0),
				}.get(event.key)
				if requested_direction and requested_direction != (-direction[0], -direction[1]):
					next_direction = requested_direction

	if state == "playing":
		move_timer += delta_time
		move_interval = max(MIN_SPEED, START_SPEED - score * 0.0015)
		if move_timer >= move_interval:
			move_timer %= move_interval
			direction = next_direction
			head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
			eating = head == food
			body_to_check = snake if eating else snake[:-1]
			hit_wall = not (0 <= head[0] < BOARD_COLUMNS and 0 <= head[1] < BOARD_ROWS)
			if hit_wall or head in body_to_check:
				state = "game_over"
				best_score = max(best_score, score)
			else:
				snake.insert(0, head)
				if eating:
					score += 10
					best_score = max(best_score, score)
					food = new_food(snake)
					if food is None:
						state = "game_over"
				else:
					snake.pop()

	screen.fill(COLORS["background"])
	draw_board(snake, food)
	draw_hud(score, best_score)

	if state == "ready":
		draw_overlay("SNAKE", "A quiet little test of focus.", "START GAME", button_rect, mouse_position)
	elif state == "paused":
		draw_overlay("PAUSED", "Take a breath. Your run is right here.", "RESUME", button_rect, mouse_position)
	elif state == "game_over":
		draw_overlay("RUN OVER", f"You collected {score} points.", "PLAY AGAIN", button_rect, mouse_position)

	pygame.display.flip()

pygame.quit()
sys.exit()
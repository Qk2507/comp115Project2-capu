import pygame
import pygame.gfxdraw
import random
import sys

# ── Constants ──────────────────────────────────────────────────────────────────
COLS, ROWS = 20, 20
CELL       = 20
W, H       = COLS * CELL, ROWS * CELL  # 400 x 400
PANEL_H    = 44
BOTTOM_H   = 160
WIN_W      = W
WIN_H      = H + PANEL_H + BOTTOM_H

SPEEDS = [("Slow", 160), ("Normal", 100), ("Fast", 55)]

C_BG         = ( 45,  90,  27)
C_PANEL      = ( 74, 124,  47)
C_CELL_L     = (141, 198,  63)
C_CELL_D     = (125, 181,  52)
C_HEAD       = ( 74, 144, 217)
C_BODY       = ( 91, 163, 232)
C_OUTLINE    = ( 44, 111, 173)
C_APPLE      = (224,  48,  48)
C_APPLE_DARK = (180,  30,  30)
C_LEAF       = ( 58, 158,  47)
C_STEM       = ( 92,  51,  23)
C_WHITE      = (255, 255, 255)
C_EYE        = ( 26,  26,  46)
C_TEXT       = (255, 255, 255)
C_DIM        = (180, 210, 160)

TICK_EVENT = pygame.USEREVENT + 1


# ── Drawing helpers ────────────────────────────────────────────────────────────

def aa_circle(surf, colour, cx, cy, r, alpha=255):
    if r < 1:
        return
    s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
    pygame.gfxdraw.aacircle(s, r+2, r+2, r, (*colour[:3], alpha))
    pygame.gfxdraw.filled_circle(s, r+2, r+2, r, (*colour[:3], alpha))
    surf.blit(s, (cx - r - 2, cy - r - 2))


def draw_apple_icon(surf, cx, cy, r):
    aa_circle(surf, C_APPLE, cx - r//3, cy + r//5, int(r * 0.72))
    aa_circle(surf, C_APPLE, cx + r//3, cy + r//5, int(r * 0.72))
    pygame.draw.rect(surf, C_APPLE, (cx - r//3, cy - r//4, r//3*2 + 1, r))
    aa_circle(surf, C_APPLE_DARK, cx + r//4, cy + r//3, int(r * 0.45), alpha=90)
    aa_circle(surf, C_WHITE, cx - r//3, cy - r//6, int(r * 0.28), alpha=140)
    stem_x = cx + 1
    stem_top = cy - int(r * 0.85)
    pygame.draw.line(surf, C_STEM, (stem_x, cy - r//4), (stem_x, stem_top), 2)
    leaf_pts = [
        (stem_x,     stem_top + 4),
        (stem_x + 9, stem_top - 2),
        (stem_x + 5, stem_top + 7),
    ]
    pygame.draw.polygon(surf, C_LEAF, leaf_pts)
    pygame.gfxdraw.aapolygon(surf, leaf_pts, (*C_LEAF, 200))


def draw_btn(surf, label, rect, font, hover=False):
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s, (255, 255, 255, 90 if hover else 55), (0, 0, rect.w, rect.h), border_radius=14)
    surf.blit(s, (rect.x, rect.y))
    t = font.render(label, True, C_TEXT)
    surf.blit(t, (rect.x + rect.w//2 - t.get_width()//2,
                  rect.y + rect.h//2 - t.get_height()//2))


def draw_arrow_btn(surf, direction, rect, hover=False):
    s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
    pygame.draw.rect(s, (255, 255, 255, 90 if hover else 55), (0, 0, rect.w, rect.h), border_radius=12)
    surf.blit(s, (rect.x, rect.y))
    cx = rect.x + rect.w // 2
    cy = rect.y + rect.h // 2
    m = 9
    if direction == "up":
        pts = [(cx, cy - m), (cx - m, cy + m//2), (cx + m, cy + m//2)]
    elif direction == "down":
        pts = [(cx, cy + m), (cx - m, cy - m//2), (cx + m, cy - m//2)]
    elif direction == "left":
        pts = [(cx - m, cy), (cx + m//2, cy - m), (cx + m//2, cy + m)]
    else:
        pts = [(cx + m, cy), (cx - m//2, cy - m), (cx - m//2, cy + m)]
    pygame.draw.polygon(surf, C_WHITE, pts)
    pygame.gfxdraw.aapolygon(surf, pts, (*C_WHITE, 255))


def draw_board(surf, panel_h):
    for col in range(COLS):
        for row in range(ROWS):
            c = C_CELL_L if (col + row) % 2 == 0 else C_CELL_D
            pygame.draw.rect(surf, c, (col*CELL, panel_h + row*CELL, CELL, CELL))


def draw_snake(surf, snake, direction, panel_h):
    for i, (col, row) in enumerate(snake):
        x = col*CELL + 2
        y = panel_h + row*CELL + 2
        w = CELL - 4
        h = CELL - 4
        pygame.draw.rect(surf, C_OUTLINE, (x-1, y-1, w+2, h+2), border_radius=6)
        pygame.draw.rect(surf, C_HEAD if i == 0 else C_BODY, (x, y, w, h), border_radius=5)

    hcol, hrow = snake[0]
    hcx = hcol*CELL + CELL//2
    hcy = panel_h + hrow*CELL + CELL//2
    dx, dy = direction
    eo = 4
    if   dx ==  1: eyes = [(hcx+4, hcy-eo), (hcx+4, hcy+eo)]
    elif dx == -1: eyes = [(hcx-4, hcy-eo), (hcx-4, hcy+eo)]
    elif dy == -1: eyes = [(hcx-eo, hcy-4), (hcx+eo, hcy-4)]
    else:          eyes = [(hcx-eo, hcy+4), (hcx+eo, hcy+4)]
    for ex, ey in eyes:
        aa_circle(surf, C_WHITE, ex, ey, 3)
        aa_circle(surf, C_EYE,   ex, ey, 2)


def draw_apple(surf, food, panel_h):
    fc, fr = food
    acx = fc*CELL + CELL//2
    acy = panel_h + fr*CELL + CELL//2 + 1
    r   = CELL//2 - 2
    aa_circle(surf, C_APPLE, acx, acy, r)
    aa_circle(surf, (0,0,0),  acx+2, acy+2, int(r*0.6), alpha=40)
    aa_circle(surf, C_WHITE,  acx-3, acy-4, 3, alpha=110)
    pygame.draw.line(surf, C_STEM, (acx, acy-r+1), (acx+2, acy-r-6), 2)
    aa_circle(surf, C_LEAF, acx+4, acy-r-2, 4)


# ── Game logic ─────────────────────────────────────────────────────────────────

def place_food(snake):
    occupied = set(snake)
    while True:
        pos = (random.randint(0, COLS-1), random.randint(0, ROWS-1))
        if pos not in occupied:
            return pos


def init_game():
    mid   = ROWS // 2
    snake = [(6, mid), (5, mid), (4, mid)]
    return snake, (1, 0), (1, 0), place_food(snake), 0


def change_dir(cur, nxt, dx, dy):
    if (dx, dy) == (-cur[0], -cur[1]):
        return nxt
    return (dx, dy)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Snake")
    clock  = pygame.time.Clock()

    def load_font(size, bold=False):
        for name in ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans"]:
            f = pygame.font.match_font(name, bold=bold)
            if f:
                return pygame.font.Font(f, size)
        return pygame.font.SysFont(None, size + 8, bold=bold)

    font_big = load_font(20, bold=True)
    font_sm  = load_font(13)

    play_rect  = pygame.Rect(WIN_W - 88,  (PANEL_H-28)//2, 76, 28)
    speed_rect = pygame.Rect(WIN_W - 200, (PANEL_H-28)//2, 104, 28)

    # ── D-pad layout ──────────────────────────────────────────────────────────
    # Text zone: PANEL_H + H  to  PANEL_H + H + 34  (two lines of text)
    # D-pad zone: below that
    TEXT_ZONE_H = 34
    BS, GAP = 42, 6
    dcx    = WIN_W // 2
    dbase  = PANEL_H + H + TEXT_ZONE_H + 8   # starts below text

    dpad = {
        "up":    pygame.Rect(dcx - BS//2,            dbase,            BS, BS),
        "left":  pygame.Rect(dcx - BS - GAP - BS//2, dbase + BS + GAP, BS, BS),
        "down":  pygame.Rect(dcx - BS//2,            dbase + BS + GAP, BS, BS),
        "right": pygame.Rect(dcx + GAP + BS//2,      dbase + BS + GAP, BS, BS),
    }
    dmap = {"up":(0,-1), "down":(0,1), "left":(-1,0), "right":(1,0)}

    snake, direction, next_dir, food, score = init_game()
    best       = 0
    running    = False
    speed_idx  = 1
    msg        = "Press Play or Space to start"
    play_label = "Play"

    def restart():
        nonlocal snake, direction, next_dir, food, score, running, msg, play_label
        pygame.time.set_timer(TICK_EVENT, 0)
        snake, direction, next_dir, food, score = init_game()
        running    = True
        msg        = "Arrow keys or D-pad to steer"
        play_label = "Restart"
        pygame.time.set_timer(TICK_EVENT, SPEEDS[speed_idx][1])

    while True:
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    restart()
                elif running:
                    km = {pygame.K_UP:(0,-1), pygame.K_DOWN:(0,1),
                          pygame.K_LEFT:(-1,0), pygame.K_RIGHT:(1,0)}
                    if event.key in km:
                        next_dir = change_dir(direction, next_dir, *km[event.key])

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(event.pos):
                    restart()
                elif speed_rect.collidepoint(event.pos):
                    speed_idx = (speed_idx + 1) % len(SPEEDS)
                    if running:
                        pygame.time.set_timer(TICK_EVENT, 0)
                        pygame.time.set_timer(TICK_EVENT, SPEEDS[speed_idx][1])
                if running:
                    for k, r in dpad.items():
                        if r.collidepoint(event.pos):
                            next_dir = change_dir(direction, next_dir, *dmap[k])

            if event.type == TICK_EVENT and running:
                direction = next_dir
                hx, hy = snake[0]
                head   = (hx + direction[0], hy + direction[1])
                if head[0] < 0 or head[0] >= COLS or head[1] < 0 or head[1] >= ROWS or head in set(snake):
                    running    = False
                    msg        = f"Game over!  Score: {score}"
                    play_label = "Play Again"
                    pygame.time.set_timer(TICK_EVENT, 0)
                else:
                    snake.insert(0, head)
                    if head == food:
                        score += 1
                        if score > best:
                            best = score
                        food = place_food(snake)
                    else:
                        snake.pop()

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(C_BG)
        draw_board(screen, PANEL_H)
        draw_apple(screen, food, PANEL_H)
        draw_snake(screen, snake, direction, PANEL_H)

        # Panel
        pygame.draw.rect(screen, C_PANEL, (0, 0, WIN_W, PANEL_H), border_radius=10)
        draw_apple_icon(screen, 20, PANEL_H // 2 + 1, 12)
        t = font_big.render(str(score), True, C_TEXT)
        screen.blit(t, (38, PANEL_H//2 - t.get_height()//2))
        draw_btn(screen, f"Speed: {SPEEDS[speed_idx][0]}", speed_rect, font_sm, speed_rect.collidepoint(mouse))
        draw_btn(screen, play_label, play_rect, font_sm, play_rect.collidepoint(mouse))

        # Text lines — sit in their own zone above the d-pad
        text_y = PANEL_H + H + 6
        mt = font_sm.render(msg, True, C_DIM)
        screen.blit(mt, (WIN_W//2 - mt.get_width()//2, text_y))
        bt = font_sm.render(f"Best: {best}", True, C_DIM)
        screen.blit(bt, (WIN_W//2 - bt.get_width()//2, text_y + 16))

        # D-pad — sits below text, fully visible
        for k, r in dpad.items():
            draw_arrow_btn(screen, k, r, r.collidepoint(mouse))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
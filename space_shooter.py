
import tkinter as tk
import random

# ─── Constants ────────────────────────────────────────────────────────────────
W, H = 800, 650
FPS  = 30

# Palette
BG       = "#050A1A"
ACCENT   = "#00CFFF"
ACCENT2  = "#FF4D6D"
GOLD     = "#FFD700"
DIMGRAY  = "#1A2340"
WHITE    = "#E8F0FF"
DARKBLUE = "#0A1628"

# ─── Stars Background ─────────────────────────────────────────────────────────
class StarField:
    def __init__(self, canvas):
        self.canvas = canvas
        self.stars  = []
        for _ in range(60):
            x    = random.randint(0, W)
            y    = random.randint(0, H)
            r    = random.uniform(0.5, 1.5)
            spd  = random.uniform(0.4, 1.2)
            item = canvas.create_oval(x-r, y-r, x+r, y+r, fill="#AACCFF", outline="")
            self.stars.append([x, y, r, spd, item])

    def update(self):
        for s in self.stars:
            s[1] += s[3]
            if s[1] > H:
                s[1] = 0
                s[0] = random.randint(0, W)
            self.canvas.coords(s[4], s[0]-s[2], s[1]-s[2], s[0]+s[2], s[1]+s[2])


# ─── Bullet ───────────────────────────────────────────────────────────────────
class Bullet:
    def __init__(self, canvas, x, y, dy=-14):
        self.canvas = canvas
        self.x, self.y = x, y
        self.dy  = dy
        self.alive = True
        self.item = canvas.create_rectangle(x-2, y-10, x+2, y, fill=ACCENT, outline="")

    def update(self):
        self.y += self.dy
        self.canvas.move(self.item, 0, self.dy)
        if self.y < -20 or self.y > H + 20:
            self.destroy()

    def destroy(self):
        if self.alive:
            self.alive = False
            self.canvas.delete(self.item)

    def get_rect(self):
        return (self.x - 2, self.y - 10, self.x + 2, self.y)


# ─── Explosion ────────────────────────────────────────────────────────────────
class Explosion:
    def __init__(self, canvas, x, y):
        self.canvas  = canvas
        self.life    = 0
        self.max_life= 8
        self.ring = canvas.create_oval(x-2, y-2, x+2, y+2, outline=ACCENT2, width=2)

    def update(self):
        self.life += 1
        r = self.life * 4
        cx = self.canvas.coords(self.ring)
        if cx:
            midx, midy = (cx[0]+cx[2])/2, (cx[1]+cx[3])/2
            self.canvas.coords(self.ring, midx-r, midy-r, midx+r, midy+r)

    def is_done(self):
        return self.life >= self.max_life

    def destroy(self):
        self.canvas.delete(self.ring)


# ─── Enemy ────────────────────────────────────────────────────────────────────
class Enemy:
    def __init__(self, canvas, x, y, speed):
        self.canvas = canvas
        self.x, self.y = x, y
        self.alive  = True
        self.size   = 16
        self.dy     = speed  # Configured dynamically by the current level difficulty
        
        s = self.size
        pts = [x, y-s, x+s, y, x, y+s, x-s, y]
        self.body = self.canvas.create_polygon(*pts, fill=DIMGRAY, outline=ACCENT2, width=2)

    def update(self):
        self.y += self.dy
        self.canvas.move(self.body, 0, self.dy)

    def destroy(self):
        if self.alive:
            self.alive = False
            self.canvas.delete(self.body)

    def get_rect(self):
        s = self.size
        return (self.x - s, self.y - s, self.x + s, self.y + s)


# ─── Player ───────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, canvas):
        self.canvas  = canvas
        self.x       = W // 2
        self.y       = H - 60
        self.speed   = 8.5
        self.alive   = True
        
        x, y = self.x, self.y
        self.body = self.canvas.create_polygon(
            x, y-25, x-15, y+15, x, y+5, x+15, y+15,
            fill=DARKBLUE, outline=ACCENT, width=2
        )

    def move(self, dx, dy):
        nx = max(20, min(W - 20, self.x + dx * self.speed))
        ny = max(40, min(H - 20, self.y + dy * self.speed))
        self.canvas.move(self.body, nx - self.x, ny - self.y)
        self.x, self.y = nx, ny

    def destroy(self):
        if self.alive:
            self.alive = False
            self.canvas.delete(self.body)

    def get_rect(self):
        return (self.x - 15, self.y - 25, self.x + 15, self.y + 15)


# ─── Game Manager ─────────────────────────────────────────────────────────────
class Game:
    def __init__(self, root):
        self.root  = root
        self.root.title("GALACTIC ASSAULT")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.canvas = tk.Canvas(root, width=W, height=H, bg=BG, highlightthickness=0)
        self.canvas.pack()

        self.high_score = 0
        self._show_menu()

    def _show_menu(self):
        self.canvas.delete("all")
        self.state = "menu"
        self.stars_bg = StarField(self.canvas)

        cx = W // 2
        self.canvas.create_rectangle(cx-200, 100, cx+200, 180, fill=DARKBLUE, outline=ACCENT, width=1)
        self.canvas.create_text(cx, 140, text="GALACTIC ASSAULT", fill=ACCENT, font=("Courier", 26, "bold"))

        self.canvas.create_rectangle(cx-150, 220, cx+150, 360, fill=DARKBLUE, outline=DIMGRAY, width=1)
        self.canvas.create_text(cx, 245, text=f"HIGH SCORE: {self.high_score}", fill=GOLD, font=("Courier", 12, "bold"))
        self.canvas.create_text(cx, 290, text="Move: W, A, S, D / Arrows\nShoot: SPACEBAR", fill=WHITE, font=("Courier", 11), justify="center")

        btn = self.canvas.create_rectangle(cx-100, 420, cx+100, 465, fill=ACCENT, outline="")
        btn_txt = self.canvas.create_text(cx, 442, text="START GAME", fill=BG, font=("Courier", 14, "bold"))
        
        self.canvas.tag_bind(btn, "<Button-1>", lambda e: self._start_game())
        self.canvas.tag_bind(btn_txt, "<Button-1>", lambda e: self._start_game())

        self._menu_loop()

    def _menu_loop(self):
        if self.state == "menu":
            self.stars_bg.update()
            self.root.after(33, self._menu_loop)

    def _start_game(self):
        self.canvas.delete("all")
        self.state      = "playing"
        self.score      = 0
        self.level      = 1  # Standard start point
        self.enemies    = []
        self.bullets    = []
        self.explosions = []
        self.keys       = set()

        self.stars_bg   = StarField(self.canvas)
        self.player     = Player(self.canvas)
        
        # HUD Layout setup with dynamic elements
        self.canvas.create_rectangle(0, 0, W, 40, fill=DARKBLUE, outline=DIMGRAY, tags="hud")
        self.score_val = self.canvas.create_text(20, 20, text="SCORE: 0", fill=WHITE, font=("Courier", 12, "bold"), anchor="w", tags="hud")
        self.level_val = self.canvas.create_text(W - 20, 20, text="LEVEL: 1 (EASY)", fill=GOLD, font=("Courier", 12, "bold"), anchor="e", tags="hud")

        self.root.bind("<KeyPress>",   lambda e: self.keys.add(e.keysym.lower()))
        self.root.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym.lower()))

        self._spawn_wave()
        self._loop()

    def _spawn_wave(self):
        # ─── Level Scaling Configurations ─────────────────────────────────────
        if self.level == 1:
            rows, cols, speed, label = 2, 4, 0.6, "1 (EASY)"
        elif self.level == 2:
            rows, cols, speed, label = 2, 6, 0.9, "2 (NORMAL)"
        elif self.level == 3:
            rows, cols, speed, label = 3, 7, 1.2, "3 (INTERMEDIATE)"
        elif self.level == 4:
            rows, cols, speed, label = 3, 9, 1.5, "4 (HARD)"
        else:  # Level 5 or higher
            rows, cols, speed, label = 4, 10, 1.9, "5 (VERY HARD)"

        self.canvas.itemconfig(self.level_val, text=f"LEVEL: {label}")

        # Centering calculations for the rows
        start_x = (W - (cols - 1) * 75) // 2
        for row in range(rows):
            for col in range(cols):
                x = start_x + col * 75
                y = 60 + row * 45
                self.enemies.append(Enemy(self.canvas, x, y, speed))

    def _loop(self):
        if self.state != "playing": return

        dx = dy = 0
        if "left"  in self.keys or "a" in self.keys: dx -= 1
        if "right" in self.keys or "d" in self.keys: dx += 1
        if "up"    in self.keys or "w" in self.keys: dy -= 1
        if "down"  in self.keys or "s" in self.keys: dy += 1
        if dx or dy: self.player.move(dx, dy)

        if "space" in self.keys and len(self.bullets) < 4:
            self.bullets.append(Bullet(self.canvas, self.player.x, self.player.y - 25))
            if "space" in self.keys: self.keys.remove("space")

        self.stars_bg.update()

        for b in self.bullets[:]:
            if b.alive: b.update()
            else: self.bullets.remove(b)

        for e in self.enemies[:]:
            if e.alive:
                e.update()
                if e.y > H - 40 or self._overlap(e.get_rect(), self.player.get_rect()):
                    self._game_over()
                    return
            else:
                self.enemies.remove(e)

        for ex in self.explosions[:]:
            ex.update()
            if ex.is_done():
                ex.destroy()
                self.explosions.remove(ex)

        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if b.alive and e.alive and self._overlap(b.get_rect(), e.get_rect()):
                    b.destroy()
                    e.destroy()
                    self.score += 10
                    self.high_score = max(self.high_score, self.score)
                    self.canvas.itemconfig(self.score_val, text=f"SCORE: {self.score}")
                    self.explosions.append(Explosion(self.canvas, e.x, e.y))

        # Progress logic upon clearing structural array arrays
        if not self.enemies:
            if self.level < 5:
                self.level += 1
            self._spawn_wave()

        self.canvas.tag_raise("hud")
        self.root.after(1000 // FPS, self._loop)

    def _overlap(self, r1, r2):
        return r1[0]<r2[2] and r1[2]>r2[0] and r1[1]<r2[3] and r1[3]>r2[1]

    def _game_over(self):
        self.state = "gameover"
        self.canvas.delete("all")
        self.stars_bg = StarField(self.canvas)

        cx = W // 2
        self.canvas.create_rectangle(cx-150, 150, cx+150, 230, fill=DARKBLUE, outline=ACCENT2, width=1)
        self.canvas.create_text(cx, 190, text="GAME OVER", fill=ACCENT2, font=("Courier", 24, "bold"))

        self.canvas.create_rectangle(cx-150, 260, cx+150, 340, fill=DARKBLUE, outline=DIMGRAY, width=1)
        self.canvas.create_text(cx, 300, text=f"FINAL SCORE: {self.score}", fill=WHITE, font=("Courier", 14, "bold"))

        btn = self.canvas.create_rectangle(cx-100, 390, cx+100, 435, fill=ACCENT, outline="")
        btn_txt = self.canvas.create_text(cx, 412, text="MAIN MENU", fill=BG, font=("Courier", 12, "bold"))

        self.canvas.tag_bind(btn, "<Button-1>", lambda e: self._show_menu())
        self.canvas.tag_bind(btn_txt, "<Button-1>", lambda e: self._show_menu())
        self._go_loop()

    def _go_loop(self):
        if self.state == "gameover":
            self.stars_bg.update()
            self.root.after(33, self._go_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
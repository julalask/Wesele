import asyncio
import os
import random
import sys

import pygame


# =========================================================
# ZŁAP PREZENT
# Gra weselna dla Julii i Norberta
#
# Folder assets:
# background.png  -> tło gry
# player.png      -> Julia i Norbert jako główna postać
# ring.png        -> obrączki, dobry przedmiot
# bouquet.png     -> bukiet, dobry przedmiot
# cake.png        -> tort, dobry przedmiot
# lemon.png       -> cytryna, dobry przedmiot
# heart.png       -> serce, dobry przedmiot + ikonka życia
# cloud.png       -> chmurka, zły przedmiot
# bad_glass.png   -> stłuczony kieliszek, zły przedmiot
# =========================================================


WIDTH = 960
HEIGHT = 540
FPS = 60

TITLE = "Złap prezent"
BRIDE = "Julia"
GROOM = "Norbert"

ASSET_DIR = "assets"


GOOD_ITEMS = [
    {
        "name": "Obrączki",
        "image": "ring.png",
        "points": 25,
        "size": (76, 76),
    },
    {
        "name": "Bukiet",
        "image": "bouquet.png",
        "points": 20,
        "size": (76, 76),
    },
    {
        "name": "Tort",
        "image": "cake.png",
        "points": 18,
        "size": (78, 78),
    },
    {
        "name": "Cytryna",
        "image": "lemon.png",
        "points": 12,
        "size": (66, 66),
    },
    {
        "name": "Serce",
        "image": "heart.png",
        "points": 15,
        "size": (58, 58),
    },
]

BAD_ITEMS = [
    {
        "name": "Chmurka",
        "image": "cloud.png",
        "points": -15,
        "size": (80, 62),
    },
    {
        "name": "Stłuczony kieliszek",
        "image": "bad_glass.png",
        "points": -20,
        "size": (76, 76),
    },
]


pygame.init()
pygame.display.set_caption(TITLE)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT_BIG = pygame.font.SysFont("georgia", 54, bold=True)
FONT_MEDIUM = pygame.font.SysFont("georgia", 30, bold=True)
FONT_SMALL = pygame.font.SysFont("georgia", 22)
FONT_TINY = pygame.font.SysFont("georgia", 16)


def asset_path(filename):
    return os.path.join(ASSET_DIR, filename)


def load_image(filename, size=None):
    image = pygame.image.load(asset_path(filename)).convert_alpha()
    if size is not None:
        image = pygame.transform.smoothscale(image, size)
    return image


BACKGROUND = load_image("background.png", (WIDTH, HEIGHT))
PLAYER_IMAGE = load_image("player.png", (200, 200))
HEART_IMAGE = load_image("heart.png", (30, 30))

IMAGES = {}
for item in GOOD_ITEMS + BAD_ITEMS:
    IMAGES[item["image"]] = load_image(item["image"], item["size"])


def draw_text_center(text, font, color, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(WIDTH // 2, y))
    screen.blit(surface, rect)


def draw_background():
    screen.blit(BACKGROUND, (0, 0))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 250, 240, 45))
    screen.blit(overlay, (0, 0))


def draw_panel(rect, alpha=205):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (255, 248, 235, alpha), panel.get_rect(), border_radius=18)
    pygame.draw.rect(panel, (170, 129, 67, 230), panel.get_rect(), 2, border_radius=18)
    screen.blit(panel, rect)


def draw_button(rect, text):
    pygame.draw.rect(screen, (218, 180, 112), rect, border_radius=18)
    pygame.draw.rect(screen, (103, 72, 38), rect, 3, border_radius=18)
    label = FONT_MEDIUM.render(text, True, (72, 47, 26))
    screen.blit(label, label.get_rect(center=rect.center))


def draw_hearts(lives):
    x = WIDTH // 2 - 24
    y = 28
    for i in range(3):
        if i < lives:
            screen.blit(HEART_IMAGE, (x + i * 34, y))
        else:
            empty = HEART_IMAGE.copy()
            empty.set_alpha(65)
            screen.blit(empty, (x + i * 34, y))


def create_particles(x, y):
    particles = []
    colors = [
        (230, 183, 91),
        (240, 200, 118),
        (242, 161, 166),
        (154, 180, 119),
        (255, 242, 200),
    ]
    for _ in range(18):
        particles.append(
            {
                "x": x,
                "y": y,
                "vx": random.uniform(-180, 180),
                "vy": random.uniform(-230, -70),
                "life": random.uniform(0.35, 0.85),
                "color": random.choice(colors),
            }
        )
    return particles


class FallingItem:
    def __init__(self, level):
        bad_chance = min(0.16 + level * 0.025, 0.40)

        if random.random() < bad_chance:
            data = random.choice(BAD_ITEMS)
            self.bad = True
        else:
            data = random.choice(GOOD_ITEMS)
            self.bad = False

        self.name = data["name"]
        self.points = data["points"]
        self.image_name = data["image"]
        self.image = IMAGES[self.image_name]

        self.x = random.randint(70, WIDTH - 70)
        self.y = -90

        # Z czasem przedmioty spadają coraz szybciej.
        self.speed = random.uniform(145, 235) + level * 28

        self.drift = random.uniform(-35, 35)
        self.angle = random.uniform(-8, 8)
        self.rotation_speed = random.uniform(-55, 55)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, dt):
        self.x += self.drift * dt
        self.y += self.speed * dt
        self.angle += self.rotation_speed * dt

        if self.x < 45 or self.x > WIDTH - 45:
            self.drift *= -1

        self.rect = self.image.get_rect(center=(self.x, self.y))

    def draw(self):
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)


class Game:
    def __init__(self):
        self.state = "menu"
        self.player_x = WIDTH // 2
        self.player_speed = 650
        self.items = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.time_left = 60
        self.spawn_timer = 0
        self.level = 1
        self.message = ""
        self.message_timer = 0

    def reset(self):
        self.state = "playing"
        self.player_x = WIDTH // 2
        self.items = []
        self.particles = []
        self.score = 0
        self.lives = 3
        self.time_left = 60
        self.spawn_timer = 0
        self.level = 1
        self.message = ""
        self.message_timer = 0

    def player_rect(self):
        return pygame.Rect(self.player_x - 60, HEIGHT - 210, 120, 60)

    def spawn_item(self):
        self.items.append(FallingItem(self.level))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.player_x = max(165, min(WIDTH - 165, event.pos[0]))

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state in ("menu", "gameover"):
                self.reset()

        if event.type == pygame.KEYDOWN:
            if self.state == "menu" and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.reset()
            elif self.state == "gameover" and event.key in (
                pygame.K_r,
                pygame.K_SPACE,
                pygame.K_RETURN,
            ):
                self.reset()
            elif self.state == "playing" and event.key == pygame.K_ESCAPE:
                self.state = "menu"

    def update(self, dt):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x -= self.player_speed * dt
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x += self.player_speed * dt

        self.player_x = max(165, min(WIDTH - 165, self.player_x))

        self.time_left -= dt

        # Tempo gry rośnie z czasem.
        elapsed_time = 60 - self.time_left
        self.level = 1 + int(elapsed_time // 7)

        self.spawn_timer -= dt

        # Z czasem przedmioty pojawiają się coraz częściej.
        spawn_interval = max(0.22, 0.85 - self.level * 0.065)

        if self.spawn_timer <= 0:
            self.spawn_item()
            self.spawn_timer = spawn_interval

        catcher = self.player_rect()

        for item in self.items[:]:
            item.update(dt)

            if item.rect.colliderect(catcher):
                self.items.remove(item)

                if item.bad:
                    self.score = max(0, self.score + item.points)
                    self.lives -= 1
                    self.message = f"Ups! {item.name}: {item.points} pkt"
                else:
                    self.score += item.points
                    self.message = f"{item.name}: +{item.points} pkt"
                    self.particles.extend(create_particles(item.x, item.y))

                self.message_timer = 1.1

            elif item.y > HEIGHT + 90:
                self.items.remove(item)
                if not item.bad:
                    self.message = "Prezent spadł na parkiet!"
                    self.message_timer = 0.8

        for particle in self.particles[:]:
            particle["life"] -= dt
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["vy"] += 420 * dt
            if particle["life"] <= 0:
                self.particles.remove(particle)

        if self.message_timer > 0:
            self.message_timer -= dt

        if self.time_left <= 0 or self.lives <= 0:
            self.state = "gameover"

    def draw_hud(self):
        rect_score = pygame.Rect(28, 18, 220, 48)
        rect_lives = pygame.Rect(360, 18, 240, 48)
        rect_time = pygame.Rect(715, 18, 215, 48)

        draw_panel(rect_score, 220)
        draw_panel(rect_lives, 220)
        draw_panel(rect_time, 220)

        score_text = FONT_SMALL.render(f"Punkty: {self.score}", True, (76, 48, 25))
        lives_text = FONT_SMALL.render("Życia:", True, (76, 48, 25))
        time_text = FONT_SMALL.render(f"Czas: {max(0, int(self.time_left))} s", True, (76, 48, 25))

        screen.blit(score_text, (48, 31))
        screen.blit(lives_text, (382, 31))
        draw_hearts(self.lives)
        screen.blit(time_text, (748, 31))

        tempo_text = FONT_TINY.render(f"Tempo: {self.level}", True, (76, 48, 25))
        screen.blit(tempo_text, (806, 68))

        if self.message_timer > 0:
            label = FONT_SMALL.render(self.message, True, (77, 49, 25))
            bg = pygame.Rect(0, 0, label.get_width() + 42, 42)
            bg.center = (WIDTH // 2, 88)
            draw_panel(bg, 230)
            screen.blit(label, label.get_rect(center=bg.center))

    def draw_player(self):
        player_rect = PLAYER_IMAGE.get_rect(midbottom=(self.player_x, HEIGHT - 10))

        shadow = pygame.Surface((180, 28), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (65, 45, 24, 45), shadow.get_rect())
        screen.blit(shadow, (self.player_x - 90, HEIGHT - 24))

        screen.blit(PLAYER_IMAGE, player_rect)

    def draw_particles(self):
        for particle in self.particles:
            alpha = max(0, min(255, int(255 * particle["life"])))
            surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(surf, particle["color"] + (alpha,), (4, 4), 4)
            screen.blit(surf, (particle["x"], particle["y"]))

    def draw_menu(self):
        draw_background()

        panel = pygame.Rect(160, 92, 640, 342)
        draw_panel(panel, 218)

        draw_text_center(TITLE, FONT_BIG, (74, 47, 24), 180)
        draw_text_center(f"{BRIDE} & {GROOM}", FONT_MEDIUM, (135, 96, 48), 228)

        lines = [
            "Steruj Julią i Norbertem i łap weselne prezenty.",
            "Zbieraj: obrączki, bukiety, tort, cytryny i serca.",
            "Unikaj: chmurki i stłuczonego kieliszka.",
            "Im dłużej grasz, tym szybciej spadają przedmioty.",
            "Sterowanie: myszka, dotyk, strzałki albo A/D.",
        ]

        for i, line in enumerate(lines):
            label = FONT_SMALL.render(line, True, (84, 60, 38))
            screen.blit(label, label.get_rect(center=(WIDTH // 2, 265 + i * 25)))

        draw_button(pygame.Rect(332, 455, 296, 58), "START")

    def draw_gameover(self):
        draw_background()

        panel = pygame.Rect(190, 110, 580, 300)
        draw_panel(panel, 225)

        draw_text_center("Koniec gry!", FONT_BIG, (74, 47, 24), 165)
        draw_text_center(f"Wynik: {self.score} punktów", FONT_MEDIUM, (130, 88, 43), 225)

        if self.score >= 1000:
            comment = "Świetnie Ci poszło! Za taki wynik powinien być bimber!"
        elif self.score >= 500:
            comment = "Całkiem nieźle! Para Młoda ma refleks jak na parkiecie!"
        else:
            comment = "Jeszcze jedna runda - może pójdzie lepiej!"

        draw_text_center(comment, FONT_SMALL, (84, 60, 38), 272)
        draw_button(pygame.Rect(310, 330, 340, 58), "ZAGRAJ PONOWNIE")
        draw_text_center("Kliknij albo naciśnij R / Spację", FONT_TINY, (105, 81, 61), 430)

    def draw_playing(self):
        draw_background()

        for item in self.items:
            item.draw()

        self.draw_particles()
        self.draw_player()
        self.draw_hud()

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_playing()
        elif self.state == "gameover":
            self.draw_gameover()


game = Game()


async def main():
    running = True

    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        game.update(dt)
        game.draw()
        pygame.display.update()

        await asyncio.sleep(0)

    if sys.platform != "emscripten":
        pygame.quit()


asyncio.run(main())
import os
import pygame
from .player import Player
from .platform import Platform
from .hazard import Hazard

# Game Engine

WHITE = (255, 255, 255)
BROWN = (150, 100, 60)
RED = (220, 60, 60)
GREEN = (0, 200, 0)
GOLD = (240, 200, 60)
GRAY = (190, 190, 190)

# (name, key, gravity per 60 FPS frame, jump strength)
DIFFICULTIES = [
    ("Easy",   pygame.K_1, 0.45, -11),
    ("Medium", pygame.K_2, 0.60, -12),
    ("Hard",   pygame.K_3, 0.80, -12),
]


# Sound files live in an "assets/sounds" folder next to this file.
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "sounds")
SOUND_NAMES = ["jump", "land", "goal", "game_over"]  # looked up as <name>.wav, .ogg or .mp3


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.start_x, self.start_y = 40, height - 120

        # A forgiving hand-built level: wide platforms with small gaps
        # (falling into a gap means falling off the bottom of the
        # screen), one thin hazard, and a goal near the right edge.
        ground_y = height - 40
        self.platforms = [
            Platform(0, ground_y, 190),
            Platform(235, ground_y, 180),
            Platform(460, ground_y - 60, 160),
            Platform(650, ground_y, 200),
        ]
        self.hazards = [Hazard(300, ground_y - 8, 60, 8)]
        self.goal_x = 740

        self.font = pygame.font.SysFont("Arial", 30)
        self.small_font = pygame.font.SysFont("Arial", 24)
        self.title_font = pygame.font.SysFont("Arial", 56, bold=True)

        self._load_sounds()
        self.reset("Medium")

    def _load_sounds(self):
        """Load whatever sound files exist; missing files or no audio device are fine."""
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            return  # no audio device: run silently
        for name in SOUND_NAMES:
            for ext in (".wav", ".ogg", ".mp3"):
                path = os.path.join(SOUND_DIR, name + ext)
                if os.path.exists(path):
                    try:
                        self.sounds[name] = pygame.mixer.Sound(path)
                    except pygame.error:
                        pass
                    break

    def play(self, name):
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def reset(self, difficulty):
        """Start a fresh run at the given difficulty name."""
        name, _, gravity, jump_strength = next(
            d for d in DIFFICULTIES if d[0] == difficulty
        )
        self.difficulty = name
        self.gravity = gravity

        self.player = Player(self.start_x, self.start_y)
        self.player.GRAVITY = gravity
        self.player.jump_strength = jump_strength

        self.score = 0
        self.game_over = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if not self.game_over:
            if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                if self.player.on_ground:
                    self.play("jump")
                self.player.jump()
            return

        # Game-over screen: pick a difficulty to play again, or exit.
        for name, key, _, _ in DIFFICULTIES:
            if event.key == key:
                self.reset(name)
                return
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_input(self):
        if self.game_over:
            self.player.vx = 0
            return
        keys = pygame.key.get_pressed()
        self.player.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.vx = -self.player.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.vx = self.player.speed

    def update(self, dt=1 / 60):
        """dt in seconds, e.g. clock.tick(60) / 1000."""
        if self.game_over:
            return

        # Delta-time gravity plus swept collision lives in Player.update.
        was_on_ground = self.player.on_ground
        self.player.update(dt, self.platforms)
        if self.player.x < 0:
            self.player.x = 0
        if self.player.on_ground and not was_on_ground:
            self.play("land")

        for hazard in self.hazards:
            if self.player.rect().colliderect(hazard.rect()):
                self.game_over = True
                self.play("game_over")
                return

        if self.player.y > self.height:
            self.game_over = True
            self.play("game_over")
            return

        if self.player.x >= self.goal_x:
            self.score += 1
            self.play("goal")
            self.player.x, self.player.y = self.start_x, self.start_y
            self.player.vy = 0

    def _draw_centered(self, screen, text, font, color, y):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(self.width // 2, y))
        screen.blit(surface, rect)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        cy = self.height // 2
        self._draw_centered(screen, "GAME OVER", self.title_font, RED, cy - 110)
        self._draw_centered(screen, f"Final score: {self.score}", self.font, WHITE, cy - 55)
        self._draw_centered(screen, "Play again - choose a difficulty:", self.small_font, GRAY, cy)
        for i, (name, key, _, _) in enumerate(DIFFICULTIES):
            label = f"{pygame.key.name(key)}  -  {name}"
            color = GOLD if name == self.difficulty else WHITE
            self._draw_centered(screen, label, self.small_font, color, cy + 35 + i * 30)
        self._draw_centered(screen, "Esc  -  Exit", self.small_font, GRAY, cy + 145)

    def render(self, screen):
        for platform in self.platforms:
            pygame.draw.rect(screen, BROWN, platform.rect())
        for hazard in self.hazards:
            pygame.draw.rect(screen, RED, hazard.rect())

        goal_rect = pygame.Rect(self.goal_x, 0, 6, self.height)
        pygame.draw.rect(screen, GREEN, goal_rect)

        pygame.draw.rect(screen, WHITE, self.player.rect())

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            self._render_game_over(screen)

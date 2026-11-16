import pygame

class Player:
    GRAVITY = 0.6          # per frame at 60 FPS
    MAX_FALL_SPEED = 20    # per frame at 60 FPS
    MAX_DT = 0.05          # clamp long frames (window drag, lag spike)

    def __init__(self, x, y, width=24, height=32):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = 0
        self.vy = 0
        self.speed = 4
        self.jump_strength = -12
        self.on_ground = False

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def jump(self):
        if self.on_ground:
            self.vy = self.jump_strength
            self.on_ground = False

    def update(self, dt, platforms):
        """dt in seconds (e.g. clock.tick(60) / 1000)."""
        step = min(dt, self.MAX_DT) * 60  # 1.0 == one 60 FPS frame

        # --- Horizontal: move, then push out sideways only ---
        self.x += self.vx * step
        player_rect = self.rect()
        for p in platforms:
            pr = p.rect()
            if player_rect.colliderect(pr):
                if self.vx > 0:
                    self.x = pr.left - self.width
                elif self.vx < 0:
                    self.x = pr.right
                player_rect = self.rect()

        # --- Vertical: gravity scaled by dt, swept against previous position ---
        prev_top = self.y
        prev_bottom = self.y + self.height

        self.vy = min(self.vy + self.GRAVITY * step, self.MAX_FALL_SPEED)
        self.y += self.vy * step
        bottom = self.y + self.height
        self.on_ground = False

        landing_top = None
        ceiling_bottom = None
        for p in platforms:
            pr = p.rect()
            if self.x + self.width <= pr.left or self.x >= pr.right:
                continue  # no horizontal overlap

            # Falling: did the feet cross the platform's top surface this frame?
            if self.vy >= 0 and prev_bottom <= pr.top and bottom >= pr.top:
                if landing_top is None or pr.top < landing_top:
                    landing_top = pr.top  # nearest surface wins
            # Rising: did the head cross the platform's underside?
            elif self.vy < 0 and prev_top >= pr.bottom and self.y <= pr.bottom:
                if ceiling_bottom is None or pr.bottom > ceiling_bottom:
                    ceiling_bottom = pr.bottom

        if landing_top is not None:
            self.y = landing_top - self.height
            self.vy = 0
            self.on_ground = True
        elif ceiling_bottom is not None:
            self.y = ceiling_bottom
            self.vy = 0

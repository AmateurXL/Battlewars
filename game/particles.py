class Particle:
    def __init__(self, x, y, vx, vy, color):
        self.x     = x
        self.y     = y
        self.vx    = vx
        self.vy    = vy
        self.color = color
        self.life  = 20

    def update(self) -> bool:
        """Move particle. Returns False when it should be removed."""
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.1
        self.life -= 1
        return self.life > 0
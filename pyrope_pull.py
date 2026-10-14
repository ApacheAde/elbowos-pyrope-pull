#!/usr/bin/env python3
"""Pyrope Pull — full-colour Python 3 neon magnet arcade for ElbowOS."""
import math, os, random, subprocess, sys
RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame
W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/PYROPE_PULL_ElbowOS.mp4")
TITLE, HANDLE = "PYROPE PULL", "x.com/ElbowOS"
BG = (6, 4, 18)
NAVY = (12, 8, 32)
CYAN = (48, 220, 255)
MAG = (255, 64, 196)
GOLD = (255, 196, 64)
VIOLET = (168, 92, 255)
LIME = (140, 255, 90)
WHITE = (244, 248, 255)
ROSE = (255, 90, 120)
class Orb:
    def __init__(self):
        self.x = random.randint(80, W-80)
        self.y = random.randint(-400, -40)
        self.vy = random.uniform(3.5, 7.0)
        self.r = random.randint(18, 32)
        self.kind = random.choice(["gold"]*3 + ["violet"])
        self.alive = True
    def update(self, mx, my, polarity):
        # polarity +1 attract gold/repel violet, -1 opposite
        dx = mx - self.x
        dy = my - self.y
        dist = math.hypot(dx, dy) + 1
        force = 0
        if self.kind == "gold":
            force = 1800 * polarity / dist
        else:
            force = -2200 * polarity / dist
        if dist < 320:
            self.x += force * dx / dist * 0.15
            self.y += force * dy / dist * 0.08
        self.y += self.vy
        if self.y > H + 40 or self.y < -600:
            self.alive = False
class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.font_lg = pygame.font.SysFont("Arial", 72, bold=True)
        self.font_md = pygame.font.SysFont("Arial", 42, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 28)
        self.mx = W // 2
        self.my = H - 180
        self.pol = 1  # +1 cyan attract gold
        self.orbs = [Orb() for _ in range(8)]
        self.score = 0
        self.lives = 3
        self.t = 0
        self.particles = []
        self.canvas = pygame.Surface((W, H))
    def spawn(self):
        if random.random() < 0.18 and len(self.orbs) < 14:
            self.orbs.append(Orb())
    def autoplay(self):
        # simple AI
        golds = [o for o in self.orbs if o.alive and o.kind == "gold" and o.y > 200]
        violets = [o for o in self.orbs if o.alive and o.kind == "violet" and o.y > 300]
        target = None
        if golds:
            target = min(golds, key=lambda o: abs(o.x - self.mx) + (H - o.y)*0.3)
            if abs(target.x - self.mx) > 40:
                self.mx += 12 if target.x > self.mx else -12
        if violets and random.random() < 0.3:
            v = min(violets, key=lambda o: abs(o.x - self.mx))
            if abs(v.x - self.mx) < 120 and v.y > self.my - 200:
                self.mx += 18 if v.x < self.mx else -18
        if random.random() < 0.04:
            self.pol *= -1
        self.mx = max(60, min(W-60, self.mx))
    def tick(self):
        self.t += 1
        self.spawn()
        for o in self.orbs:
            if not o.alive: continue
            o.update(self.mx, self.my, self.pol)
            if o.y > self.my - 30 and abs(o.x - self.mx) < 55:
                if o.kind == "gold":
                    self.score += 15
                    o.alive = False
                    self.particles.append([o.x, o.y, GOLD, 20])
                else:
                    self.score = max(0, self.score - 25)
                    self.lives -= 1
                    o.alive = False
                    self.particles.append([o.x, o.y, ROSE, 30])
        self.orbs = [o for o in self.orbs if o.alive]
        # particles
        for p in self.particles[:]:
            p[3] -= 1
            if p[3] <= 0:
                self.particles.remove(p)
        if self.lives <= 0:
            self.lives = 3
            self.score = max(0, self.score // 2)
    def draw(self, surf):
        surf.fill(BG)
        # subtle grid
        for i in range(0, W, 60):
            pygame.draw.line(surf, (20, 16, 40), (i, 0), (i, H), 1)
        for i in range(0, H, 60):
            pygame.draw.line(surf, (20, 16, 40), (0, i), (W, i), 1)
        # orbs
        for o in self.orbs:
            col = GOLD if o.kind == "gold" else VIOLET
            pygame.draw.circle(surf, col, (int(o.x), int(o.y)), o.r)
            pygame.draw.circle(surf, WHITE, (int(o.x), int(o.y)), o.r, 3)
            if o.kind == "gold":
                pygame.draw.circle(surf, (255, 255, 180), (int(o.x-6), int(o.y-6)), o.r//3)
        # particles
        for p in self.particles:
            pygame.draw.circle(surf, p[2], (int(p[0]), int(p[1])), max(2, p[3]//3))
        # magnet
        pol_col = CYAN if self.pol > 0 else MAG
        pygame.draw.rect(surf, pol_col, (self.mx-50, self.my-20, 100, 40), border_radius=12)
        pygame.draw.rect(surf, WHITE, (self.mx-50, self.my-20, 100, 40), 4, border_radius=12)
        lab = "+" if self.pol > 0 else "-"
        txt = self.font_md.render(lab, True, WHITE)
        surf.blit(txt, txt.get_rect(center=(self.mx, self.my)))
        # field glow
        for r in (80, 140, 200):
            alpha_surf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surf, (*pol_col, 30), (r, r), r, 4)
            surf.blit(alpha_surf, (self.mx-r, self.my-r))
        # HUD
        title = self.font_lg.render(TITLE, True, GOLD)
        surf.blit(title, title.get_rect(center=(W//2, 90)))
        sc = self.font_md.render(f"SCORE {self.score}", True, LIME)
        surf.blit(sc, sc.get_rect(center=(W//2, 170)))
        lv = self.font_sm.render(f"LIVES {self.lives}  POL {'ATTRACT' if self.pol>0 else 'REPEL'}", True, CYAN)
        surf.blit(lv, lv.get_rect(center=(W//2, 220)))
        handle = self.font_sm.render(HANDLE, True, WHITE)
        surf.blit(handle, handle.get_rect(center=(W//2, H-60)))
        hint = self.font_sm.render("A/D move  SPACE flip polarity", True, (180, 180, 200))
        surf.blit(hint, hint.get_rect(center=(W//2, H-100)))
    def play_interactive(self):
        screen = pygame.display.set_mode((W, H))
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    self.pol *= -1
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.mx -= 14
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.mx += 14
            self.mx = max(60, min(W-60, self.mx))
            self.tick()
            self.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()
    def record(self):
        frames = FPS * SECS
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-preset", "fast", "-movflags", "+faststart", OUT
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for i in range(frames):
                self.autoplay()
                self.tick()
                self.draw(self.canvas)
                proc.stdin.write(pygame.image.tostring(self.canvas, "RGB"))
                if i % 30 == 0:
                    print(f"frame {i}/{frames}", flush=True)
        finally:
            proc.stdin.close()
            err = proc.stderr.read().decode("utf-8", "ignore")
            rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()
def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()
if __name__ == "__main__":
    main()

import pygame
from game.world import World
from game.constants import W, H, FPS, TITLE

def main():
    pygame.init()

    # Start at native resolution — resizable from here
    screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Fixed internal surface — all game rendering goes here
    canvas = pygame.Surface((W, H))

    world = World(canvas, screen)
    world.new_battle()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()
            world.handle_event(event)

        world.update()
        world.draw()

        # Scale canvas to current window size
        win_w, win_h = screen.get_size()
        scaled = pygame.transform.scale(canvas, (win_w, win_h))
        screen.blit(scaled, (0, 0))

        # Debug panels drawn AFTER scale — native window resolution
        world.draw_debug(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
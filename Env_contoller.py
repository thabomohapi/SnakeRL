import sys

class GameController:
    def __init__(self, engine):
        self.engine = engine

    def run_game(self):
        self.engine.e.time.set_timer(self.engine.SCREEN_UPDATE, 150)
        while True:
            if self.engine.death:
                self.engine.reset_game()

            events = self.engine.e.event.get()
            keys = self.engine.e.key.get_pressed()
            for event in events:
                if event.type == self.engine.e.QUIT or keys[self.engine.e.K_ESCAPE]:
                    self.engine.e.quit()
                    sys.exit()

                if event.type == self.engine.SCREEN_UPDATE:
                    self.engine.update()
                
            self.engine.handle_keys(keys)
            self.engine.view.update_high_score()
            self.engine.view.draw()
            self.engine.e.display.flip() # use flip instead of update for a complete frame update
            self.engine.clock.tick(self.engine.fps) # set framerate
import sys

class GameController:
    def __init__(self, engine):
        self.engine = engine

    def run_game(self):
        self.engine.e.time.set_timer(self.engine.SCREEN_UPDATE, 105)
        self.engine.running = True
        while self.engine.running:
            self.engine.event_manager.handle_events()
                
            if self.engine.death:
                self.engine.reset_game()
            
            self.engine.event_manager.handle_keys()
            self.engine.renderer.update_high_score()
            self.engine.renderer.draw()
            self.engine.e.display.flip() # use flip instead of update for a complete frame update
            self.engine.clock.tick(self.engine.fps) # set framerate
        
        self.engine.e.quit()
        sys.exit()
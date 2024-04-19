class EventManager:
    def __init__(self, engine: object) -> None:
        self.engine = engine

    def handle_events(self) -> None:
        self.events = self.engine.e.event.get()
        self.keys = self.engine.e.key.get_pressed()
        
        for event in self.events:
            if event.type == self.engine.e.QUIT or self.keys[self.engine.e.K_ESCAPE]:
                self.engine.running = False
                break

            if event.type == self.engine.SCREEN_UPDATE:
                self.engine.update()

    def handle_keys(self) -> None:
        for key, direction in self.engine.key_map.items():
            if self.keys[key] and direction + self.engine.snake.head != self.engine.snake.body[1]: # check if direction is valid and not to the snake's neck
                self.engine.snake.direction = direction
                break
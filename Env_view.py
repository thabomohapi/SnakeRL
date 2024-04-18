class GameView:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.font = self.engine.e.font.Font(None, 36)
        self.color = (255, 215, 0)
        self.timer_position = (self.engine.width // 3 - 150, 20)
        self.score_position = (self.engine.width // 2.5, 20)
        self.high_score_position = (self.engine.width // 2 + 150, 20)
        self.high_score = self.engine.snake.score
        self.background = self.engine.load_image("assets/bg.png")

    def draw(self) -> None:
        # Draw the game state to the screen
        # ...
        self.clear_screen()
        self.draw_background()
        self.draw_timer()
        self.draw_score()
        self.draw_high_score()
        self.draw_entities()

    def clear_screen(self) -> None:
        self.engine.screen.fill((0, 0, 0))

    def draw_background(self) -> None:
        self.engine.screen.blit(self.background, (0, 0))

    def draw_entities(self) -> None:
        for fruit in self.engine.fruits:
            fruit.draw()
        self.engine.snake.draw()
        for obstacle in self.engine.obstacles:
            obstacle.draw()

    def draw_timer(self) -> None:
        elapsed_time = (self.engine.e.time.get_ticks() - self.engine.start_timer) // 1000
        timer_text = f"Time: {elapsed_time}"
        timer_surface = self.font.render(timer_text, True, self.color)
        timer_rect = timer_surface.get_rect(center=(self.timer_position[0], self.timer_position[1]))
        self.engine.screen.blit(timer_surface, timer_rect)

    def draw_score(self) -> None:
        score_text = f"Score: {self.engine.snake.score}"
        score_surface = self.font.render(score_text, True, self.color)
        score_rect = score_surface.get_rect(center=(self.score_position[0], self.score_position[1]))
        self.engine.screen.blit(score_surface, score_rect)

    def draw_high_score(self) -> None:
        high_score_text = f"High Score: {self.high_score}"
        high_score_surface = self.font.render(high_score_text, True, self.color)
        high_score_rect = high_score_surface.get_rect(center=(self.high_score_position[0], self.high_score_position[1]))
        self.engine.screen.blit(high_score_surface, high_score_rect)

    def update_high_score(self) -> None:
        if self.engine.snake.score > self.high_score:
            self.high_score = self.engine.snake.score
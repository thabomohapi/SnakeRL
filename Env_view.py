class Renderer:
    def __init__(self, engine) -> None:
        self.engine = engine
        self.font = self.engine.e.font.Font(None, 36)
        self.color = (255, 215, 0)
        self.high_score = self.engine.snake.score
        self.background = self.engine.load_image("assets/bg.png")
        self.side_panel_width = self.engine.side_panel_width
        self.game_area_width = self.engine.width - self.side_panel_width
        self.ui_elements = ['timer', 'score', 'high_score']
        self.calculate_ui_positions()

    def draw(self) -> None:
        # Draw the environment state to the screen
        # ...
        self.clear_screen()
        self.draw_game_area()
        self.draw_side_panel()

    def draw_game_area(self) -> None:
        # set the clipping area to the game area only
        self.engine.screen.set_clip(0, 0, self.game_area_width, self.engine.height)
        self.draw_background()
        self.draw_entities()
        # remove the clipping area
        self.engine.screen.set_clip(None)

    def draw_side_panel(self) -> None:
        # set the clipping area to the side_panel area only
        self.engine.screen.set_clip(self.game_area_width, 0, self.side_panel_width, self.engine.height)
        # Draw the side panel background
        self.engine.screen.fill((30, 30, 30), (self.game_area_width, 0, self.side_panel_width, self.engine.height))
        # draw UI elements
        self.draw_timer()
        self.draw_score()
        self.draw_high_score()
        # remove the clipping area
        self.engine.screen.set_clip(None)

    def calculate_ui_positions(self) -> None:
        # calculate the vertical center positions for the UI elements
        panel_height = self.engine.height
        num_elements = len(self.ui_elements)
        element_height = panel_height // (num_elements + 1)
        self.timer_position = (self.game_area_width + self.side_panel_width // 2, element_height * 0.5)
        self.score_position = (self.game_area_width + self.side_panel_width // 2, element_height * 1)
        self.high_score_position = (self.game_area_width + self.side_panel_width // 2, element_height * 1.5)

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
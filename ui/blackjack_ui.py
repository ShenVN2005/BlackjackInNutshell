import pygame
import os
from render.card_drawer import draw_card, CARD_WIDTH
from envs.blackjack_env import score_hand

BG_COLOR = (34, 139, 34)
TEXT_COLOR = (255, 255, 255)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

class Slider:
    def __init__(self, x, y, width, max_val):
        self.rect = pygame.Rect(x, y, width, 6)
        self.max_val = max_val
        self.val = 10
        self.dragging = False
    
    def update_max(self, max_val):
        self.max_val = max(10, max_val)
        if self.val > self.max_val:
            self.val = self.max_val
            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                thumb_rect = self._get_thumb_rect()
                if thumb_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                    self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                rel_x = event.pos[0] - self.rect.x
                ratio = max(0.0, min(1.0, rel_x / self.rect.width))
                self.val = int(10 + ratio * (self.max_val - 10))
                self.val = round(self.val / 10) * 10
                
    def _get_thumb_rect(self):
        if self.max_val <= 10:
            ratio = 0
        else:
            ratio = (self.val - 10) / (self.max_val - 10)
        thumb_x = self.rect.x + ratio * self.rect.width - 8
        thumb_y = self.rect.y - 5
        return pygame.Rect(thumb_x, thumb_y, 16, 16)
        
    def draw(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), self.rect, border_radius=3)
        thumb_rect = self._get_thumb_rect()
        pygame.draw.ellipse(surface, (0, 210, 255), thumb_rect)

class VolumeSlider:
    def __init__(self, x, y, width, initial_val=0.4):
        self.rect = pygame.Rect(x, y, width, 8)
        self.val = initial_val  
        self.dragging = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                
                mouse_pos = event.pos
                thumb_rect = self._get_thumb_rect()
                if thumb_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                    self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                rel_x = event.pos[0] - self.rect.x
                self.val = max(0.0, min(1.0, rel_x / self.rect.width))
                
    def _get_thumb_rect(self):
        thumb_x = self.rect.x + (self.val * self.rect.width) - 10
        thumb_y = self.rect.y - 6
        return pygame.Rect(thumb_x, thumb_y, 20, 20)
        
    def draw(self, surface):
        
        pygame.draw.rect(surface, (100, 100, 100), self.rect, border_radius=4)
        
        fill_rect = pygame.Rect(self.rect.x, self.rect.y, self.val * self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (255, 215, 0), fill_rect, border_radius=4)
        
        thumb_rect = self._get_thumb_rect()
        pygame.draw.ellipse(surface, (255, 255, 255), thumb_rect)
class BlackjackUI:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Blackjack in Nutshell :v")
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.volume_slider = VolumeSlider(self.width // 2 - 150, self.height // 2, 300, initial_val=0.4)
        
        try:
            bg = pygame.image.load(os.path.join(ASSETS_DIR, "Background.png")).convert()
            self.bg_img = pygame.transform.scale(bg, (width, height))
        except FileNotFoundError:
            self.bg_img = None
            
        try:
            bg2 = pygame.image.load(os.path.join(ASSETS_DIR, "Background2.png")).convert()
            self.play_bg_img = pygame.transform.scale(bg2, (width, height))
        except FileNotFoundError:
            self.play_bg_img = None
            
        try:
            chips = pygame.image.load(os.path.join(ASSETS_DIR, "DecoChips.png")).convert_alpha()
            self.chips_img = pygame.transform.scale(chips, (320, 160))
        except FileNotFoundError:
            self.chips_img = None
            
        self.slider = Slider(90, self.height - 30, 200, 1000)
        
        self._init_menu_buttons()
        self._init_game_buttons()
        self._init_confirm_buttons()
        try:
            icon_path = os.path.join(ASSETS_DIR, "setting.png")
            self.settings_icon = pygame.image.load(icon_path).convert_alpha()
            self.settings_icon = pygame.transform.scale(self.settings_icon, (40, 40))
        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file assets/setting.png")
            self.settings_icon = None
        
    def _init_menu_buttons(self):
        btn_width = 250
        btn_height = 60
        start_y = 300
        cx = self.width // 2 - btn_width // 2
        
        self.btn_play = pygame.Rect(cx, start_y, btn_width, btn_height)
        self.btn_settings = pygame.Rect(cx, start_y + 100, btn_width, btn_height)
        self.btn_exit = pygame.Rect(cx, start_y + 200, btn_width, btn_height)
        self.btn_back = pygame.Rect(cx, self.height // 2 + 100, btn_width, btn_height)
        
    def _init_game_buttons(self):
        gb_width = 110
        gb_height = 40
        gb_x = self.width // 2 - (gb_width*4 + 30) // 2
        gb_y = self.height - 80
        
        self.btn_hit = pygame.Rect(gb_x, gb_y, gb_width, gb_height)
        self.btn_stand = pygame.Rect(gb_x + gb_width + 10, gb_y, gb_width, gb_height)
        self.btn_surrender = pygame.Rect(gb_x + (gb_width + 10)*2, gb_y, gb_width, gb_height)
        self.btn_cashout = pygame.Rect(gb_x + (gb_width + 10)*3, gb_y, gb_width, gb_height)
        self.btn_game_settings = pygame.Rect(10, 10, 140, 40)
        self.btn_gear = pygame.Rect(self.width - 60, 20, 40, 40)
        
    def _init_confirm_buttons(self):
        self.btn_yes = pygame.Rect(self.width//2 - 140, self.height//2 + 10, 120, 50)
        self.btn_no = pygame.Rect(self.width//2 + 20, self.height//2 + 10, 120, 50)
        self.btn_continue = pygame.Rect(self.width//2 - 100, self.height - 200, 200, 60)
        self.btn_confirm_bet = pygame.Rect(self.width // 2 - 100, self.height - 100, 200, 60)
        
    def _draw_button(self, rect, text, border_radius=15, bg_color=(50, 205, 50)):
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=border_radius)
        pygame.draw.rect(self.screen, (0, 100, 0), rect, width=4, border_radius=border_radius)
        t_surf = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.centery - t_surf.get_height()//2))

    def draw_menu(self):
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BG_COLOR)
            
        title_font = pygame.font.SysFont("Arial", 70, bold=True)
        title = title_font.render("BLACKJACK", True, (255, 215, 0))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 120))
        
        self._draw_button(self.btn_play, "PLAY",)
        self._draw_button(self.btn_settings, "SETTINGS",)
        self._draw_button(self.btn_exit, "EXIT",)
        
        pygame.display.flip()

    def draw_settings(self):
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BG_COLOR)
            
        title_font = pygame.font.SysFont("Arial", 50, bold=True)
        title_surf = title_font.render("SETTINGS", True, (255, 215, 0))
        self.screen.blit(title_surf, (self.width//2 - title_surf.get_width()//2, 150))
        vol_label = self.font.render(f"Music Volume: {int(self.volume_slider.val * 100)}%", True, (255, 255, 255))
        self.screen.blit(vol_label, (self.width//2 - vol_label.get_width()//2, self.height//2 - 50))
        self.volume_slider.draw(self.screen)
        
        self._draw_button(self.btn_back, "BACK")
        pygame.display.flip()
        
    def draw_confirm_screen(self):
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BG_COLOR)
            
        dialog = pygame.Rect(self.width//2 - 250, self.height//2 - 150, 500, 250)
        pygame.draw.rect(self.screen, (20, 20, 20), dialog, border_radius=15)
        pygame.draw.rect(self.screen, (100, 100, 100), dialog, width=3, border_radius=15)
        
        font = pygame.font.SysFont("Arial", 40, bold=True)
        text = font.render("Take Cash and leave?", True, (255, 255, 255))
        self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2 - 80))
        
        self._draw_button(self.btn_yes, "YES", bg_color=(150, 40, 40))
        self._draw_button(self.btn_no, "NO", bg_color=(40, 150, 40))
        
        pygame.display.flip()

    def draw_summary(self, balances):
        if self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BG_COLOR)
            
        title = pygame.font.SysFont("Arial", 60, bold=True).render("TABLE SUMMARY", True, (255, 215, 0))
        self.screen.blit(title, (self.width//2 - title.get_width()//2, 120))
        
        names = ["You", "Random", "MonteCarlo+Martingale"]
        start_y = 250
        
        for i in range(3):
            profit = balances[i] - 2000.0
            
            if profit > 0:
                p_text = f"Won +${int(profit)}"
                color = (50, 255, 50)
            elif profit < 0:
                p_text = f"Lost -${abs(int(profit))}"
                color = (255, 50, 50)
            else:
                p_text = "$0"
                color = (200, 200, 200)
                
            entry = f"{names[i]}:   {p_text}"
            surf = self.font.render(entry, True, color)
            self.screen.blit(surf, (self.width//2 - surf.get_width()//2, start_y + (i * 80)))
            
        self._draw_button(self.btn_continue, "CONTINUE")
        pygame.display.flip()
        
    def draw_betting(self, balances):
        if hasattr(self, 'play_bg_img') and self.play_bg_img:
            self.screen.blit(self.play_bg_img, (0, 0))
        elif self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BG_COLOR)
            
        # Draw player names and balances in the background
        positions = [
            (self.width // 2 - 75, self.height - 300, "Player"),
            (150, self.height - 400, "Random"),
            (self.width - 200, self.height - 400, "MonteCarlo")
        ]
        for p_idx in range(3):
            x, y, label = positions[p_idx]
            self._draw_text(label, x, y - 30, TEXT_COLOR)
            self._draw_text(f"Bal: ${int(balances[p_idx])}", x, y - 60, TEXT_COLOR, font=self.small_font)
            
        self._draw_text("Dealer", self.width // 2 - 50, 30, TEXT_COLOR)
            
        self._draw_bet_panel(balances[0])
        self._draw_button(self.btn_confirm_bet, "DEAL CARDS", border_radius=8, bg_color=(255, 140, 0))
        pygame.display.flip()
        
    def _draw_bet_panel(self, player_balance):
        self.slider.update_max(player_balance)
        bx, by = 0, self.height - 160
        if self.chips_img:
            self.screen.blit(self.chips_img, (bx, by))
        else:
            pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(bx, by, 320, 160), border_radius=15)
            pygame.draw.rect(self.screen, (200, 150, 50), pygame.Rect(bx, by, 320, 160), width=3, border_radius=15)
            
        self._draw_text(f"Your Bet: ${int(self.slider.val)}", bx + 100, by + 90, (0, 210, 255), self.font)
        self.slider.draw(self.screen)
        
    def draw_board(self, env_state, balances, current_player, current_bets=None):
        if hasattr(self, 'play_bg_img') and self.play_bg_img:
            self.screen.blit(self.play_bg_img, (0, 0))
        elif self.bg_img:
            self.screen.blit(self.bg_img, (0, 0))
        else:
            self.screen.fill(BG_COLOR)
            
        self.slider.update_max(balances[0])
            
        dealer_hand = env_state.dealer_hand
        hands = env_state.hands
        
        dealer_x = self.width // 2 - 50
        dealer_y = 60
        self._draw_text("Dealer", dealer_x, dealer_y - 30)
        
        dealer_visible_cards = [c for i, c in enumerate(dealer_hand) if not (i == 1 and current_player < 3)]
        dealer_score = score_hand(dealer_visible_cards)
        score_text = f"Score: {dealer_score}" if current_player < 3 else f"Score: {dealer_score}"
        self._draw_text(score_text, dealer_x, dealer_y + 110, color=(200, 255, 200), font=self.small_font)
        
        for i, val in enumerate(dealer_hand):
            hidden = (i == 1 and current_player < 3)
            draw_card(self.screen, self.font, dealer_x + (i * 30), dealer_y, val, hidden=hidden)
            
        positions = [
            (self.width // 2 - 75, self.height - 300, "Player"),
            (150, self.height - 400, "Random"),
            (self.width - 250, self.height - 400, "MonteCarlo")
        ]
        
        for p_idx in range(3):
            x, y, label = positions[p_idx]
            color = (255, 255, 0) if current_player == p_idx else TEXT_COLOR
            self._draw_text(label, x, y - 30, color)
            self._draw_text(f"Bal: ${int(balances[p_idx])}", x, y - 60, TEXT_COLOR, font=self.small_font)
            
            
            score_val = score_hand([c for c in hands[p_idx] if c != "HIDDEN"])
            self._draw_text(f"Score: {score_val}", x, y + 150, color=(200, 255, 200), font=self.small_font)
            
            if current_bets is not None and p_idx < len(current_bets):
                self._draw_text(f"Bet: ${int(current_bets[p_idx])}", x - 90, y, color=(255, 215, 0), font=self.small_font)
            
            for i, val in enumerate(hands[p_idx]):
                draw_card(self.screen, self.font, x + (i * 25), y, val)
                
            if env_state.surrendered[p_idx]:
                self._draw_text("SURRENDERED", x, y + 180, (255, 50, 50), font=self.font)
            elif score_val > 21:
                self._draw_text("BUST", x, y + 180, (255, 50, 50), font=self.font)
            elif current_player >= 3:
                d_score = score_hand(dealer_hand)
                if d_score > 21:
                    self._draw_text("WIN", x, y + 180, (50, 255, 50), font=self.font)
                elif score_val > d_score:
                    self._draw_text("WIN", x, y + 180, (50, 255, 50), font=self.font)
                elif score_val == d_score:
                    self._draw_text("DRAW", x, y + 180, (200, 200, 200), font=self.font)
                else:
                    self._draw_text("LOSE", x, y + 180, (255, 50, 50), font=self.font)
                
        self._draw_text(f"Cards in Deck: {len(env_state.deck)}", 30, 30, font=self.small_font)
        
        self._draw_bet_panel(balances[0])
        
        if current_player == 0:
            for r, text in [(self.btn_hit, "HIT"), (self.btn_stand, "STAND"), (self.btn_surrender, "SURR"), (self.btn_cashout, "CASH OUT")]:
                color = (34, 139, 34) if text == "HIT" else ((139, 34, 34) if text in ["SURR", "CASH OUT"] else (60, 60, 60))
                pygame.draw.rect(self.screen, color, r, border_radius=8)
                pygame.draw.rect(self.screen, (255, 255, 255), r, width=2, border_radius=8)
                t_surf = self.small_font.render(text, True, (255, 255, 255))
                self.screen.blit(t_surf, (r.centerx - t_surf.get_width()//2, r.centery - t_surf.get_height()//2))
                
        if self.settings_icon:
            self.screen.blit(self.settings_icon, (self.btn_gear.x, self.btn_gear.y))    
            
        pygame.display.flip()
        
    def _draw_text(self, text, x, y, color=TEXT_COLOR, font=None):
        f = font if font else self.font
        surface = f.render(text, True, color)
        self.screen.blit(surface, (x, y))

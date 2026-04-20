import pygame
import sys
import random

from envs.blackjack_env import MultiPlayerBlackjackEnv
from agent.random_agent import RandomAgent
from agent.monte_carlo_agent import MonteCarloAgent
from ui.blackjack_ui import BlackjackUI

def train_agents(env, random_agent, mc_agent, episodes=20000):
    print(f"Training Agents for {episodes} episodes without UI...")
    for _ in range(episodes):
        obs, info = env.reset()
        done = False
        mc_episode = []
        
        while not done:
            cp = info['current_player']
            if cp == 0:
                action = env.action_space.sample()
                obs, reward, done, _, info = env.step(action)
            elif cp == 1:
                action = random_agent.get_action(obs, is_training=True)
                obs, reward, done, _, info = env.step(action)
            elif cp == 2:
                s2 = obs
                a2 = mc_agent.get_action(s2, is_training=True)
                mc_episode.append((s2, a2))
                obs, reward, done, _, info = env.step(a2)
                    
        rewards = info['rewards']
        if mc_episode:
            mc_agent.update(mc_episode, rewards[2])

    print("Training complete.")

def main():
    env = MultiPlayerBlackjackEnv()
    random_agent = RandomAgent()
    mc_agent = MonteCarloAgent()
    
    train_agents(env, random_agent, mc_agent, 20000)
    
    ui = BlackjackUI(width=1280, height=720)
    clock = pygame.time.Clock()
    
    balances = [2000.0, 2000.0, 2000.0]
    current_bets = [10, 10, 10]
    agent1_streak = 0
    agent2_lose_streak = 0
    
    obs, info = env.reset()
    done = False
    
    state = "MENU"
    running = True
    
    while running:
        
        if state == "MENU":
            ui.draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ui.btn_play.collidepoint(event.pos):
                        state = "BETTING"
                    elif ui.btn_settings.collidepoint(event.pos):
                        state = "SETTINGS"
                    elif ui.btn_exit.collidepoint(event.pos):
                        running = False
            clock.tick(30)
            
        elif state == "SETTINGS":
            ui.draw_settings()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ui.btn_back.collidepoint(event.pos):
                        state = "MENU"
            clock.tick(30)
            
        elif state == "CONFIRM_CASHOUT":
            ui.draw_confirm_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ui.btn_yes.collidepoint(event.pos):
                        state = "SUMMARY"
                    elif ui.btn_no.collidepoint(event.pos):
                        state = "GAME"
            clock.tick(30)
            
        elif state == "SUMMARY":
            ui.draw_summary(balances)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ui.btn_continue.collidepoint(event.pos):
                        print(f"\n[!] ${balances[0]}!\n")
                        balances = [1000.0, 1000.0, 1000.0]
                        current_bets = [10, 10, 10]
                        agent1_streak = 0
                        agent2_lose_streak = 0
                        obs, info = env.reset()
                        state = "MENU"
            clock.tick(30)
            
        elif state == "BETTING":
            ui.draw_betting(balances)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                ui.slider.handle_event(event)
                
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if ui.btn_confirm_bet.collidepoint(event.pos):
                        amount0 = ui.slider.val
                        amount1 = 10
                        target2 = 10 * (2 ** agent2_lose_streak)
                        amount2 = target2 if target2 < balances[2] else 10
                        current_bets = [amount0, amount1, amount2]
                        state = "GAME"
            clock.tick(30)
            
        elif state == "GAME":
            cp = env.current_player
            
            if done:
                ui.draw_board(env, balances, 4, current_bets)
                pygame.display.flip()
                pygame.time.delay(5000)
                
                rewards = info['rewards']
                for i in range(3):
                    gain = rewards[i] * current_bets[i]
                    balances[i] += gain
                    
                    if rewards[i] > 0:
                        if i == 1: agent1_streak += 1
                        if i == 2: agent2_lose_streak = 0
                    elif rewards[i] < 0:
                        if i == 1: agent1_streak = 0
                        if i == 2: agent2_lose_streak += 1
                    
                obs, info = env.reset()
                done = False
                state = "BETTING"
                continue
                
            ui.draw_board(env, balances, cp, current_bets)
            
            if cp == 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if ui.btn_hit.collidepoint(event.pos):
                            obs, _, done, _, info = env.step(1)
                        elif ui.btn_stand.collidepoint(event.pos):
                            obs, _, done, _, info = env.step(0)
                        elif ui.btn_surrender.collidepoint(event.pos):
                            obs, _, done, _, info = env.step(2)
                        elif ui.btn_cashout.collidepoint(event.pos):
                            state = "CONFIRM_CASHOUT"
                            
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        
                pygame.time.delay(1000) 
                
                if cp == 1:
                    a1 = random_agent.get_action(obs, is_training=False)
                    obs, _, done, _, info = env.step(a1)
                elif cp == 2:
                    a2 = mc_agent.get_action(obs, is_training=False)
                    obs, _, done, _, info = env.step(a2)
                    
            clock.tick(30)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

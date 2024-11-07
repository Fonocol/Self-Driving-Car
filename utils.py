import pygame
import matplotlib.pyplot as plt
from IPython import display
import numpy as np  
import math     


def scale_img(img,factor):
  size = round(img.get_width()*factor),round(img.get_height()*factor)
  return pygame.transform.scale(img,size)


def blit_rotate_center(win,image,top_left,angle):
  rotated_image = pygame.transform.rotate(image,angle)
  new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
  win.blit(rotated_image,new_rect.topleft)


def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title('Training...')
    plt.xlabel('Number of games')
    plt.ylabel('Score')
    plt.plot(scores, label="Score")
    plt.plot(mean_scores, label="Mean Score")
    plt.ylim(ymin=0)
    plt.text(len(scores) - 1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores) - 1, mean_scores[-1], str(mean_scores[-1]))
    plt.legend(loc="upper left")  # ajout d'une légende pour différencier les courbes
    plt.gcf().canvas.draw()  # force le rendu
    plt.pause(0.1)  # courte pause pour afficher


def calculate_reward(car, action, finish_position, checkpoints, width, height, max_time=500):
    ALPHA = 5     # Poids pour la progression
    BETA = 1      # Poids pour la vitesse
    GAMMA = 2     # Poids pour l'orientation vers le prochain checkpoint
    DELTA = -10   # Pénalité pour collision
    TIMEOUT_PENALTY = -15  # Pénalité pour dépassement de temps

    # 1. Récompense pour la progression par rapport au dernier checkpoint franchi
    checkpoint_idx = car.get_current_checkpoint_index()
    if checkpoint_idx < len(checkpoints) - 1:
        next_checkpoint = checkpoints[checkpoint_idx + 1]
        finish_distance = np.linalg.norm(np.array([car.x, car.y]) - np.array(next_checkpoint))
        max_distance = np.sqrt(width**2 + height**2)
        reward_progress = ALPHA * (1 - finish_distance / max_distance)
    else:
        reward_progress = 0  # À l’arrivée, pas de progression nécessaire

    # 2. Récompense pour l'orientation vers le prochain checkpoint
    angle_to_checkpoint = math.atan2(next_checkpoint[1] - car.y, next_checkpoint[0] - car.x)
    angle_diff = abs(car.angle - math.degrees(angle_to_checkpoint)) % 180
    reward_orientation = GAMMA * (1 - angle_diff / 180)

    # 3. Récompense ajustée pour la vitesse
    speed = car.vel / car.max_vel
    ideal_speed = 0.5 if checkpoint_idx < len(checkpoints) // 2 else 0.7  # Vitesse plus faible dans les virages
    reward_speed = -BETA * abs(speed - ideal_speed)

    # 4. Pénalité de collision et ajustement du temps
    reward_collision = 0
    if car.is_collision():
        reward_collision = DELTA
        car.time_left -= 3  # Réduire plus de temps en cas de collision fréquente

    # 5. Timeout si le temps est écoulé
    game_over = False
    reward_timeout = 0
    if car.time_left <= 0:
        game_over = True
        reward_timeout = TIMEOUT_PENALTY

    # 6. Récompense pour avoir terminé le parcours
    if car.game_finished():
        game_over = True
        reward_progress += 20  # Bonus pour avoir terminé le parcours

    # Calcul de la récompense totale
    reward = reward_progress + reward_speed + reward_orientation + reward_collision + reward_timeout
    return reward, game_over







  #def play_step(self, action, win=WIN, images=images):
    # Boucle de mise à jour
    #self._update_ui(win, images)  # Mise à jour de l'interface graphique
    # Mise à jour des événements
    #for event in pygame.event.get():
        #if event.type == pygame.QUIT:
            #pygame.quit()
            #return 0, True, self.score  # Fin du jeu si la fenêtre est fermée

    # Application de l'action de l'IA
    #self.move_IA_Car(action)

    # Vérification des collisions
    #reward = 0
    #game_over = False

    #if self.is_collision() != None:
        #self.score += 2/FPS
        #print("danger")
        #reward = -10
        #if self.score >=4*FPS:
          #game_over = True
          #reward = -20
        #return reward, game_over, self.score
     

    # Vérification de la ligne d'arrivée
    #if self.game_finished():
        #game_over = True
        #reward = 10
    
    #self.clock.tick(FPS)
    #return reward, game_over, self.score



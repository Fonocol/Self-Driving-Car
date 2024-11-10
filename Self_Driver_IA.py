import pygame
import time
import math
from utils import scale_img,blit_rotate_center
from Collection import Collectable
import random
from enum import Enum
import numpy as np


import pickle
import os

with open('.model/random_forest_model.pkl', 'rb') as f:
    loaded_model = pickle.load(f)

pygame.init()
#font = pygame.font.Font('arial.ttf', 25)
font = pygame.font.SysFont(None, 24)

TRACK = scale_img(pygame.image.load('./imgs/map.png'), 0.55)
TOITURE = scale_img(pygame.image.load('./imgs/toiture.png'), 0.55)
PLANTES = scale_img(pygame.image.load('./imgs/plantes.png'), 0.55)
TRACK_BORDER = scale_img(pygame.image.load('./imgs/masck.png'), 0.55)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load('./imgs/finish.png')
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (317, 501)

RED_CAR = scale_img(pygame.image.load('./imgs/red-car.png'),0.8)
GREEN_CAR = scale_img(pygame.image.load('./imgs/green-car.png'),0.8)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CAR GAME!")

RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLANC =(255, 255, 255)

HUMAIN_POSITION = [(475, 518), (585, 515), (700, 513), (797, 502), (823, 457), (828, 387), (778, 340), (778, 340), (692, 376), (605, 435), (532, 384), (543, 313), (540, 239), (559, 183), (616, 190), (640, 247), (688, 286), (753, 251), (811, 199), (832, 124), (818, 76), (761, 43), (705, 62), (662, 92), (610, 109), (568, 90), (531, 50), (476, 38), (447, 80), (379, 108), (435, 137), (445, 202), (468, 271), (474, 340), (440, 380), (367, 369), (326, 280), (300, 194), (309, 134), (326, 74), (306, 34), (213, 28), (107, 37), (53, 62), (53, 123), (65, 164), (133, 215), (203, 247), (253, 294), (283, 354), (277, 411), (217, 451), (176, 412), (144, 332), (99, 273), (51, 309), (50, 381), (53, 446), (82, 507), (189, 521)]


FPS = 25
images = [(TRACK,(0,0)),(FINISH,FINISH_POSITION)] #,(TRACK_BORDER,(0,0))


class Car:
  def __init__(self,max_vel,rotation_vel):
    self.img = self.IMG
    self.max_vel = max_vel
    self.vel = 0
    self.angle = -90
    self.rotation_vel = rotation_vel
    self.x, self.y = self.START_POS
    self.acceleration = 0.1
    self.score = 0
    self.time = 0
    self.clock = pygame.time.Clock()
    self.client = None
    self._place_client()
    

  def rotate(self,left=False,right=False):
    if left:
      self.angle += self.rotation_vel
    elif right:
      self.angle -= self.rotation_vel

  def draw(self,win):
    blit_rotate_center(win,self.img,(self.x,self.y),self.angle)
    self.client.draw(win)

  def move_forward(self):
    self.vel = min(self.vel + self.acceleration,self.max_vel)
    self.move()

  def move_backward(self):
    self.vel = max(self.vel - self.acceleration,-self.max_vel/2)
    self.move()

  def move(self):
    radians = math.radians(self.angle)
    vertical = math.cos(radians)*self.vel
    horizontal = math.sin(radians)*self.vel

    self.y -= vertical
    self.x -= horizontal

  def reduce_speed(self):
    self.vel = max(self.vel - self.acceleration/2,0)
    self.move()

  def collide(self,mask,x=0,y=0):
    car_mask = pygame.mask.from_surface(self.img)
    offset = (int(self.x-x),int(self.y-y))

    point_de_collision = mask.overlap(car_mask,offset)
    return point_de_collision
  
  def bounce(self):
    self.vel = -self.vel
    self.move()

  def reset(self):
    self.x, self.y = self.START_POS
    self.angle = 0
    self.vel = 0
    self.score = 0
    self.time = 0
    self.client = None
    self._place_client()

  def _place_client(self):
        i = random.randint(0, len(HUMAIN_POSITION)-1)
        x,y = HUMAIN_POSITION[i]
        self.client = Collectable(x, y)
  

class CarAI(Car):
  IMG = GREEN_CAR
  START_POS = (190, 513)

  def _update_ui(self,win,images):
    for img,pos in images:
      win.blit(img,pos)

    super().draw(win)
    #debug
    self.debug(win)
    win.blit(TOITURE, (0,0))
    win.blit(PLANTES, (0,0))
    text = font.render("Score: " + str(self.score)+ " Time: "+str(self.time), True, BLANC)
    win.blit(text, [0,0])
    text = font.render("GARA DE CALAIS VILLE" , True, BLANC)
    win.blit(text, [317, 440])
    pygame.display.update()


  def move_IA_Car(self, action):
    # Action [1,0,0,0] : Avancer tout droit
    if np.array_equal(action, [1, 0, 0,0]):
        self.move_forward()
    # Action [0,1,0] : Tourner à droite
    elif np.array_equal(action, [0, 1, 0,0]):
        self.rotate(right=True)
        self.move_forward()
    # Action [0,0,1] : Tourner à gauche
    elif np.array_equal(action, [0, 0, 1,0]):
        self.rotate(left=True)
        self.move_forward()
    # Action [0,0,0,1] : Reculer
    elif np.array_equal(action, [0, 0, 0, 1]):
        self.move_backward()

    else:
        self.reduce_speed()

    

  def game_finished(self):
      AI_finish_point_collide = self.collide(FINISH_MASK,*FINISH_POSITION)
      if AI_finish_point_collide != None:
          if AI_finish_point_collide[1] == 0:
            self.bounce()
          else:
            print("finish")
            return True

      return False

  def is_collision(self):
      border_point_collide = self.collide(TRACK_BORDER_MASK)
      if border_point_collide != None:
        #print("zonne interdite")
        if self.x > WIDTH-20 or self.x < 20 or self.y > HEIGHT-10 or self.y < 5:
            self.bounce()
        
      return border_point_collide   



  def play_step(self, action, win=WIN, images=images):
    
    self._update_ui(win, images)  # Mise à jour de l'interface graphique
  
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return 0, True, self.score  # Fin du jeu si la fenêtre est fermée


    self.client.attach_to_car(FINISH_POSITION,self)  # Attache si proche
    self.client.update_position(self)  # Suivre la voiture si collecté
    self.client.detach_at_destination(FINISH_POSITION,self)  # Détache si à la destination
    if self.client.depart == False and self.client.arrive == True:
       self._place_client()
       self.score +=1

    # Application de l'action de l'IA
    self.move_IA_Car(action)

    game_over = False

    if self.is_collision() != None:
        self.time += 2/FPS
        if self.time >=4*FPS:
            game_over = True
        return game_over, self.score
     

    # Vérification de la ligne d'arrivée
    if self.game_finished():
        game_over = True

    
    self.clock.tick(FPS)
    return game_over, self.score

  def debug(self,win):
      front_dist,p1 = self.get_distance_in_direction("front")
      back_dist,p2 = self.get_distance_in_direction("back")
      left_dist,p3 = self.get_distance_in_direction("left")
      right_dist,p4 = self.get_distance_in_direction("right")
      left_font_dist,p5 = self.get_distance_in_direction("left_font")
      right_font_dist,p6 = self.get_distance_in_direction("right_font")
      left_back_dist,p7 = self.get_distance_in_direction("left_back")
      right__back_dist,p8 = self.get_distance_in_direction("right__back")

      pygame.draw.circle(win, RED, p1, 10)
      text_f = font.render("F", True, BLANC)
      win.blit(text_f, (p1[0] - text_f.get_width() // 2, p1[1] - text_f.get_height() // 2))

      pygame.draw.circle(win, RED, p2, 10)
      text_b = font.render("B", True, BLANC)
      win.blit(text_b, (p2[0] - text_b.get_width() // 2, p2[1] - text_b.get_height() // 2))

      pygame.draw.circle(win, BLUE, p3, 10)
      text_l = font.render("L", True, BLANC)
      win.blit(text_l, (p3[0] - text_l.get_width() // 2, p3[1] - text_l.get_height() // 2))

      pygame.draw.circle(win, BLUE, p4, 10)
      text_r = font.render("R", True, BLANC)
      win.blit(text_r, (p4[0] - text_r.get_width() // 2, p4[1] - text_r.get_height() // 2))

      pygame.draw.circle(win, YELLOW, p5, 10)
      text_r = font.render("LF", True, BLANC)
      win.blit(text_r, (p5[0] - text_r.get_width() // 2, p5[1] - text_r.get_height() // 2))

      pygame.draw.circle(win, YELLOW, p6, 10)
      text_r = font.render("RF", True, BLANC)
      win.blit(text_r, (p6[0] - text_r.get_width() // 2, p6[1] - text_r.get_height() // 2))

      pygame.draw.circle(win, YELLOW, p7, 10)
      text_r = font.render("LB", True, BLANC)
      win.blit(text_r, (p7[0] - text_r.get_width() // 2, p7[1] - text_r.get_height() // 2))

      pygame.draw.circle(win, YELLOW, p8, 10)
      text_r = font.render("RB", True, BLANC)
      win.blit(text_r, (p8[0] - text_r.get_width() // 2, p8[1] - text_r.get_height() // 2))

      #line
      pygame.draw.line(win, RED, FINISH_POSITION , (self.x, self.y), 1)
    


  def get_state(self):
    front_dist,p1 = self.get_distance_in_direction("front")
    back_dist,p2 = self.get_distance_in_direction("back")
    left_dist,p3 = self.get_distance_in_direction("left")
    right_dist,p4 = self.get_distance_in_direction("right")
    left_font_dist,p5 = self.get_distance_in_direction("left_font")
    right_font_dist,p6 = self.get_distance_in_direction("right_font")
    left_back_dist,p7 = self.get_distance_in_direction("left_back")
    right__back_dist,p8 = self.get_distance_in_direction("right__back")
    
    angle = (self.angle % 360) / 180 - 1
    speed = self.vel / self.max_vel
    collision = False
    if self.is_collision():
       collision = True
    finish_distance = np.linalg.norm(
        np.array([self.x, self.y]) - np.array(FINISH_POSITION)
    )
    normalized_finish_distance = finish_distance / np.sqrt(WIDTH**2 + HEIGHT**2)
    state = [
        front_dist,
        back_dist,
        left_dist,
        right_dist,
        left_font_dist,
        right_font_dist,
        left_back_dist,
        right__back_dist,
        angle,
        speed,
        collision,
        normalized_finish_distance,
    ]

    return np.array(state, dtype=np.float32)

  # Méthode pour obtenir la distance dans une direction donnée
  def get_distance_in_direction(self, direction):
    radians = math.radians(self.angle)
    if direction == "front":
        dx, dy = math.cos(radians + math.pi / 2), -math.sin(radians + math.pi / 2)
    elif direction == "back":
        dx, dy = math.cos(radians - math.pi / 2), -math.sin(radians - math.pi / 2)
    elif direction == "left":
        dx, dy = math.cos(radians), -math.sin(radians)
    elif direction == "right":
        dx, dy = -math.cos(radians), math.sin(radians)
    elif direction == "left_font":
        dx, dy = math.cos(radians + 3*math.pi / 4), -math.sin(radians + 3*math.pi / 4)
    elif direction == "right_font":
        dx, dy = math.cos(radians + math.pi / 4), -math.sin(radians + math.pi / 4)
    elif direction == "left_back":
        dx, dy = math.cos(radians - math.pi / 4), -math.sin(radians - math.pi / 4)
    elif direction == "right__back":
        dx, dy = math.cos(radians - 3*math.pi / 4), -math.sin(radians - 3*math.pi / 4)
        
    
    # distance à l'obstacle
    x, y, dist = self.x, self.y, 0
    while 0 <= int(x) < WIDTH and 0 <= int(y) < HEIGHT:
        x += dx
        y += dy
        dist += 1
        # Vérifie les collisions avec les bords
        if TRACK_BORDER_MASK.get_at((int(x), int(y))):
            break

    # Normaliser la distance entre 0 et 1
    max_distance = np.sqrt(WIDTH**2 + HEIGHT**2)
    point = (x,y)
    return dist / max_distance,point



def train():
    nbr_games = 0
    game = CarAI(5, 5)


    while True:
        state = [game.get_state()]
        index = loaded_model.predict(state)
        move = index[0]

        action = [0, 0, 0, 0]
        action[move] = 1

        done, score = game.play_step(action)

        if done:
            game.reset()
            nbr_games += 1
            print('Game:', nbr_games, 'Score:', score)

#if __name__ == '__main__':
    #train()

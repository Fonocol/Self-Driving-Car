import pygame
import time
import random
import math
from utils import scale_img, blit_rotate_center
import numpy as np
import csv  # Import pour la sauvegarde des données

pygame.init()
font = pygame.font.SysFont(None, 24)

TRACK = scale_img(pygame.image.load('./imgs/map.png'), 0.55)
TOITURE = scale_img(pygame.image.load('./imgs/toiture.png'), 0.55)
PLANTES = scale_img(pygame.image.load('./imgs/plantes.png'), 0.55)
TRACK_BORDER = scale_img(pygame.image.load('./imgs/masck.png'), 0.55)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load('./imgs/finish.png')
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (317, 501)

RED_CAR = scale_img(pygame.image.load('./imgs/red-car.png'), 0.55)
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CAR GAME!")

RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLANC =(255, 255, 255)
GREEN = (0, 255, 0)

FPS = 60
HUMAIN_POSITION = [(475, 518), (585, 515), (700, 513), (797, 502), (823, 457), (828, 387), (778, 340), (778, 340), (692, 376), (605, 435), (532, 384), (543, 313), (540, 239), (559, 183), (616, 190), (640, 247), (688, 286), (753, 251), (811, 199), (832, 124), (818, 76), (761, 43), (705, 62), (662, 92), (610, 109), (568, 90), (531, 50), (476, 38), (447, 80), (379, 108), (435, 137), (445, 202), (468, 271), (474, 340), (440, 380), (367, 369), (326, 280), (300, 194), (309, 134), (326, 74), (306, 34), (213, 28), (107, 37), (53, 62), (53, 123), (65, 164), (133, 215), (203, 247), (253, 294), (283, 354), (277, 411), (217, 451), (176, 412), (144, 332), (99, 273), (51, 309), (50, 381), (53, 446), (82, 507), (189, 521)]
COLLECTABLE_IMG = scale_img(pygame.image.load('./imgs/femme.png'), 0.08)

# Initialisation de la collecte de données
data_collection = []





class Collectable:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.depart = True
        self.arrive = False   

    def draw(self, win):
        win.blit(COLLECTABLE_IMG, (int(self.x), int(self.y)))

    def attach_to_car(self, destination, car):
        distance = math.sqrt((self.x - car.x) ** 2 + (self.y - car.y) ** 2)
        distance_to_destination = math.sqrt((self.x - destination[0]) ** 2 + (self.y - destination[1]) ** 2)
        if distance < 20 and distance_to_destination>20:
            self.depart = False

    def update_position(self, car):
        if self.depart == False and self.arrive == False:
            self.x, self.y = car.x, car.y

    def detach_at_destination(self, destination,car):
        distance_to_destination = math.sqrt((self.x - destination[0]) ** 2 + (self.y - destination[1]) ** 2)
        distance = math.sqrt((self.x - car.x) ** 2 + (self.y - car.y) ** 2)
        if distance_to_destination < 20 and distance < 20: 
            self.arrive = True




class Car:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.angle = -90
        self.rotation_vel = rotation_vel
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.score = 0
        self.client = None
        self._place_client()

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        self.debug(win)
        pygame.draw.circle(win, BLANC, (self.client.x,self.client.y) , 20) #cercle client
       
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
        self.client.draw(win)
        

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def is_collision(self):
      border_point_collide = self.collide(TRACK_BORDER_MASK)
      if border_point_collide != None:
        #print("zonne interdite")
        if self.x >= WIDTH-20 or self.x <= 20 or self.y >= HEIGHT-10 or self.y <= 5:
            self.bounce()
        
      return border_point_collide  

    def bounce(self):
        self.vel = -self.vel
        self.move()

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
        self.client = None
        self._place_client()

    def debug(self,win):
      angele_dis = self.radar()
      index = 0
      for dis_pos in angele_dis:
        pygame.draw.circle(win, BLUE, dis_pos[1], 10)
        pygame.draw.line(win, GREEN, dis_pos[1] , (self.x, self.y), 1)
        text_f = font.render(str(index), True, BLANC)
        win.blit(text_f, (dis_pos[1][0] - text_f.get_width() // 2, dis_pos[1][1] - text_f.get_height() // 2))
        index += 1

    def debug1(self,win):
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
      pygame.draw.line(win, RED, p1 , (self.x, self.y), 1)

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
      pygame.draw.circle(win, BLUE, FINISH_POSITION , 20)


    def get_state(self):
      front_dist,p1 = self.get_distance_in_direction("front")
      back_dist,p2 = self.get_distance_in_direction("back")
      left_dist,p3 = self.get_distance_in_direction("left")
      right_dist,p4 = self.get_distance_in_direction("right")
      left_font_dist,p5 = self.get_distance_in_direction("left_font")
      right_font_dist,p6 = self.get_distance_in_direction("right_font")
      left_back_dist,p7 = self.get_distance_in_direction("left_back")
      right__back_dist,p8 = self.get_distance_in_direction("right__back")
    
      pygame.display.update()
      angle = (self.angle % 360) / 180 - 1
      speed = self.vel / self.max_vel
      collision = False
      if self.is_collision():
           collision = True
      #collision = int(self.is_collision() is not None)
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
        
    
      # la distance à l'obstacle
      x, y, dist = self.x, self.y, 0
      while 10 <= int(x) < WIDTH-10 and 10 <= int(y) < HEIGHT-10:
        x += dx
        y += dy
        dist += 1
        # Vérifie les colisions
        if TRACK_BORDER_MASK.get_at((int(x), int(y))):
            break

      # Normaliser la distance entre 0 et 1
      max_distance = np.sqrt(WIDTH**2 + HEIGHT**2)
      point = (x,y)
      return dist / max_distance,point


    def radar(self):
        radians = math.radians(self.angle)
        angele_dis = []
        max_distance = np.sqrt(WIDTH**2 + HEIGHT**2)
        
        for decalage in range(0, 360):  # Utilise les angles en radians
            # Convertit le décalage en radians, chaque angle ayant une différence de 45° (pi/4 radians)
            angle_offset = math.radians(decalage)
            dx, dy = math.cos(radians + angle_offset), -math.sin(radians + angle_offset)
            
            # Initialisation des coordonnées de départ et distance
            x, y, dist = self.x, self.y, 0
            while 10 <= int(x) < WIDTH - 10 and 10 <= int(y) < HEIGHT - 10:
                x += dx
                y += dy
                dist += 1
                # Vérifie les collisions
                if TRACK_BORDER_MASK.get_at((int(x), int(y))):
                    break
            
            # Ajoute la distance normalisée et le point d'impact pour chaque direction
            angele_dis.append((dist / max_distance, (x, y)))
        
        return angele_dis



    def _place_client(self):
        i = random.randint(0, len(HUMAIN_POSITION)-1)
        x,y = HUMAIN_POSITION[i]
        self.client = Collectable(x, y)



    




class PlayerCar(Car):
    IMG = RED_CAR
    START_POS = (480, 514)

    



def collect_data(player_car, action):
    state = player_car.get_state()
    front_dist, back_dist, left_dist, right_dist,left_font_dist,right_font_dist,left_back_dist,right__back_dist, angle, speed, collision, finish_dist = state

    data_collection.append({
        'x': player_car.x,
        'y': player_car.y,
        'speed': speed,
        'angle': angle,
        'front_dist': front_dist,
        'back_dist': back_dist,
        'left_dist': left_dist,
        'right_dist': right_dist,
        'collision': collision,
        'finish_distance': finish_dist,
        'action': action,
        'left_font_dist' : left_font_dist,
        'right_font_dist' : right_font_dist,
        'left_back_dist' : left_back_dist,
        'right__back_dist' : right__back_dist
    })

def save_data_to_csv():
    fieldnames = [
        'x', 'y', 'speed', 'angle', 'front_dist', 'back_dist', 
        'left_dist', 'right_dist', 'collision', 'finish_distance', 'action','left_font_dist','right_font_dist','left_back_dist','right__back_dist'
    ]
    
    with open('player_car_data.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_collection:
            writer.writerow(data)

def draw(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)
    player_car.draw(win)
    win.blit(TOITURE, (0,0))
    win.blit(PLANTES, (0,0))
    text = font.render("Score: " + str(player_car.score), True, BLANC)
    win.blit(text, [0,0])
    text = font.render("GARA DE CALAIS VILLE" , True, BLANC)
    win.blit(text, [317, 440])
    pygame.display.update()

def move_player(player_car):
    keys = pygame.key.get_pressed()
    action = None
    
    if keys[pygame.K_UP]:
        action = 'forward'
        player_car.move_forward()
    elif keys[pygame.K_DOWN]:
        action = 'backward'
        player_car.move_backward()
    if abs(player_car.vel) > 0:
        if keys[pygame.K_LEFT]:
            action = 'rotate_left'
            player_car.rotate(left=True)
        elif keys[pygame.K_RIGHT]:
            action = 'rotate_right'
            player_car.rotate(right=True)

    if action is None:
        player_car.reduce_speed()
    
    return action

run = True
clock = pygame.time.Clock()
images = [(TRACK, (0, 0)),(FINISH, FINISH_POSITION)] #,  (TRACK_BORDER, (0, 0))
player_car = PlayerCar(4, 4)


while run:
    clock.tick(FPS)
    
    # Affiche l'arrière-plan et autres images
    draw(WIN, images, player_car)
    
    
    player_car.client.attach_to_car(FINISH_POSITION,player_car)  # Attache si proche
    player_car.client.update_position(player_car)  # Suivre la voiture si collecté
    player_car.client.detach_at_destination(FINISH_POSITION,player_car)  # Détache si à la destination
    if player_car.client.depart == False and player_car.client.arrive == True:
       player_car._place_client()
       player_car.score +=1

    # Gère les actions du joueur
    action = move_player(player_car)
    #print(player_car.x,player_car.y)
    if action:
        collect_data(player_car, action)
    
   
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    pygame.display.update() 

pygame.quit()

#save = int(input("Save data? Entre 1: save = "))
#if save == 1:
   #save_data_to_csv()

import pygame
from utils import scale_img, blit_rotate_center
import math

COLLECTABLE_IMG = scale_img(pygame.image.load('./imgs/femme.png'), 0.08)
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
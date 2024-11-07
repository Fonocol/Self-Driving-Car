import pygame
import math
import random
from collections import namedtuple

pygame.init()
font = pygame.font.Font(None, 25)

# Couleurs
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Dimensions et paramètres
SCREEN_WIDTH, SCREEN_HEIGHT = 740, 580
RADIUS = 200  # Rayon du cercle
BAR_LENGTH = 100  # Longueur de la barre
BALL_SPEED = 5  # Vitesse de la balle
ROTATION_SPEED = 5  # Vitesse de rotation de la barre
BARRE_ANGLE = 45  # Angle entre les extrémités de la barre
GRAVITY= 0.0


Point = namedtuple('Point', 'x, y')


class CircleGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Circle Game')
        self.clock = pygame.time.Clock()

        # Initialisation des positions et angles
        self.center = Point(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.bar_angle = 65  # Angle initial de la barre avec le centre (en degrés)
        self.ball_position = Point(self.center.x, self.center.y)
        self.ball_velocity = [0, BALL_SPEED * math.sin(math.radians(45))]  # Vitesse initiale de la balle
        self.score = 0

    def rotate_bar(self, direction):
        if self.bar_angle >= 360:
            self.bar_angle = 0
        # Ajustement de l’angle de la barre
        if direction == 'LEFT':
            self.bar_angle += ROTATION_SPEED
        elif direction == 'RIGHT':
            self.bar_angle -= ROTATION_SPEED



    def move_ball(self):
        # Déplacement de la balle en suivant sa vitesse
        self.ball_velocity[1] += GRAVITY 
        self.ball_position = Point(
            self.ball_position.x + self.ball_velocity[0],
            self.ball_position.y + self.ball_velocity[1]
        )

        # Vérification si la balle sort du cercle
        distance_to_center = math.sqrt((self.ball_position.x - self.center.x) ** 2 +
                                       (self.ball_position.y - self.center.y) ** 2)
        if distance_to_center > RADIUS + 5:  # 5 est une marge
            self.ball_velocity[0] = -self.ball_velocity[0]  # Inverser la direction de la balle
            self.ball_velocity[1] = -self.ball_velocity[1]  # Inverser la direction de la balle

    
    def calculate_bar_position(self):
        bar_x1 = int(self.center.x + (RADIUS * math.cos(math.radians(self.bar_angle))))
        bar_y1 = int(self.center.y + (RADIUS * math.sin(math.radians(self.bar_angle))))
        bar_x2 = int(self.center.x + (RADIUS * math.cos(math.radians(self.bar_angle + BARRE_ANGLE))))
        bar_y2 = int(self.center.y + (RADIUS * math.sin(math.radians(self.bar_angle + BARRE_ANGLE))))
        return bar_x1, bar_y1, bar_x2, bar_y2
    
    def distansto(self,point1,point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    def check_collision(self):
        bar_x1, bar_y1, bar_x2, bar_y2 = self.calculate_bar_position()

        # Calcul de la distance entre la balle et la ligne de la barre
        distance_to_bar = abs((bar_y2 - bar_y1) * self.ball_position.x -
                              (bar_x2 - bar_x1) * self.ball_position.y +
                              bar_x2 * bar_y1 - bar_y2 * bar_x1) / math.sqrt((bar_y2 - bar_y1) ** 2 + (bar_x2 - bar_x1) ** 2)

        # Si la balle est assez proche pour être en collision avec la barre
        #distance_to_bar_center = math.sqrt((((bar_x2 + bar_x1)/2) - self.center.x )**2 + (((bar_y2 + bar_y1)/2)- self.center.y) ** 2)
        distance_center_ball = math.sqrt((self.ball_position.x - self.center.x)**2 + (self.ball_position.y  - self.center.y)**2)
        ball_p1 = self.distansto((self.ball_position.x,self.ball_position.y),(bar_x1,bar_y1))
        ball_p2 = self.distansto((self.ball_position.x,self.ball_position.y),(bar_x2,bar_y2))

        if distance_to_bar < 30  and distance_center_ball < RADIUS-30 and ball_p1>=10 and  ball_p2>=10 :  # Seuil de collision, ajustable pour plus de précision
            # Calcul du vecteur normal de la barre
            bar_dx = bar_x2 - bar_x1
            bar_dy = bar_y2 - bar_y1
            bar_length = math.sqrt(bar_dx**2 + bar_dy**2)
            normal_x = -bar_dy / bar_length
            normal_y = bar_dx / bar_length

            # Produit scalaire pour déterminer la nouvelle direction
            dot_product = self.ball_velocity[0] * normal_x + self.ball_velocity[1] * normal_y
            self.ball_velocity[0] -= 2 * dot_product * normal_x
            self.ball_velocity[1] -= 2* dot_product * normal_y
            

            self.score += 1
            return True
        return False


    def is_game_over(self):
        # Vérifier si la balle sort du cercle
        distance_to_center = math.sqrt((self.ball_position.x - self.center.x) ** 2 +
                                       (self.ball_position.y - self.center.y) ** 2)
        return False
        #return distance_to_center >= RADIUS-5  # 5 est une marge

    def play_step(self):
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # Contrôle de la rotation de la barre
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rotate_bar('LEFT')
        elif keys[pygame.K_RIGHT]:
            self.rotate_bar('RIGHT')

        # Mise à jour des positions
        self.move_ball()
        self.check_collision()

        # Vérifier si la partie est terminée
        if self.is_game_over():
            print(f"Game Over! Score final: {self.score}")
            pygame.quit()
            exit()

        # Rafraîchir l'affichage
        self.screen.fill(BLACK)
        pygame.draw.circle(self.screen, WHITE, (self.center.x, self.center.y), RADIUS, 2)

        # Dessiner la barre
        bar_x1, bar_y1, bar_x2, bar_y2 = self.calculate_bar_position()

        pygame.draw.line(self.screen, GREEN, (bar_x1, bar_y1), (bar_x2, bar_y2), 2)

        # Dessiner la balle
        pygame.draw.circle(self.screen, RED, (int(self.ball_position.x), int(self.ball_position.y)), 8)

        # Afficher le score
        score_text = font.render("Score: " + str(self.score), True, WHITE)
        self.screen.blit(score_text, [10, 10])

        pygame.display.flip()
        self.clock.tick(60)

if __name__ == "__main__":
    game = CircleGame()
    while True:
        game.play_step()

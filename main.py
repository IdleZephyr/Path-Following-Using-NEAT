import pygame
import os
import math
import sys
import neat
from pygame import mixer

maxfit = 0 # Define ตัวแปร maxfit ไว้เป็น 0 (Max Fitness)

# ขนาดของหน้าต่างโปรแกรม (ตั้งไว้มีขนาดเท่ากับรูปแผนที่สนาม)
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.init()
MAP = pygame.image.load(os.path.join("Picture", "road+.png")) # โหลดไฟล์ รูปสนาม
FONT = pygame.font.Font("freesansbold.ttf", 20) # กำหนด font

mixer.music.load(os.path.join("Sound", "Flash-Run.wav")) # โหลดไฟล์ background music
mixer.music.play(-1) # เล่นไฟล์ background music

class Car(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load(os.path.join("Picture", "crockcroch.png")) # โหลดไฟล์ รูปรถ
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(815, 487)) # จุด spawn
        self.vel_vector = pygame.math.Vector2(2, 0) # ความเร็วการเคลื่อนที่
        self.angle = 0
        self.rotation_vel = 7 # ความเร็วการหมุน
        self.direction = 0 # -1 เลี้ยวซ้าย / 1 เลี้ยวขวา
        self.alive = True
        self.radars = []


    def update(self): #ฟังก์ชันอัพเดตการทำงานของรถ โดยเรียกใช้ฟังก์ชันต่างๆในคลาส Car
        self.radars.clear()
        self.drive()
        self.rotate()
        for radar_angle in (-90,-60, -30, 0, 30, 60, 90): # ลูปเพื่อสร้างเรดาร์ 7 เส้น
            self.radar(radar_angle)
        self.collision()
        self.data()


    def drive(self): #ฟังก์ชันการเคลื่อนที่
        self.rect.center += self.vel_vector * 6

    def collision(self): #ฟังก์ชันชน/ออกนอกทาง
        # กำหนดจุดการชนซ้ายขวา
        length = 20 # ระยะระหว่างจุดกึงกางของตัวรถ ถึงจดการชน
        collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 18)) * length),   #ตำแหน่งจุดการชนด้านขวา
                                 int(self.rect.center[1] - math.sin(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle - 18)) * length),    #ตำแหน่งจุดการชนด่านซ้าย
                                int(self.rect.center[1] - math.sin(math.radians(self.angle - 18)) * length)]

        # ชนสีดำ = ตาย
        if SCREEN.get_at(collision_point_right) == pygame.Color(0,0,0,255) \
                or SCREEN.get_at(collision_point_left) == pygame.Color(0,0,0,255):
            self.alive = False

        # วาดแสดงจุดการชนซ้ายขวา สีน้ำเงิน
        pygame.draw.circle(SCREEN, (0,0,255,1), collision_point_right, 3)
        pygame.draw.circle(SCREEN, (0,0,255,1), collision_point_left, 3)


    def rotate(self): #ฟังก์ชันการหมุนเลี้ยวรถ
        if self.direction == 1: #เลี่ยวขวา / หมุนตามเข็มนาฬิกา
            self.angle -= self.rotation_vel
            self.vel_vector.rotate_ip(self.rotation_vel)
        if self.direction == -1: #เลี่ยวซ้าย / หมุนทวนเข็มนาฬิกา
            self.angle += self.rotation_vel
            self.vel_vector.rotate_ip(-self.rotation_vel)

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 0.1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def radar(self, radar_angle): #ฟังก์ชันเรดาร์
        length = 0 #ระยะเรดาร์เริ่มที่ 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        while not SCREEN.get_at((x, y)) == pygame.Color(0,0,0,255) and length < 200: #ระยะเรดาร์เริ่มเพิ่มจนกว่าจะเจอสีดำ สูงระยะสุด 200
            length += 1 #ระยะเรดาร์เริ่มเพิ่มทีละ 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle)) * length) #คำนวณจุดปลายของเรดาร์
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle)) * length)

        # วาดเรดาร์
        pygame.draw.line(SCREEN, (255, 255, 255, 255), self.rect.center, (x, y), 1) # เส้นตรงสีขาว
        pygame.draw.circle(SCREEN, (255, 0, 0, 1), (x, y), 2) # จุดปลายสีแดง

        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2)
                             + math.pow(self.rect.center[1] - y, 2)))

        self.radars.append([radar_angle, dist])

    def data(self):
        input = [0, 0, 0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input


def remove(index): #ฟังก์ชันลบรถออก

    cars.pop(index)
    ge.pop(index)
    nets.pop(index)

def statistics(): #ฟังก์ชันแสดงสถานะ genetic algorithm บนหน้าต่างโปรแกรม
        text_1 = FONT.render(f'Alive:  {str(len(cars))}', True, (255, 255, 255))
        text_2 = FONT.render(f'Generation:  {pop.generation + 1}', True, (255, 255, 0))
        text_3 = FONT.render(f'Fitness:  {ge[0].fitness}', True, (255, 255, 255))
        text_4 = FONT.render(f'MaxFitness:  {maxfit}', True, (255, 255, 255))

        SCREEN.blit(text_1, (840, 610))
        SCREEN.blit(text_2, (840, 710))
        SCREEN.blit(text_3, (840, 810))
        SCREEN.blit(text_4, (840, 910))

def eval_genomes(genomes, config): #ฟังก์ชัน main ของโปรแกรม ประเมินค่า fitness
    global cars, ge, nets, maxfit

    cars = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        cars.append(pygame.sprite.GroupSingle(Car()))
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.blit(MAP, (0, 0))

        if len(cars) == 0:
            break

        for i, car in enumerate(cars):
            ge[i].fitness += 1

            if maxfit < ge[i].fitness:
                maxfit = ge[i].fitness
            if maxfit > 10000:
                exit()

            if not car.sprite.alive:
                remove(i)

        for i, car in enumerate(cars):
            output = nets[i].activate(car.sprite.data())
            if output[0] > 0.7:
                car.sprite.direction = 1
            if output[1] > 0.7:
                car.sprite.direction = -1
            if output[0] <= 0.7 and output[1] <= 0.7:
                car.sprite.direction = 0

        # Update
        for car in cars:
            car.draw(SCREEN)
            car.update()
            statistics()
        pygame.display.update()


# Setup NEAT Neural Network
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)

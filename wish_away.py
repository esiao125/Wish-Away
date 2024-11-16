import pygame
from pygame.locals import *
import pickle
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

SCREEN_WIDTH = 1000  #game window
SCREEN_HEIGHT = 1000 #game window

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #game window
pygame.display.set_caption("Wish Away")

#define game variables
tile_size = 50
game_over = 0
main_menu = True


#load images
room_img = pygame.image.load('img/floor.jpg')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True


		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)
		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)

	def update(self, game_over):

		dx = 0
		dy = 0
		walk_cooldown = 5


		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False: 
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10

			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0

				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False
				
			#check for collision with enemies
			if pygame.sprite.spritecollide(self, clown_group, False):
				game_over = -1


			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy
		elif game_over == -1:
			self.image = self.dead_image
			if self.rect.y > 200:
				self.rect.y -= 5

		#draw player onto screen
		screen.blit(self.image, self.rect)
		return game_over

	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/guy{num}.png')
			img_right = pygame.transform.scale(img_right, (40, 80))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/ghost.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True 


class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		ground_img = pygame.image.load('img/ground.png')
		shelf_img = pygame.image.load('img/shelf.png')
		clown_img = pygame.image.load('img/clown.png')
		rope_img = pygame.image.load('img/rope.png')
		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(ground_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 7:
					img = pygame.transform.scale(shelf_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					img = pygame.transform.scale(rope_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile) 
				if tile == 9:
					clown = Enemy(col_count * tile_size, row_count * tile_size + (tile_size // 2), player)
					clown_group.add(clown)

				col_count += 1
			row_count += 1
	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y, player):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/clown.png')
		self.image = pygame.transform.scale(self.image, (50, 50))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.speed = 2
		self.player = player
		
	def update(self):
		dx, dy = player.rect.x - self.rect.x, player.rect.y - self.rect.y
		distance = max(1, (dx**2 + dy**2) ** 0.5)
		dx, dy = dx/distance, dy/distance

		self.rect.x += int(dx * self.speed)
		self.rect.y += int(dy * self.speed)

with open("data.pkl", "rb") as file:
	world_data = pickle.load(file)


player = Player(100, SCREEN_HEIGHT - 130)


clown_group = pygame.sprite.Group()

for i in range(3):
	x = random.randint(0, SCREEN_WIDTH - 4)
	y = random.randint(0, SCREEN_HEIGHT - 3)
	clown = Enemy(x, y, player)
	clown_group.add(clown)

world = World(world_data)

#create buttons
restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT//2 + 100, restart_img)
start_button = Button(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2, start_img)
exit_button = Button(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2, exit_img)


run = True #game loop
while run: #game loop

	clock.tick(fps)

	screen.blit(room_img, (0, 0))

	if main_menu:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False

	else:
		world.draw()

		clown_group.update()
		screen.blit(player.image, player.rect)
		clown_group.draw(screen)
		pygame.display.flip()

		game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			if restart_button.draw():
				player.reset(100, SCREEN_HEIGHT - 130)
				game_over = 0


	
	for event in pygame.event.get(): #event handler
		if event.type == pygame.QUIT: #event handler
			run = False #event handler
			
	pygame.display.update()

pygame.quit()

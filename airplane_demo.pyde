add_library('minim')
import os
import random

# we detected importing images inside the classes make the game a bit slower  and posses unexepected 
#error when playing for long so we decided to put them out from the class.
path = os.getcwd()
tile_path = path + "/kenney_pixelshmup"
player = Minim(this)
RESOLUTION_X = 800
RESOLUTION_Y = 800

airplane = loadImage(tile_path + "/Ships/ship_0000.png")
enemy_1 = loadImage(tile_path + "/Ships/ship_0001.png")
enemy_2 = loadImage(tile_path + "/Ships/ship_0007.png")
enemy_3 = loadImage(tile_path + "/Ships/ship_0009.png")
enemy_4 = loadImage(tile_path + "/Ships/ship_0011.png")
bullet_image = loadImage(tile_path + "/Tiles/tile_0000.png")
healthpack_image = loadImage(tile_path + "/Tiles/tile_0024.png")


explosion_images = []
for x in range(4, 9):
    explosion_images.append(loadImage(tile_path + "/Tiles/tile_000" + str(x) + ".png"))

backgroundMap = loadImage(path + "/map.png")

angle = 0
#Airplane class which is responsible for coordinate tracking trancking of aiprlanes
class Airplane:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    #destance calculation for genaral case
    def distance(self, other):
        return((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
#player class which manages the player air plane
class Player(Airplane):
    def __init__(self, x, y):
        Airplane.__init__(self, x, y)
        self.image = airplane
        self.key_handler = {LEFT:False, RIGHT:False, UP:False, DOWN:False, ' ':False}
        self.r = 20
        self.vx = 0
        self.vy = 0
        self.score = 0
        self.health = 100
        self.exp = False
    def follow_cursor(self):
        global angle
        # Calculate the angle based on the difference between the airplane's x-position and the mouse's x-position
        angle = atan2(mouseX - RESOLUTION_X / 2, RESOLUTION_Y - 100)
        
        # Translate to the center of the airplane
        translate(RESOLUTION_X / 2, RESOLUTION_Y - 100)
        
        # Rotate the airplane based on the calculated angle
        rotate(angle)
    #displays the player airplane
    def display(self):        
        imageMode(CENTER)
        image(airplane, self.x, self.y, 40, 40)
    #update calss which the relevant information for this class
    def update(self):
        global bullet_damage
        if self.key_handler[LEFT] == True:
            # Left key is pressed.
            if self.vx > -5:
                self.vx -= 0.2
        elif self.key_handler[RIGHT] == True:
            # right key is pressed
            if self.vx < 5:
                self.vx += 0.2
        elif self.key_handler[UP] == True:
            # up key is pressed - jump (only if mario is on the ground)
            if self.vy > -5:
                self.vy -= 0.2
        elif self.key_handler[DOWN] == True:
            if self.vy < 5:
                self.vy += 0.2
        elif self.key_handler[' '] == True:
            self.shoot()
        
        self.y += self.vy
        self.x += self.vx
        
         # prevent the plane from going out of the screen from the left/right
        if self.x < 20:
            self.x = 20
        if self.x > RESOLUTION_X - 20:
            self.x = RESOLUTION_X - 20
        if self.y < RESOLUTION_Y/2:
            self.y = RESOLUTION_Y/2
        if self.y > RESOLUTION_Y - 50:
            self.y = RESOLUTION_Y - 50
        #game over condition
        if self.health <= 0:
            game.gameOver = True
            game.displayGameOver()
        if frameCount % 5 == 0:
            for bullet in game.bullets:
                    if self.distance(bullet) <= self.r + bullet.r and bullet.vy < 0:
                        self.health -= bullet_damage
                        game.bullets.remove(bullet)
            #enemy plane colision handling
            for enemy in game.enemies:
                if enemy.exploded == False:
                    if self.distance(enemy) <= self.r + enemy.r:
                        if self.health - 25 < 0:
                            self.health = 0
                        else:
                            self.health -= 25
                        enemy.explode()
        
                                        
            try:
                #health regeneration
                if self.distance(game.healthpack) <= self.r + game.healthpack.r:
                    if self.health + 25 > 100:
                        self.health = 100
                    else:
                        self.health += 25
                    # del game.healthpack
                    game.healthpack = None
            except AttributeError:
                # if there are no healthpacks currently spawned
                pass
                
        
    def shoot(self):
        #shooting of bullet
        game.bullets.append(Bullet(self.x, self.y - 30, 10, 10, bullet_image))
        if game.player.health <= 0:
            pass
        else:
            game.shot_sound.rewind()
            game.shot_sound.play()
        
    
#class handlling enemy
class Enemy(Airplane):
    def __init__(self, x, y):
        Airplane.__init__(self, x, y)          
        self.y = random.randint(-100, 0)
        self.x = random.randint(0, RESOLUTION_X)
        self.r = 20
        self.image = random.choice([enemy_1, enemy_2, enemy_3, enemy_4])
        # self.shadow_image = darken_image(self.image)
        self.vy = random.randint(2, 3)
        self.shoot_rate = random.randint(3, 7)
        self.health = 50
        self.score_inc = player.loadFile(path + "/sounds/score_inc.mp3")
        self.exp_sound = player.loadFile(path + "/sounds/explosion.mp3")
        self.eab = False
        self.ex_img = explosion_images[0]
        self.start_frame = 0
        self.isAlive = True
        self.exploded = False
    #methode responsible to display enemy plane and also explosion_animation
    def display(self):
        
        resetMatrix()
        image(self.image, self.x, self.y, 40, 40, 40, 40, 0, 0)
        if self.eab == True:
            image(self.ex_img, self.x-20, self.y-20, 80, 80, 40, 40, 0, 0)
        
    #methode that updates enemy status if it is alive or not
    def update(self):
        self.y += self.vy
        if frameCount % 5 == 0:
            for bullet in game.bullets:
                if self.exploded == False:
                    if self.distance(bullet) <= self.r + bullet.r and bullet.vy >0:
                        game.bullets.remove(bullet)
                        self.health -= 25
                        if self.health <= 0:
                            self.explode()
        if self.eab:
            self.explosion_animation()
    #methode for explosion animation
    def explosion_animation(self):
        if frameCount - self.start_frame < 3:
            self.ex_img = explosion_images[0]
        elif frameCount - self.start_frame < 6:
            self.ex_img = explosion_images[1]
        elif frameCount - self.start_frame < 9:
            self.ex_img = explosion_images[2]
        else:
            frameCount - self.start_frame < 12
            self.ex_img = explosion_images[3]
            self.eab = False
            self.isAlive = False

        self.display()

    #methode for enemy to explode, to disapper    
    def explode(self):
        game.player.score += 1
        self.score_inc.rewind()
        self.score_inc.play()
        try:
            self.exploded = True
            self.eab = True
            self.start_frame = frameCount
            self.exp_sound.rewind()
            self.exp_sound.play()
            
        except:
            pass
     
    
    #enemy bullet shotting methode
    def shoot(self):
        if frameCount % 60 * self.shoot_rate == 0:
            game.bullets.append(Bullet(self.x, self.y + 30, random.randint(-10, -5), 10, bullet_image))
            game.shot_sound.rewind()
            game.shot_sound.play()
        if self.eab:
            self.explosion_animation()
        


def darken_image(src_img):
    # Create a copy of the source image
    dark_img = createImage(src_img.width, src_img.height, RGB)
    dark_img.loadPixels()
    src_img.loadPixels()

    # Darken each pixel in the image
    for i in range(len(src_img.pixels)):
        dark_img.pixels[i] = color(red(src_img.pixels[i]) * 0.5, green(src_img.pixels[i]) * 0.5, blue(src_img.pixels[i]) * 0.5)

    dark_img.updatePixels()
    return dark_img
#Bullet image and animation Hnadlling class 
class Bullet:
    def __init__(self, x, y, speed, bullet_radius, img):
        self.x = x
        self.y = y
        self.vy = speed
        self.r = bullet_radius
        self.img = img
    def display(self):
        image(self.img, self.x, self.y, 20, 20)
        self.y -= self.vy

#HealthPack
class HealthPack:
    def __init__(self, x, y):
        self.x = random.randint(0, RESOLUTION_X)
        self.y = -50
        self.r = 20
        self.vy = 1
    #display health pack image
    def display(self):
        # circle(self.x, self.y, self.r * 2)
        image(healthpack_image, self.x, self.y, 30, 30)
    #insures the movement of the health pack image
    def update(self):
        self.y += self.vy
#Games class responsible for handling the game logic
class Game:
    def __init__(self):
        self.player = Player(RESOLUTION_X/2, RESOLUTION_Y - 100)
        self.enemies = [Enemy(0, 0) for x in range(4)]
        self.backgroundPos = 0
        self.backgroundSpeed = 1
        self.bullets = []
        self.healthpack = HealthPack(100, 100)
        self.gameOver = False
        self.bg_sound = player.loadFile(path + "/sounds/background.mp3")
        self.bg_sound.loop()
        self.shot_sound = player.loadFile(path + "/sounds/shot.mp3")
        self.explosion = loadImage(path + "/image/" + "explosion_spryite.png")
        self.backgroundPos2 = 0
    #display methode which desplayes enemies and player plane in a logical way
    def display(self):
        strokeWeight(2)
        self.displayBackground()
        noStroke()
        for enemy in self.enemies:
            enemy.display()
            enemy.update()
            enemy.shoot()
            if enemy.isAlive == False:
                self.enemies.remove(enemy)
        try:
            self.healthpack.display()
            self.healthpack.update()
        except AttributeError:
            pass

        self.player.display()
        self.player.update()
        for bullet in self.bullets:
            bullet.display()
            if bullet.y < 0 or bullet.y > RESOLUTION_Y:
                # bullet goes out of screen
                game.bullets.remove(bullet)
                del bullet
        if self.player.health <= 0:
            
            self.bg_sound.close()
    #Background Display Methode
    def displayBackground(self):
        self.backgroundPos += self.backgroundSpeed
        self.backgroundPos2 = self.backgroundPos - RESOLUTION_Y * 3
        
        if self.backgroundPos >= RESOLUTION_Y * 3:
            self.backgroundPos = 0
        
        if self.backgroundPos2 >= 0:
            self.backgroundPos2 = -RESOLUTION_Y * 3
    
        image(backgroundMap, RESOLUTION_X / 2, self.backgroundPos, RESOLUTION_X, RESOLUTION_Y * 3)
        image(backgroundMap, RESOLUTION_X / 2, self.backgroundPos2, RESOLUTION_X, RESOLUTION_Y * 3)
    #Game over display Methode
    def displayGameOver(self):
        global highscore
        textAlign(CENTER)
        textSize(20)
        if self.player.score > highscore:
            highscore = self.player.score
            file = open('highscore.txt', 'w')
            # write the new highscore to the file
            file.write(str(highscore))
            file.close()
            text("New Highscore: " + str(highscore), RESOLUTION_X/2, RESOLUTION_Y/2 + 50)

        fill(0)
        textSize(50)
        text("Game Over", RESOLUTION_X/2, RESOLUTION_Y/2)
        noFill()
        strokeWeight(2)
        stroke(0,225,0)
        rect(width/2 - 95, height/2 + 20, 190, 40)
        textSize(30)
        textAlign(CENTER, CENTER)
        fill(0)
        text("Restart", width/2, height/2 + 40)
        noFill()
        stroke(255,0,0)
        rect(width/2 - 50, height/2 + 70, 100, 40)
        textSize(30)
        textAlign(CENTER, CENTER)
        fill(0)
        text("Quit", width/2, height/2 + 90)
            
    #randome displaying of health pack methode
    def spawn_healthpack(self):
        if self.healthpack == None and frameCount % 60 == 0:
            # Randomly spawn health packs
            # there is a 5% chance of a healthpack spawning every second
            if random.randint(1, 100) <= 5:  # Adjust the probability as needed (5% chance in this example)
                self.healthpack = HealthPack(random.randint(0, RESOLUTION_X), -50)
            
    #enemy generation methode
    def generate_enemies(self):
        global enamies
        num_enemies_outside_screen = 0
        for enemy in self.enemies:
            if enemy.y > RESOLUTION_Y:
                self.enemies.remove(enemy)
                del enemy
                # remove the enemy when it goes out of the screen
            # and add a new enemy
            if len(self.enemies) < enamies:
                self.enemies.append(Enemy(0, 0))



highscore = 0
start_screen = True
started = False
Level_Selector = False
bullet_radius = 5 
bullet_damage = 5
enamies = 4
easy = False
medium = False
hard = False
rgb = False
cl = [{'R':0, 'G':0, 'B':0}, {'R':0, 'G':0, 'B':0}, {'R':0, 'G':0, 'B':0}]
def setup():
    global highscore
    size(RESOLUTION_X, RESOLUTION_Y)
    pixel_font = createFont("arcade-font.ttf", 16)
    textFont(pixel_font)
    background(255)
    # Read the high score from the file
    try:
        with open('highscore.txt', 'r') as file:
            highscore = int(file.read().strip())
    except:
        # If the file is not found, create it
        with open('highscore.txt', 'w') as file:
            file.write('0')
            highscore = 0

def draw():
    
    global start_screen
    #start screen display
    if start_screen:
        background(233, 245, 245)
        textSize(30)
        textAlign(CENTER)
        text("Start Game", width/2, height/2)
        # Play Button
        stroke(0,0,0)
        noFill()
        rect(width/2 - 50, height/2 + 20, 100, 40)
        textSize(25)
        textAlign(CENTER, CENTER)
        fill(0)
        text("Play", width/2, height/2 + 40)
        stroke(0,0,0)
        noFill()
        rect(width/2 - 60, height/2 + 70, 120, 40)
        textSize(25)
        textAlign(CENTER, CENTER)
        fill(0)
        text("Level", width/2, height/2 + 90)
    elif Level_Selector:
        # when Level is selected this window displays
        background(233, 245, 245)
        textSize(30)
        textAlign(CENTER)
        text("select Level", width/2, height/2)
        # Play Button
        stroke(cl[0]['R'],cl[0]['G'],cl[0]['B'])
        noFill()
        rect(width/2 - 50, height/2 + 20, 100, 40)
        textSize(25)
        textAlign(CENTER, CENTER)
        fill(0)
        text("Easy", width/2, height/2 + 40)
        stroke(cl[1]['R'],cl[1]['G'],cl[1]['B'])
        noFill()
        rect(width/2 - 70, height/2 + 70, 140, 40)
        textSize(25)
        textAlign(CENTER, CENTER)
        fill(0)
        text("Medium", width/2, height/2 + 90)
        stroke(cl[2]['R'],cl[2]['G'],cl[2]['B'])
        noFill()
        rect(width/2 - 50, height/2 + 120, 100, 40)
        textSize(25)
        textAlign(CENTER, CENTER)
        fill(0)
        text("Hard", width/2, height/2 + 140)
        stroke(0,0,0)
        noFill()
        rect(width/2 - 50, height/2 + 170, 100, 40)
        textSize(25)
        textAlign(CENTER, CENTER)
        fill(0)
        text("Exit", width/2, height/2 + 190)
        
        
    else:
        #the game starts as game is begining
        if not game.gameOver:
            background(233, 245, 245)
            game.display()
            game.generate_enemies()
            game.spawn_healthpack()
            fill(0)
            textAlign(LEFT)
            textSize(20)
            text("HEALTH: " + str(game.player.health), RESOLUTION_X - 180, 30)
            text("SCORE: " + str(game.player.score), 20, 30)
            textSize(15)
            text("HIGH SCORE: " + str(highscore), 20, 60)
            noFill()
            stroke(0)
            strokeWeight(2)
            rect(RESOLUTION_X - 180, 40, 100 * 1.5, 15, 8)
            if game.player.health > 70: fill(200, 225, 135)
            elif game.player.health > 40: fill(255, 247, 97)
            else: fill(255, 118, 97)
            if game.player.health != 0:
                rect(RESOLUTION_X - 180, 40, game.player.health * 1.5, 15, 8)
#key pressing handler
def keyPressed():
    try:
        if keyCode == LEFT or keyCode == 65:
            game.player.key_handler[LEFT] = True
        elif keyCode == RIGHT or keyCode == 68:
            game.player.key_handler[RIGHT] = True
        elif keyCode == UP or keyCode == 87:
            game.player.key_handler[UP] = True
        elif keyCode == DOWN or keyCode == 83:
            game.player.key_handler[DOWN] = True
        if key == ' ':
            # game.player.key_handler[' '] = True
            game.player.shoot()
    except:
        pass
#key relsing handler
def keyReleased():
    try:
        if keyCode == LEFT or keyCode == 65:
            game.player.key_handler[LEFT] = False
        elif keyCode == RIGHT or keyCode == 68:
            game.player.key_handler[RIGHT] = False
        elif keyCode == UP or keyCode == 87:
            game.player.key_handler[UP] = False
        elif keyCode == DOWN or keyCode == 83:
            game.player.key_handler[DOWN] = False
    except:
        pass
#Mouse clicked event handler
def mouseClicked():
    global game, start_screen, started, Level_Selector, bullet_radius, bullet_damage, enamies, easy, medium, hard, cl, rgb
    if start_screen:
        # Check if the user clicks the "Play" button
        if width/2 - 50 <= mouseX <= width/2 + 50 and height/2 + 20 <= mouseY <= height/2 + 60:
            start_screen = False  # Set start_screen to False to start the game
            game = Game()  # Initialize the game
            started = True
        else:
            started = False
        try:
            if width/2 - 60 <= mouseX <= width/2 + 60 and height/2 + 70 <= mouseY <= height/2 + 110:
                start_screen = False
                Level_Selector = True
                rgb = False
        except:
            pass
    if Level_Selector:
        try:
            #color selector when clicked up for the levels
            if width/2 - 50 <= mouseX <= width/2 + 50 and height/2 + 20 <= mouseY <= height/2 + 60:
                bullet_radius = 10
                bullet_damage = 5
                enamies = 4
                cl[2]['G'] = 0
                cl[1]['G'] = 0
                cl[0]['G'] = 255
                rgb = True
            if width/2 - 70 <= mouseX <= width/2 + 70 and height/2 + 70 <= mouseY <= height/2 + 110:
                bullet_radius = 5
                bullet_damage = 5
                enamies = 8
                if rgb == True:
                    cl[2]['G'] = 0
                    cl[0]['G'] = 0
                    cl[1]['G'] = 255
                rgb = True
            if width/2 - 50 <= mouseX <= width/2 + 50 and height/2 + 120 <= mouseY <= height/2 + 160:
                bullet_radius = 5
                bullet_damage = 5
                enamies = 10
                cl[0]['G'] = 0
                cl[1]['G'] = 0
                cl[2]['G'] = 255
                rgb = True
            if width/2 - 50 <= mouseX <= width/2 + 50 and height/2 + 170 <= mouseY <= height/2 + 210:
                Level_Selector = False
                start_screen = True
                
                    
        except:
           pass 
    if started:
        #start condition for game
        if game.gameOver:
            if width/2 - 95 <= mouseX <= width/2 + 95 and height/2 + 20 <= mouseY <= height/2 + 60:
                game = Game()
            if width/2 - 50 <= mouseX <= width/2 + 50 and height/2 + 70 <= mouseY <= height/2 + 110:
                start_screen = True
        
        

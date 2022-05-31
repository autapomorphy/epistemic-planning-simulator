import pygame, sys
from pygame.locals import *
import random

pygame.init()

#FPS setting
FPS = 60
FramePerSec = pygame.time.Clock()

#Colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (196,196,196)

#Font

font = pygame.font.SysFont('Times New Roman', 16)
text_height = font.render("foo", True, BLACK).get_height()

# Screen information
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PANEL_WIDTH = 300

# Draw the background
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("3 boxes")

# images

image_box_unknown = pygame.image.load("box_unknown.png")
image_box_empty_known = pygame.image.load("emptybox_known.png")
image_box_empty_opened = pygame.image.load("emptybox_opened.png")
image_box_with_ball_known = pygame.image.load("box_with_ball_known.png")
image_box_with_ball_opened = pygame.image.load("box_with_ball_open.png")
box_size = image_box_unknown.get_width()


# players setting
player_view = -1;#-1: real world. >=0: players' view
player_num = 2;

# box setting
box_num = 3
box_y0 = 100+box_size/2
box_y_gap = (SCREEN_HEIGHT - 200 - box_size)/2


"""
knowledge format:

p = box_[id]_has_ball, not_[p] , player_[id]_knows_[p]


"""

class info_panel(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.rect = pygame.Rect(SCREEN_WIDTH-PANEL_WIDTH,0,PANEL_WIDTH,SCREEN_HEIGHT)
        self.image = pygame.Surface(self.rect.size)
        self.image.fill(WHITE)
        self.text = []
    
    def draw(self,surface):
        surface.blit(self.image, self.rect) 
        if(len(self.text)!=0):
            for i,s in enumerate(self.text):
                surface.blit(font.render(s, True, BLACK), (self.rect.left,self.rect.top+i*text_height))
        
    
    def clear(self):
        self.text = [];
    
    def box_info(self,box):
        self.text = []
        if(player_view==-1):
            self.text.append("box "+str(box.id))
            if(box.with_ball):
                self.text.append("It has a ball!")
            else:
                self.text.append("It has no ball")
        else:
            self.text.append("box "+str(box.id) + " in player "+ str(player_view) + "'s mind")
            if(player_list[player_view].if_knows("box_"+str(box.id)+"_has_ball")):
                self.text.append("It has a ball!")
            elif(player_list[player_view].if_knows("not_box_"+str(box.id)+"_has_ball")):
                self.text.append("It has no ball")
            else:
                self.text.append("No idea")
        
    def player_info(self,player):
        self.text = []
        if(player_view==-1 or player_view==player.id):
            self.text.append("player "+str(player.id))
            self.text.extend(player.knowledge_base)
            if(len(self.text)==1):
                self.text.append("It knows nothing!")
        else:
            self.text.append("player "+str(player.id) + " in player "+ str(player_view) + "'s mind")
            for s in player_list[player_view].knowledge_base:
                if(s.startswith("player_"+str(player.id)+"_knows_")):
                    self.text.append(s[15+int(player.id/10):])
            if(len(self.text)==1):
                self.text.append("It knows nothing!")

class Box(pygame.sprite.Sprite):
      def __init__(self,id):
        super().__init__()
        self.id = id
        self.with_ball = False
        self.image = image_box_unknown
        self.rect = self.image.get_rect()
        self.rect.center=(SCREEN_WIDTH-PANEL_WIDTH-box_size/2,box_y0+self.id*box_y_gap) 
        self.opened = False
 
      def draw(self, surface):
        box_has_ball = False
        box_known = False
        box_image = image_box_unknown
        if(player_view==-1):
            box_known = True
            if(self.with_ball):
                box_has_ball = True
            else:
                box_has_ball = False
        else:
            if(player_list[player_view].if_knows("box_"+str(self.id)+"_has_ball")):
                box_has_ball = True
                box_known = True
            elif(player_list[player_view].if_knows("not_box_"+str(self.id)+"_has_ball")):
                box_has_ball = False
                box_known = True
            else:
                box_known = False
        
        if(not box_known):
            box_image = image_box_unknown
        else:
            if(box_has_ball):
                if(self.opened):
                    box_image = image_box_with_ball_opened
                else:
                    box_image = image_box_with_ball_known
            else:
                if(self.opened):
                    box_image = image_box_empty_opened
                else:
                    box_image = image_box_empty_known
        
        surface.blit(box_image, self.rect)
      def clicked(self,panel):
        panel.box_info(self)
        
        
      def opened_by(self,player):
        pygame.time.set_timer(pygame.USEREVENT+self.id, 1000)
        self.opened = True
        if self.with_ball:
            player.knows("box_"+str(self.id)+"_has_ball")
        else:
            player.knows("not_box_"+str(self.id)+"_has_ball")

class Player(pygame.sprite.Sprite):
    def __init__(self,id):
        super().__init__() 
        self.id = id;
        self.original_image = pygame.image.load("Player.png")
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (self.rect.width/2, (SCREEN_HEIGHT-100)/player_num*id+50)
        self.facing = 1 #right
        self.knowledge_base = []
    
    def faceto(self):
        self.image =pygame.transform.rotate(self.original_image,-90*(self.facing-1))
        if(self.facing==3):
            self.image =pygame.transform.flip(self.original_image,True,False)
    
    
    def move(self):
        if(player_view!=self.id):
            return;
        pressed_keys = pygame.key.get_pressed()
        previous_position = self.rect.center
        if self.rect.top > 0:
            if pressed_keys[K_UP]:
                self.rect.move_ip(0, -5)
                self.facing = 4
        if self.rect.bottom < SCREEN_HEIGHT:
            if pressed_keys[K_DOWN]:
                self.rect.move_ip(0,5)
                self.facing = 2
             
        if self.rect.left > 0:
              if pressed_keys[K_LEFT]:
                  self.rect.move_ip(-5, 0)
                  self.facing = 3
        if self.rect.right < SCREEN_WIDTH-PANEL_WIDTH:        
              if pressed_keys[K_RIGHT]:
                  self.rect.move_ip(5, 0)
                  self.facing = 1
        self.faceto()
        # collide detection
        if(self.rect.collidelist([sprite.rect for sprite in all_sprites if sprite!=self])!=-1):
            self.rect.center = previous_position
 
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if(player_view==self.id):
            image_indicator = pygame.image.load("ind.png")
            ind_rect = image_indicator.get_rect()
            ind_rect.center = self.rect.center
            ind_rect.move_ip(0,-self.rect.height)
            surface.blit(image_indicator, ind_rect)
        
    
    def attack(self):
        self.attack_rect = pygame.Rect(0,0,30,30)
        self.attack_rect.center = self.rect.center
        if(self.facing == 1):
            self.attack_rect.move_ip((self.rect.width+self.attack_rect.width)/2,0)
        elif(self.facing == 2):
            self.attack_rect.move_ip(0,(self.rect.height+self.attack_rect.height)/2)
        elif(self.facing == 3):
            self.attack_rect.move_ip(-(self.rect.width+self.attack_rect.width)/2,0)
        elif(self.facing == 4):
            self.attack_rect.move_ip(0,-(self.rect.height+self.attack_rect.height)/2)
        for box in boxes:
            if(self.attack_rect.colliderect(box.rect)):
                box.opened_by(self)

        for player in player_list:
            if(player.id!=player_view):
                if(self.attack_rect.colliderect(player.rect)):
                    
                    self.tell(player)
    
    def clicked(self,panel):
        panel.player_info(self)
            
        
    def knows(self,knowledge):
        if(knowledge not in self.knowledge_base):
            self.knowledge_base.append(knowledge)
    
    def if_knows(self,knowledge):
        return knowledge in self.knowledge_base
        
    def tell(self,player):
    #self tells everything to player
        old_knowledge_base = self.knowledge_base.copy()
        for s in self.knowledge_base:#everything I know
            if not s.startswith("player_"+str(player.id)+"_knows_"):
                player.knows(s)
        for s in self.knowledge_base:#now he knows I know all I know
            player.knows("player_"+str(self.id)+"_knows_"+s)
        for s in old_knowledge_base:#now I knows he know all I know
            if not s.startswith("player_"+str(player.id)+"_knows_"):
                self.knows("player_"+str(player.id)+"_knows_"+s)

player_list = []
all_sprites = pygame.sprite.Group()
for i in range(player_num):
   player_list.append(Player(i))
   all_sprites.add(player_list[i])


box_list = []
boxes = pygame.sprite.Group()
for i in range(box_num):
    box_list.append(Box(i))
    boxes.add(box_list[i])
    all_sprites.add(box_list[i])
box_list[1].with_ball = True;
panel = info_panel()
#the main loop
while True:     
    for event in pygame.event.get():              
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == KEYDOWN:
            if(event.key==K_x):
                if(player_view>=0):
                    player_list[player_view].attack();
            elif(event.key==K_v):
                player_view+=1
                panel.clear()
                if player_view >= player_num:
                    player_view = -1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for sprite in all_sprites:
                if(sprite.rect.collidepoint(pygame.mouse.get_pos())):
                    sprite.clicked(panel);
        elif event.type >= pygame.USEREVENT and event.type < pygame.USEREVENT+box_num:
            box_list[event.type-pygame.USEREVENT].opened = False
    for player in player_list:
        player.move()
     
    DISPLAYSURF.fill(GREY)
    for sprite in all_sprites:
        sprite.draw(DISPLAYSURF)
    panel.draw(DISPLAYSURF)
    pygame.display.update()
    FramePerSec.tick(FPS)

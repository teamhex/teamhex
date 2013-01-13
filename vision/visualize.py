import pygame, sys
from pygame.locals import *
import ctypes

c = ctypes.CDLL('./vision.so')

def init():
    global c
    c.startCam("/dev/video1")
    c.enableCam()

init()

pygame.init()
fpsClock = pygame.time.Clock()

c.getInfo()
prev_path = 'tmp/snap'
live = True
fullscreen = False
v = pygame.display.Info()
swidth = v.current_w
sheight = v.current_h

liveview = pygame.image.load(prev_path)
width, height = liveview.get_size()
main_surface = pygame.display.set_mode((width, height))
if fullscreen:
    main_surface.toggle_fullscreen()

while live:
    c.getInfo()
    liveview = pygame.image.load(prev_path)
    if fullscreen:
        if swidth*height/width > sheight:
            liveview = pygame.transform.scale(liveview, (sheight*width/height, sheight))
        else:
            liveview = pygame.transform.scale(liveview, (swidth, swidth*height/width))
    w,h = liveview.get_size()
    mw,mh = main_surface.get_size()
    main_surface.blit(liveview, (mw/2-w/2,mh/2-h/2))
    
    for event in pygame.event.get():
        if event.type == QUIT:
            live = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                live = False
            elif event.key == K_f:
                if(fullscreen):
                    pygame.display.set_mode((width,height))
                else:
                    pygame.display.set_mode((swidth, sheight), FULLSCREEN)
                fullscreen = not fullscreen
    
    pygame.display.update()
    fpsClock.tick(5)

c.stopCam()
pygame.display.quit()
pygame.quit()


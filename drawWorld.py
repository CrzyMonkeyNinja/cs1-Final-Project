import pygame as pg
import runWorld as rw

def loadImage(filename):
    imageSurface = pg.image.load(filename)
    imageSurface.convert()
    return imageSurface


def makeLabel(content, typeface, size, color):
    font = pg.font.SysFont(typeface, size)
    return font.render(content, size, color)


def fill(color):
    rw.displaySurface.fill(color)


def draw(surf, loc):
    rw.displaySurface.blit(surf, loc)

black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

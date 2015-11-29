import runWorld as rw
import drawWorld as dw
import pygame as pg
import math
from random import randint

################################################################

# Define the colors we will use in RGB format
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize world
name = "proj"
width = 1200
height = 800
screen = rw.newDisplay(width, height, name)


class State(object):
    def __init__(self, screen, entities):
        self.screen = screen
        self.entities = entities
        self.keys = []

    def update(self):
        player = self.entities[0]
        """
        functDict = {"W": player.move(0, -5),
                     "A": player.move(-5, 0),
                     "S": player.move(0, 5),
                     "D": player.move(5, 0)}
        """

        functDict = {119: (0, -5),
                     97: (-5, 0),
                     115: (0, 5),
                     100: (5, 0)}

        for key in self.keys:
            if key in functDict:
                player.move(functDict[key])

    def display(self):
        dw.fill(dw.black)
        for ent in self.entities:
            ent.disp(self.screen)

    def end(self):
        result = False
        for ent in self.entities:
            if ((ent.Xcoord < 0) or (ent.Xcoord > width)) or ((ent.Ycoord < 0) or (ent.Ycoord > height)):
                result = True

        return result

    def handleEvent(self, event):
        keyDict = {119: "W",
                   97: "A",
                   115: "S",
                   100: "D",
                   113: "Q",
                   101: "E"}

        if (event.type == pg.KEYDOWN):
            #self.keys.append(keyDict[event.key])
            self.keys.append(event.key)
            print(event.key)

        elif (event.type == pg.KEYUP) and (event.key in self.keys):
            #self.keys.remove(keyDict[event.key])
            self.keys.remove(event.key)
            print(event.key)

    def run(self):
        clock = pg.time.Clock()
        frameRate = 60
        done = False
        while not done:
            self.update()
            self.display()
            pg.display.update()
            clock.tick(frameRate)
            if self.end():
                done = True
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    done = True
                else:
                    self.handleEvent(event)
        pg.quit()


class Entity(object):
    def __init__(self, Xcoord, Ycoord):
        self.Xcoord = Xcoord
        self.Ycoord = Ycoord
        self.head = 0
        self.health = 100

    def disp(self, screen):
        # Draw a circle
        X = (self.Xcoord - 20)
        Y = (self.Ycoord - 20)
        pg.draw.circle(screen, BLUE, [X, Y], 40)
        pg.draw.polygon(screen, RED, [[X, Y - 20], [X + 15, Y + 20], [X, Y + 15], [X - 15, Y + 20]])

    def move(self, change):
        (Xmov, Ymov) = change
        self.Xcoord += Xmov
        self.Ycoord += Ymov

player = Entity(150, 150)
state = State(screen, [player])

state.run()

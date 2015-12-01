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


def detLegs(hyp, ang, X=0, Y=0):

    # determines the length of the legs of a right triangle based on
    # the "ang" angle and the "hyp" hypotenuse and adds them to
    # existing X and Y values

    # print("ang:", ang)

    if ang == 0:
        Y -= hyp

        # print("X = X")
        # print("Y +=", hyp)

    elif ang == 180:
        Y += hyp

        # print("X = X")
        # print("Y -=", hyp)

    elif ang == 90:
        X += hyp

        # print("X +=", hyp)
        # print("Y = Y")

    elif ang == 270:
        X -= hyp

        # print("X -=", hyp)
        # print("Y = Y")

    elif ang > 0 and ang < 90:

        ang = math.radians(90 - ang)

        X += hyp * math.cos(ang)
        Y -= hyp * math.sin(ang)

        # print("X +=", (hyp*(math.cos(ang))) )
        # print("Y +=", (hyp*(math.sin(ang))) )

    elif ang > 90 and ang < 180:

        ang = math.radians(ang - 90)

        X += hyp * math.cos(ang)
        Y += hyp * math.sin(ang)

        # print("X +=", (hyp*(math.cos(ang))) )
        # print("Y -=", (hyp*(math.sin(ang))) )

    elif ang > 180 and ang < 270:

        ang = math.radians(270 - ang)

        X -= hyp * math.cos(ang)
        Y += hyp * math.sin(ang)

        # print("X -=", (hyp*(math.cos(ang))) )
        # print("Y -=", (hyp*(math.sin(ang))) )

    elif ang > 270 and ang < 360:

        ang = math.radians(ang - 270)

        X -= hyp * math.cos(ang)
        Y -= hyp * math.sin(ang)

        # print("X -=", (hyp*(math.cos(ang))) )
        # print("Y +=", (hyp*(math.sin(ang))) )

    else:
        print("\n!!!!!!!!!!\n")
        print("Something is wrong in detLegs")
        print("ang = ", ang)
        print("\n!!!!!!!!!!\n")

    return (X, Y)


class State(object):
    def __init__(self, screen, entities):
        self.screen = screen
        self.entities = entities
        self.keys = []

    def update(self):
        player = self.entities[0]

        functDict = {119: (player.move, False, 5),    # W
                     97: (player.move, True, -5),     # A
                     115: (player.move, False, -5),   # S
                     100: (player.move, True, 5),     # D
                     106: (player.rotate, False, 5),  # J
                     108: (player.rotate, True, 5)}   # L
        """
        106:  # I
        107:  # K
        """

        for key in self.keys:
            if key in functDict:
                # player.move(functDict[key])
                functDict[key][0](functDict[key][1], functDict[key][2])

        if (107 in self.keys) and (32 in self.keys) and (99 not in self.keys):
            player.block = True
            player.brace = False
            player.rotVerts()
        elif (107 in self.keys) and (32 in self.keys) and (99 in self.keys):
            player.brace = True
            player.rotVerts()
        else:
            player.block = False
            player.brace = False
            # player.rotVerts()

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
        """
        keyDict = {119: "W",
                   97: "A",
                   115: "S",
                   100: "D",
                   113: "Q",
                   101: "E"}
        """

        if (event.type == pg.KEYDOWN):
            # self.keys.append(keyDict[event.key])
            self.keys.append(event.key)
            # print(event.key)

        elif (event.type == pg.KEYUP) and (event.key in self.keys):
            # self.keys.remove(keyDict[event.key])
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
    def __init__(self, Xcoord, Ycoord, screen):
        self.Xcoord = Xcoord
        self.Ycoord = Ycoord
        self.head = 0
        self.health = 100
        self.block = False
        self.brace = False
        self.shieldHead = self.head + 315 % 360
        self.rotVerts()
        self.detVerts()

    def disp(self, screen):
        # Draw a circle
        X = (self.Xcoord - 20)
        Y = (self.Ycoord - 20)

        # arrowVerts = [[X, Y-20], [X+15, Y+20], [X, Y+15], [X-15, Y+20]]
        pg.draw.circle(screen, BLUE, [X, Y], 40)
        pg.draw.polygon(screen, RED, self.arrowVerts)
        pg.draw.polygon(screen, WHITE, self.shieldVerts)

    def move(self, axis, mod):
        # (Xmov, Ymov) = change
        if axis is True:
            ang = (self.head + 90) % 360
        else:
            ang = self.head

        (Xmod, Ymod) = detLegs(mod, ang)
        (self.Xcoord, self.Ycoord) = (self.Xcoord + round(Xmod), self.Ycoord + round(Ymod))
        self.detVerts()

    def rotate(self, clock, ang):
        if clock is False:
            ang = -ang
        self.head = (self.head + ang) % 360
        self.rotVerts()

    def slash(self, targets):
        pass

    def rotVerts(self):
        self.locArrowVerts = [detLegs(20, self.head), detLegs(25, (self.head + 135) % 360), detLegs(15, (self.head + 180) % 360), detLegs(25, (self.head + 225) % 360)]

        if self.brace is False:
            shieldSpace = 40
        else:
            shieldSpace = 50

        if (self.block is True) or (self.brace is True):
            self.shieldHead = self.head
            print("iz tru, shieldHead =", self.shieldHead, "head =", self.head)
        else:
            self.shieldHead = (self.head + 300) % 360
            print("iz false, shieldHead =", self.shieldHead, "head =", self.head)
        (shieldX, shieldY) = detLegs(shieldSpace, self.shieldHead)

        self.locShieldVerts = [detLegs(45, (self.shieldHead + 85) % 360, shieldX, shieldY), detLegs(45, (self.shieldHead + 95) % 360, shieldX, shieldY), detLegs(45, (self.shieldHead + 265) % 360, shieldX, shieldY), detLegs(45, (self.shieldHead + 275) % 360, shieldX, shieldY)]

        self.detVerts()

    def detVerts(self):
        X = (self.Xcoord - 20)
        Y = (self.Ycoord - 20)
        self.arrowVerts = handleVerts(X, Y, self.locArrowVerts)
        self.shieldVerts = handleVerts(X, Y, self.locShieldVerts)


def handleVerts(X, Y, local):
    newVerts = []
    for vert in local:
        newVerts.append((vert[0] + X, vert[1] + Y))
    return newVerts

player = Entity(150, 150, screen)
state = State(screen, [player])

state.run()

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
VISOR = (170, 170, 170)
HELM = (150, 150, 150)
TORSO = (100, 100, 100)
SHIELD = (174, 88, 11)

# Initialize world
name = "proj"
width = 1200
height = 800
screen = rw.newDisplay(width, height, name)

target1 = dw.loadImage("target1.png")
target2 = dw.loadImage("target2.png")
target3 = dw.loadImage("target3.png")
target4 = dw.loadImage("target4.png")
target5 = dw.loadImage("target5.png")


class Target(object):
    def __init__(self, X, Y, screen):
        self.Xcoord = X
        self.Ycoord = Y
        self.health = 100
        self.alive = True

    def disp(self, screen):
        if self.health >= 80:
            image = target1
        elif self.health >= 60:
            image = target2
        elif self.health >= 40:
            image = target3
        elif self.health >= 20:
            image = target4
        elif self.health >= 0:
            image = target5
        else:
            self.alive = False

        if self.alive is True:
            dw.draw(image, (self.Xcoord, self.Ycoord))


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
        self.count = 0

    def update(self):
        self.count += 1
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

        if (self.count % 10) == 0:
            self.entities[1].health -= 1

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


class Player(object):
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
        X = (self.Xcoord - 15)
        Y = (self.Ycoord - 15)

        # arrowVerts = [[X, Y-20], [X+15, Y+20], [X, Y+15], [X-15, Y+20]]
        pg.draw.circle(screen, TORSO, [X, Y], 30)
        pg.draw.circle(screen, HELM, [X, Y], 20)
        pg.draw.polygon(screen, SHIELD, self.shieldVerts)
        pg.draw.polygon(screen, VISOR, self.arrowVerts)

    def move(self, axis, mod):
        # (Xmov, Ymov) = change
        if axis is True:
            ang = (self.head + 90) % 360
        else:
            ang = self.head

        if self.brace is True:
            mod = 0
        elif self.block is True:
            mod = mod // 2

        (Xmod, Ymod) = detLegs(mod, ang)
        (self.Xcoord, self.Ycoord) = (self.Xcoord + round(Xmod), self.Ycoord + round(Ymod))
        self.detVerts()

    def rotate(self, clock, ang):
        if self.brace is True:
            ang = randint(0, 1)
            shieldSpace = 40
        elif self.block is True:
            ang = ang // 2

        if clock is False:
            ang = -ang
        self.head = (self.head + ang) % 360
        self.rotVerts()

    def slash(self, targets):
        pass

    def rotVerts(self):
        (helmX, helmY) = detLegs(25, self.head)
        self.locArrowVerts = [detLegs(15, self.head, helmX, helmY), detLegs(25, (self.head + 135) % 360, helmX, helmY), detLegs(10, (self.head + 180) % 360, helmX, helmY), detLegs(25, (self.head + 225) % 360, helmX, helmY)]

        if self.brace is False:
            shieldSpace = 40
        else:
            shieldSpace = 50

        if (self.block is True) or (self.brace is True):
            self.shieldHead = (self.head - 5) % 360
            print("iz tru, shieldHead =", self.shieldHead, "head =", self.head)
        else:
            self.shieldHead = (self.head + 300) % 360
            print("iz false, shieldHead =", self.shieldHead, "head =", self.head)
        (shieldX, shieldY) = detLegs(shieldSpace, self.shieldHead)

        self.locShieldVerts = [detLegs(45, (self.shieldHead + 85) % 360, shieldX, shieldY), detLegs(45, (self.shieldHead + 95) % 360, shieldX, shieldY), detLegs(45, (self.shieldHead + 265) % 360, shieldX, shieldY), detLegs(45, (self.shieldHead + 275) % 360, shieldX, shieldY)]

        self.detVerts()

    def detVerts(self):
        X = (self.Xcoord - 15)
        Y = (self.Ycoord - 15)
        self.arrowVerts = handleVerts(X, Y, self.locArrowVerts)
        self.shieldVerts = handleVerts(X, Y, self.locShieldVerts)


def handleVerts(X, Y, local):
    newVerts = []
    for vert in local:
        newVerts.append((vert[0] + X, vert[1] + Y))
    return newVerts


player = Player(150, 150, screen)
target = Target(500, 500, screen)
state = State(screen, [player, target])

state.run()

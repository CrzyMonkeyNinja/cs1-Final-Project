import runWorld as rw
import drawWorld as dw
import pygame as pg
import math
from random import randint

"""mouse-based turning finished; mouse button input added (left and right mouse replaceing k and i); hit detection mostly good, anomaly yet to be investigated"""

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


class Turret(object):
    def __init__(self, X, Y, screen, kind, face=0):
        self.Xcoord = X
        self.Ycoord = Y
        self.health = 100
        self.alive = True
        self.kind = kind
        self.face = face
        if (self.kind == "norm") or (self.kind == "direct"):
            self.tick = randint(0, 59)
            self.mod = 60
        elif (self.kind == "big") or (self.kind == "tracker"):
            self.tick = randint(60, 119)
            self.mod = 120

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
            # pg.draw.circle(screen, BLUE, [self.Xcoord, self.Ycoord], 30)
            dw.draw(image, (self.Xcoord - 20, self.Ycoord - 20))

    def shoot(self, player):
        Xdif = (player.Xcoord - self.Xcoord)
        Ydif = (self.Ycoord - player.Ycoord)
        shootAngle = relHead(Xdif, Ydif)
        if self.kind == "norm":
            newShot = NormalShot(self.Xcoord, self.Ycoord, shootAngle)
        elif self.kind == "big":
            newShot = BigShot(self.Xcoord, self.Ycoord, shootAngle)
        elif self.kind == "direct":
            newShot = NormalShot(self.Xcoord, self.Ycoord, self.face)
        elif self.kind == "tracker":
            newShot = TrackShot(self.Xcoord, self.Ycoord, shootAngle, player)

        return newShot


class NormalShot(object):
    def __init__(self, Xcoord, Ycoord, angle):
        self.Xcoord = Xcoord
        self.Ycoord = Ycoord
        self.angle = angle
        self.speed = 7

    def disp(self):
        pg.draw.circle(screen, BLUE, [round(self.Xcoord), round(self.Ycoord)], 5)

    def move(self):
        (self.Xcoord, self.Ycoord) = detLegs(self.speed, self.angle, self.Xcoord, self.Ycoord)

    def hit(self, target, block=False, brace=False):
        if (block is False) and (brace is False):
            player.damage(1)


class BigShot(object):
    def __init__(self, Xcoord, Ycoord, angle):
        self.Xcoord = Xcoord
        self.Ycoord = Ycoord
        self.angle = angle
        self.speed = 3

    def disp(self):
        pg.draw.circle(screen, RED, [round(self.Xcoord), round(self.Ycoord)], 10)

    def move(self):
        (self.Xcoord, self.Ycoord) = detLegs(self.speed, self.angle, self.Xcoord, self.Ycoord)

    def hit(self, target, block=False, brace=False):
        print("they don got ye")
        if (block is False) and (brace is False):
            player.damage(5)
            (player.Xcoord, player.Ycoord) = detLegs(70, self.angle, player.Xcoord, player.Ycoord)

        elif (block is True) and (brace is False):
            player.damage(1)
            (player.Xcoord, player.Ycoord) = detLegs(30, self.angle, player.Xcoord, player.Ycoord)


class TrackShot(object):
    def __init__(self, Xcoord, Ycoord, angle, target):
        self.Xcoord = Xcoord
        self.Ycoord = Ycoord
        self.angle = angle
        self.target = target
        self.speed = 7
        self.clock = 0

    def disp(self):
        pg.draw.circle(screen, GREEN, [round(self.Xcoord), round(self.Ycoord)], 7)

    def move(self):
        self.clock += 1
        if (self.clock % 3) == 0:
            Xdif = (self.target.Xcoord - self.Xcoord)
            Ydif = (self.Ycoord - self.target.Ycoord)
            shootAngle = relHead(Xdif, Ydif)
        else:
            shootAngle = self.angle
        (self.Xcoord, self.Ycoord) = detLegs(self.speed, shootAngle, self.Xcoord, self.Ycoord)

    def hit(self, target, block=False, brace=False):
        if (block is False) and (brace is False):
            player.damage(1)



def relHead(Xdif, Ydif):

    # this gives the information regarding the relative facings of the object and a target object

    if Xdif == 0 and Ydif > 0:  # on positive Y axis

        targetDirect = 0
        targetHeading = 0

    elif Xdif == 0 and Ydif < 0:  # on negative Y axis

        targetDirect = 0
        targetHeading = 180

    elif Xdif > 0 and Ydif == 0:  # on positive X axis

        targetDirect = 0
        targetHeading = 90

    elif Xdif < 0 and Ydif == 0:  # on negative X axis

        targetDirect = 0
        # targetHeading = 270
        targetHeading = -90

    elif Xdif > 0 and Ydif > 0:  # if the target is in quadrent I

        XoverY = (abs(Ydif) / abs(Xdif))  # generates the "opposite over adjacent for the arc tan to work with"
        targetDirect = (math.atan(XoverY))  # generates the angle between the target's direction and 90 degrees East in radians
        targetHeading = 90 - math.degrees(targetDirect)  # converts the angle to degrees and uses it to find the degrees from 0 degrees North to the tartet's direction

    elif Xdif < 0 and Ydif > 0:  # quadrent II

        XoverY = (abs(Ydif) / abs(Xdif))
        targetDirect = (math.atan(XoverY))
        targetHeading = 270 + math.degrees(targetDirect)
        # targetHeading = -(90 - math.degrees(targetDirect))

    elif Xdif > 0 and Ydif < 0:  # quadrent IV

        XoverY = (abs(Ydif) / abs(Xdif))
        targetDirect = (math.atan(XoverY))
        targetHeading = 90 + math.degrees(targetDirect)

    elif Xdif < 0 and Ydif < 0:  # quadrent III

        XoverY = (abs(Ydif) / abs(Xdif))
        targetDirect = (math.atan(XoverY))
        targetHeading = 270 - math.degrees(targetDirect)
        # targetHeading = -(90 + math.degrees(targetDirect))

    elif Xdif == 0 and Ydif == 0:  # no distance between self and target

        targetHeading = 0

    else:
        print("EVERYTHING EXPLODES")

    # print("targetHeading", targetHeading)

    return targetHeading


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


def getTargets(player, targets):
    targetsUse = []

    for ent in targets:
        Xdif = (ent.Xcoord - player.Xcoord)
        Ydif = (player.Ycoord - ent.Ycoord)
        targetDirect = (relHead(Xdif, Ydif) - player.head) % 360
        targetDist = distForm(Xdif, Ydif)

        # firstly the target must be near enough to strike, secondly
        # it must be within a certain cone of damage in front of the player
        # if (targetDist < 100) and ((0 < targetDirect <
        # upperHitBox)or(lowerHitBox < targetDirect < 360)):
        if (targetDist < 120) and ((0 < targetDirect < 30) or (325 < targetDirect < 360)):
            targetsUse.append(ent)
            pg.draw.circle(screen, RED, [round(ent.Xcoord), round(ent.Ycoord)], 25, 5)
            pg.display.update()

    return targetsUse


class State(object):
    def __init__(self, screen, player, turrets):
        self.screen = screen
        self.player = player
        self.turrets = turrets
        self.shots = []
        self.keys = []
        self.count = 0

    def update(self):
        # print(pg.mouse.get_pressed())
        self.count += 1
        player = self.player
        player.rotate()
        mouseState = pg.mouse.get_pressed()

        functDict = {119: (player.move, False, 3),    # W
                     97: (player.move, True, -3),     # A
                     115: (player.move, False, -3),   # S
                     100: (player.move, True, 3)}     # D
                     # 106: (player.rotate, False, 5),  # J
                     # 108: (player.rotate, True, 5)}   # L
        """
        106:  # I
        107:  # K
        """

        for shot in self.shots:
            shot.move()

        if player.hurtCool > 15:
            player.collide(self.shots)

        for key in self.keys:
            if key in functDict:
                # player.move(functDict[key])
                functDict[key][0](functDict[key][1], functDict[key][2])

        # if ((mouseState[0] is 1) or (107 in self.keys)) and (32 in
        # self.keys) and (99 not in self.keys):
        if  (32 in self.keys) and (mouseState[0] is 0) and (107 not in self.keys) and (99 not in self.keys):
            player.block = True
            player.brace = False
            player.rotVerts()
        elif ((mouseState[0] is 1) or(107 in self.keys)) and (32 in self.keys) and (99 in self.keys):
            player.brace = True
            player.rotVerts()
        else:
            if (player.block is True) or (player.brace is True):
                player.needRot = True
            player.block = False
            player.brace = False
            # player.rotVerts()

        if ((mouseState[0]) or (107 in self.keys)) and (32 not in self.keys) and (99 not in self.keys):
            player.slashDo = True

            # Damage against entities is only considered in the middle
            # of the sword's swing to prevent "spamming" and to ensure
            # floating-point numbers aren't required to keep track of
            # health that decreases by very small increments every frame
            if (player.slashCount % 30) == 0:
                targets = getTargets(player, self.turrets)
            else:
                # targets = []
                targets = getTargets(player, self.turrets)

            player.slash(targets)
        else:
            if player.slashDo is True:
                player.needRot = True
            player.slashDo = False
            player.slashCount = 0

        if player.needRot is True:
            player.rotVerts()
            player.needRot = False

        for tur in self.turrets:
            if tur.alive is False:
                self.turrets.remove(tur)
            if (tur.alive is True) and (tur.tick == (self.count % tur.mod)):
                self.shots.append(tur.shoot(player))

    def display(self):
        dw.fill(dw.black)
        self.player.disp(self.screen)
        for ent in self.turrets:
            ent.disp(self.screen)
        for shot in self.shots:
            shot.disp()

    def end(self):
        result = False
        if ((self.player.Xcoord < 0) or (self.player.Xcoord > width)) or ((self.player.Ycoord < 0) or (self.player.Ycoord > height)):
            result = True
            print("YOU LOSE")
        elif self.player.health <= 0:
            result = True
            print("YOU LOSE")
        elif not self.turrets:
            result = True
            print("YOU WIN")

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
        self.hurt = False
        self.hurtCool = 0
        self.needRot = False
        self.block = False
        self.brace = False
        self.slashDo = False
        self.slashCount = 0
        self.shieldHead = self.head + 300 % 360
        self.swordHead = self.head + 15 % 360
        self.rotVerts()
        self.detVerts()

    def disp(self, screen):
        self.hurtCool += 1
        if self.hurtCool > 15:
            self.hurt = False
        # Draw a circle
        upperHitBox = (self.head + 35) % 360
        lowerHitBox = (self.head - 35) % 360
        (upperBoxX, upperBoxY) = (detLegs(120, round(upperHitBox), round(self.Xcoord), round(self.Ycoord)))
        (lowerBoxX, lowerBoxY) = (detLegs(120, round(lowerHitBox), round(self.Xcoord), round(self.Ycoord)))

        if (self.hurt is True):
            pg.draw.circle(screen, RED, [round(self.Xcoord), round(self.Ycoord)], 35, 5)
        pg.draw.circle(screen, TORSO, [round(self.Xcoord), round(self.Ycoord)], 30)
        pg.draw.circle(screen, HELM, [round(self.Xcoord), round(self.Ycoord)], 20)
        pg.draw.polygon(screen, SHIELD, self.shieldVerts)
        pg.draw.polygon(screen, HELM, self.swordVerts)
        pg.draw.polygon(screen, TORSO, self.hiltVerts)
        pg.draw.polygon(screen, VISOR, self.helmVerts)
        pg.draw.circle(screen, RED, (round(upperBoxX), round(upperBoxY)), 5)
        pg.draw.circle(screen, RED, (round(lowerBoxX), round(lowerBoxY)), 5)
        pg.draw.polygon(screen, RED, ((50, 750), (50, 700), (550, 700), (550, 750)))
        pg.draw.polygon(screen, GREEN, ((50, 750), (50, 700), ((self.health * 5) + 50, 700), ((self.health * 5) + 50, 750)))

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
        else:
            mod = mod

        (Xmod, Ymod) = detLegs(mod, ang)
        (self.Xcoord, self.Ycoord) = (self.Xcoord + Xmod, self.Ycoord + Ymod)
        self.detVerts()

    """
    def rotate(self, clock, ang):
        if self.brace is True:
            ang = randint(0, 1)
        elif self.block is True:
            ang = ang // 2

        if clock is False:
            ang = -ang
        self.head = (self.head + ang) % 360
        self.rotVerts()
    """
    def rotate(self):
        (mouseX, mouseY) = pg.mouse.get_pos()
        Xdif = (mouseX - self.Xcoord)
        Ydif = (self.Ycoord - mouseY)
        mouseDirect =  (relHead(Xdif, Ydif) - self.head) % 360

        if mouseDirect > 180:
            headDif = mouseDirect - 360
        else:
            headDif = mouseDirect

        if self.brace is True:
            headDif = headDif // 30
        elif self.block is True:
            headDif = headDif // 10
        else:
            headDif = headDif // 2

        self.head = (self.head + headDif) % 360
        self.rotVerts()

    def collide(self, shots):
        for shot in shots:
            Xdif = (shot.Xcoord - self.Xcoord)
            Ydif = (self.Ycoord - shot.Ycoord)
            dist = distForm(Xdif, Ydif)
            targetDirect = (relHead(Xdif, Ydif) - player.head) % 360
            if (dist < 25) and (self.block is False) and (self.brace is False):
                shots.remove(shot)
                shot.hit(self)
            elif (dist < 45) and ((0 < targetDirect < 30) or (325 < targetDirect < 360)):
                shot.hit(self, self.block, self.brace)
                shots.remove(shot)
            elif (dist < 25) and not ((0 < targetDirect < 30) or (325 < targetDirect < 360)):
                shot.hit(self)
                shots.remove(shot)

    def damage(self, hurt):
        self.health -= hurt
        self.hurt = True
        self.hurtCool = 0


    def slash(self, targets):
        X = (self.Xcoord - 0)
        Y = (self.Ycoord + 0)

        # print(self.slashCount)
        if targets and (self.slashCount % 30 is 0):
            print("Hit!")
            for targ in targets:
                try:
                    targ.health -= 5
                except AttributeError:
                    pass
        slashRad = math.radians(self.slashCount * 12)

        self.swordHead = (self.head + 40 + (- math.cos(slashRad) * 40)) % 360
        (swordX, swordY) = detLegs(35, self.swordHead)

        self.locSwordVerts = constructVerts(self.swordHead, ((35, 0), (20, 15), (5, 90), (5, 270), (20, 345)))
        self.locHiltVerts = constructVerts(self.swordHead, ((15, 85), (15, 95), (15, 265), (15, 275)))

        self.locSwordVerts = shiftVerts(self.locSwordVerts, swordX, swordY)
        self.locHiltVerts = shiftVerts(self.locHiltVerts, swordX, swordY)
        self.swordVerts = shiftVerts(self.locSwordVerts, X, Y)
        self.hiltVerts = shiftVerts(self.locHiltVerts, X, Y)

        self.slashCount += 1

    def rotVerts(self):
        (helmX, helmY) = detLegs(25, self.head)
        self.locHelmVerts = constructVerts(self.head, ((15, 0), (25, 135), (10, 180), (25, 225)))

        if self.brace is False:
            shieldSpace = 40
        else:
            shieldSpace = 50

        if (self.block is True) or (self.brace is True):
            self.shieldHead = (self.head - 5) % 360
            self.swordHead = (self.head + 60) % 360
            # print("iz tru, shieldHead =", self.shieldHead, "head =", self.head)
        else:
            self.shieldHead = (self.head + 300) % 360
            self.swordHead = (self.head + 50) % 360
            # print("iz false, shieldHead =", self.shieldHead, "head =", self.head)
        (shieldX, shieldY) = detLegs(shieldSpace, self.shieldHead)

        self.locShieldVerts = constructVerts(self.shieldHead, ((45, 85), (45, 95), (45, 265), (45, 275)))


        #self.swordHead = (self.head + 40) % 360
        # print("istruiztru, swordHead =", self.swordHead, "head =", self.head)
        (swordX, swordY) = detLegs(35, self.swordHead)

        self.locSwordVerts = constructVerts(self.swordHead, ((35, 0), (20, 15), (5, 90), (5, 270), (20, 345)))
        self.locHiltVerts = constructVerts(self.swordHead, ((15, 85), (15, 95), (15, 265), (15, 275)))

        self.locHelmVerts = shiftVerts(self.locHelmVerts, helmX, helmY)
        self.locShieldVerts = shiftVerts(self.locShieldVerts, shieldX, shieldY)
        self.locSwordVerts = shiftVerts(self.locSwordVerts, swordX, swordY)
        self.locHiltVerts = shiftVerts(self.locHiltVerts, swordX, swordY)

        self.detVerts()

    def detVerts(self):
        X = (self.Xcoord + 0)
        Y = (self.Ycoord + 0)
        self.helmVerts = shiftVerts(self.locHelmVerts, X, Y)
        self.shieldVerts = shiftVerts(self.locShieldVerts, X, Y)
        self.swordVerts = shiftVerts(self.locSwordVerts, X, Y)
        self.hiltVerts = shiftVerts(self.locHiltVerts, X, Y)


def constructVerts(base, mods):
    # print("mods:", mods)
    vertList = []
    for pair in mods:
        vertList.append(detLegs(pair[0], (base + pair[1]) % 360))
    # print(vertList)
    return vertList


def shiftVerts(local, X, Y):
    # print("local:", local)
    newVerts = []
    for vert in local:
        newVerts.append((vert[0] + X, vert[1] + Y))
    return newVerts


def distForm(Xval, Yval):
    dist = ((Xval ** 2) + (Yval ** 2)) ** (1/2)

    return dist


player = Player(150, 150, screen)
turret1 = Turret(500, 500, screen, "direct", randint(0, 359))
turret2 = Turret(250, 250, screen, "tracker")

turrets = []

for count in "123":
    turret1 = Turret(randint(100, 1100), randint(100, 700), screen, "direct", randint(0, 359))
    turret3 = Turret(randint(100, 1100), randint(100, 700), screen, "norm", randint(0, 359))
    turrets.append(turret1)
    turrets.append(turret2)
    turrets.append(turret3)

for count in "12":
    turret1 = Turret(randint(100, 1100), randint(100, 700), screen, "tracker")
    turret2 = Turret(randint(100, 1100), randint(100, 700), screen, "big")
    turrets.append(turret1)
    turrets.append(turret2)

state = State(screen, player, turrets)

state.run()

"""
        #self.slashCount = 15
        print(self.slashCount)
        X = (self.Xcoord - 15)
        Y = (self.Ycoord - 15)
        self.slashHead = (self.head + (35 - ((self.slashCount // 5) * 10))) % 360
        #self.slashHead = (self.head + 40) % 360
        slashVerts0 = ((0, 0), (20, 0), (35, 5), (30, 25), (28, 45), (25, 75), (10, 90))
        slashVerts1 = ((0, 0), (20, 0), (35, 5), (35, 35), (35, 55), (35, 80), (20, 100))
        slashVerts2 = ((0, 0), (20, 0), (35, 5), (40, 65), (40, 75), (40, 90), (25, 110))
        slashVerts3 = ((0, 0), (20, 0), (35, 5), (35, 75), (40, 85), (45, 100), (40, 110))

        slashDict = {0: slashVerts0,
                     1: slashVerts1,
                     2: slashVerts2,
                     3: slashVerts3}

        (slashX, slashY) = detLegs(35, self.slashHead)

        locSlashVerts = constructVerts(self.slashHead, slashDict[self.slashCount // 5])
        locSlashVerts = shiftVerts(locSlashVerts, slashX, slashY)
        self.slashCount = (self.slashCount + 1) % 15
        self.slashVerts = shiftVerts(locSlashVerts, X, Y)
"""

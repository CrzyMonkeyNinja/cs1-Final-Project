import runWorld as rw
import drawWorld as dw
import pygame as pg
import math
from random import randint

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
name = "Beauregarde of Flankingshire"
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

        # the normal (aiming) turret and the single-direction
        # (non-aiming) turrets both shoot once per second
        if (self.kind == "norm") or (self.kind == "direct"):
            self.tick = randint(0, 59)
            self.mod = 60
        # the big and tracking turrets shoot once per two seconds
        elif (self.kind == "big") or (self.kind == "tracker"):
            self.tick = randint(60, 119)
            self.mod = 120

    def disp(self, screen):
        # the turret displays a different image the less health it
        # has, to indicate to the player how damaged it is
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

        # the image only displays if the turret is alive
        if self.alive is True:
            # pg.draw.circle(screen, BLUE, [self.Xcoord, self.Ycoord], 30)
            dw.draw(image, (self.Xcoord - 20, self.Ycoord - 20))

    def shoot(self, player):
        # the turret first determines what direction the player is in
        Xdif = (player.Xcoord - self.Xcoord)
        Ydif = (self.Ycoord - player.Ycoord)
        shootAngle = relHead(Xdif, Ydif)

        # the turret creates a new projectile, the type of which
        # dependes on the type of the turret
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
        # normal shot displayes a blue circles at its coordinates
        pg.draw.circle(screen, BLUE, [round(self.Xcoord), round(self.Ycoord)], 5)

    def move(self):
        # normal shot simply moves its speed on the angle it was shot at
        (self.Xcoord, self.Ycoord) = detLegs(self.speed, self.angle, self.Xcoord, self.Ycoord)

    def hit(self, target, block=False, brace=False):
        # if the shot collides with the player and the player is not
        # blocking, then the player is dealth one damage
        if (block is False) and (brace is False):
            player.damage(1)


class BigShot(object):
    def __init__(self, Xcoord, Ycoord, angle):
        self.Xcoord = Xcoord
        self.Ycoord = Ycoord
        self.angle = angle
        self.speed = 5 # big shot moves more slowly than other shot types

    def disp(self):
        # the big shot displays a large, red circle at its coordinates
        pg.draw.circle(screen, RED, [round(self.Xcoord), round(self.Ycoord)], 10)

    def move(self):
        # again, the big shot simply moves in the direction it was shot
        (self.Xcoord, self.Ycoord) = detLegs(self.speed, self.angle, self.Xcoord, self.Ycoord)

    def hit(self, target, block=False, brace=False):
        # if the player is not blocking at all, then th eplayer is
        # knocked back 70 pixels and damaged for 5 points
        if (block is False) and (brace is False):
            player.damage(5)
            (player.Xcoord, player.Ycoord) = detLegs(70, self.angle, player.Xcoord, player.Ycoord)

        # if the player is only blocking but not bracing, the player
        # is only knocked back 30 pixels and damages for 1 point
        elif (block is True) and (brace is False):
            player.damage(1)
            (player.Xcoord, player.Ycoord) = detLegs(30, self.angle, player.Xcoord, player.Ycoord)

        # thus if the player is bracing, they suffer no effect

class TrackShot(object):
    def __init__(self, Xcoord, Ycoord, angle, target):
        self.Xcoord = Xcoord
        self.Ycoord = Ycoord
        self.angle = angle
        self.target = target
        self.speed = 5 # the tracking shot moves at a moderate speed
        self.clock = 0

    def disp(self):
        # the shot displays a green circle at its coordinates (rounded)
        pg.draw.circle(screen, GREEN, [round(self.Xcoord), round(self.Ycoord)], 7)

    def move(self):
        self.clock += 1  # the count of the frames the shot has been
                         # active is increased by one

        Xdif = (self.target.Xcoord - self.Xcoord)
        Ydif = (self.Ycoord - self.target.Ycoord)

        if ((self.clock % 3) == 0):  # the shot only changes course
                                    # every 3 frames
            self.angle = track(Xdif, Ydif, self.angle)

        # the shot moves by using its speed as the hypotenuse in the
        # direction it is facing and adding the legs to its coordinates
        (self.Xcoord, self.Ycoord) = detLegs(self.speed, self.angle, self.Xcoord, self.Ycoord)

    def hit(self, target, block=False, brace=False):
        # if the shot hits, and the player is not blocking, the player
        # is damaged by one point
        if (block is False) and (brace is False):
            player.damage(1)


def track(Xdif, Ydif, angle):
    # the tracker determines the heading of the player relative to
    # where it is facing and turns towards the player. If the angle it
    # needs to turn is more than 5, however, it only turns 5 degrees
    # towards the player
    targetDirect = relHead(Xdif, Ydif)
    headVary = (targetDirect - angle) % 360

    if (0 <= headVary <= 5) or (355 <= headVary < 360):
        angle = targetDirect
    elif (0 < headVary < 5):
        angle = (angle + 5) % 360
    else:
        angle = (angle - 5) % 360

    return angle


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
    # existing X and Y values (default of zero)

    # print("ang:", ang)

    if ang == 0:  # on negative Y axis (graphically up)
        Y -= hyp
        # print("X = X")
        # print("Y +=", hyp)

    elif ang == 180:  # on positive Y axis (graphically down)
        Y += hyp
        # print("X = X")
        # print("Y -=", hyp)

    elif ang == 90:  # on positive X axis (graphically right)
        X += hyp
        # print("X +=", hyp)
        # print("Y = Y")

    elif ang == 270:  # on negative X axis (graphically left)
        X -= hyp
        # print("X -=", hyp)
        # print("Y = Y")

    elif ang > 0 and ang < 90:  # in quadrant I
        ang = math.radians(90 - ang)
        X += hyp * math.cos(ang)
        Y -= hyp * math.sin(ang)
        # print("X +=", (hyp*(math.cos(ang))) )
        # print("Y +=", (hyp*(math.sin(ang))) )

    elif ang > 90 and ang < 180:  # in quadrant IV
        ang = math.radians(ang - 90)
        X += hyp * math.cos(ang)
        Y += hyp * math.sin(ang)
        # print("X +=", (hyp*(math.cos(ang))) )
        # print("Y -=", (hyp*(math.sin(ang))) )

    elif ang > 180 and ang < 270:  # in quadrant III
        ang = math.radians(270 - ang)
        X -= hyp * math.cos(ang)
        Y += hyp * math.sin(ang)
        # print("X -=", (hyp*(math.cos(ang))) )
        # print("Y -=", (hyp*(math.sin(ang))) )

    elif ang > 270 and ang < 360:  # in quadrant II
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
        self.screen = screen  # this is the display things are drawn on
        self.player = player  # this is the player object
        self.turrets = turrets  # this is a list of turret objects
        self.shots = []  # this is the list of projectiles
        self.keys = []  # this is the list of currently-pressed keys
        self.count = 0  # this is the number of frames the game has
                        # been running

    def update(self):
        # print(pg.mouse.get_pressed())
        self.count += 1  # this increases the count of how many frames
                         # the game has been running

        player = self.player  # this assigns the player a simple name
                              # for ease of coding and readablility

        player.rotate()  # this rotates the player based on the mouse position

        mouseState = pg.mouse.get_pressed()  # this assigns a simple
                                        # name to the mouse state for
                                        # ease of coding and readability

        # this dictionary determines what function will be run and
        # with what parameters when certain keys are pressed
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

        # this removes any shots that are off screen from teh active
        # list and moves those that are still in play based on their
        # speed and direction of travel
        for shot in self.shots:
            if ((shot.Xcoord < 0) or (shot.Xcoord > width)) or ((shot.Ycoord < 0) or (shot.Ycoord > height)):
                self.shots.remove(shot)
            else:
                shot.move()

        # after the shots have moved, the player then checks if any
        # are either close enough to block or to hurt them
        player.collide(self.shots)

        # this loop looks through all of the currently pressed keys
        # and runs the function assigned to them in the above
        # dictionary with the given parameters
        for key in self.keys:
            if key in functDict:
                functDict[key][0](functDict[key][1], functDict[key][2])

        # if the spacebar is pressed and neither the left mouse button
        # nor k nor c are pressed, then the player will raise the
        # block flag and re-map their verticies in order to accomodate
        # the bracing animation
        if (32 in self.keys) and (mouseState[0] is 0) and (107 not in self.keys) and (99 not in self.keys):
            player.block = True
            player.brace = False
            player.needRot = True
        # if teh spacebar and c are pressed and neither the left mosue
        # button nor k are pressed, then the player will raise the
        # brace flag and re-map their verticies in order to accomodate
        # the bracing animation
        elif ((mouseState[0] is 0) or(107 not in self.keys)) and (32 in self.keys) and (99 in self.keys):
            player.brace = True
            player.needRot = True
        # if either of the above key combinations cease to be, then
        # the blocking and brace flags are ensured to be lowered and
        # if the flags had been raised in the first place, then the
        # player re-maps their verticies in order to accomodate the
        # ceasing of the brace or block animation
        else:
            if (player.block is True) or (player.brace is True):
                player.needRot = True
            player.block = False
            player.brace = False
            # player.rotVerts()

        # if the left mouse button is pressed or if k is pressed and
        # neither the spacebar or c are pressed, then the player will
        # slash (with the spacebar or c a different action would be performed)
        if ((mouseState[0]) or (107 in self.keys)) and (32 not in self.keys) and (99 not in self.keys):
            player.slashDo = True

            # Damage against entities is only considered in the middle
            # of the sword's swing to prevent "spamming" and to ensure
            # floating-point numbers aren't required to keep track of
            # health, as would be necessary if it decreased by very
            # small increments every frame as opposed to distinct
            # increments every 30 frames (half-second)
            if (player.slashCount % 30) == 0:
                targets = getTargets(player, self.turrets)
            else:
                # targets = []
                targets = getTargets(player, self.turrets)

            player.slash(targets)
        # if the slashing key combination is not met, then the slashDo
        # flag is ensured to be down and the counter recording how
        # many frames the player has been slashing is set to zero;
        # furthermore if the slashDo flag was up, the player needs to
        # re-map their verticies to ensure the cancelation of the
        # slashing animation
        else:
            if player.slashDo is True:
                player.needRot = True
            player.slashDo = False
            player.slashCount = 0

        # if the flag denoting a need to re-map verticies is up, then
        # the verticies will be re-mapped
        if player.needRot is True:
            player.rotVerts()
            player.needRot = False

        # here dead turrets are removed from the turret list and
        # those that are alive fire if the counter recording how many
        # frames the game has been running matches values modulating
        # how quickly they can fire
        for tur in self.turrets:
            if tur.alive is False:
                self.turrets.remove(tur)
            if (tur.alive is True) and (tur.tick == (self.count % tur.mod)):
                self.shots.append(tur.shoot(player))

    def display(self):
        # first the screen is wiped clean, then the player is
        # displayed, and the two loops display all of the turrets and
        # all of the active projectiles
        dw.fill(dw.black)
        self.player.disp(self.screen)
        for ent in self.turrets:
            ent.disp(self.screen)
        for shot in self.shots:
            shot.disp()

    def end(self):  # this ends the game if certain parameters are met

        result = False  # the default response to the question "is the
                        # game done?" is "no"

        # if the player moves off the screen, the game ends and the
        # player loses
        if ((self.player.Xcoord < 0) or (self.player.Xcoord > width)) or ((self.player.Ycoord < 0) or (self.player.Ycoord > height)):
            result = True
            print("YOU LOSE")

        # if the player's health is dropped below zero, the games ends
        # and the player loses
        elif self.player.health <= 0:
            result = True
            print("YOU LOSE")

        # if there are no more living turrets, the game ends and the
        # player wins
        elif not self.turrets:
            result = True
            print("YOU WIN")

        return result

    def handleEvent(self, event):  # here all keypresses are handled
        """
        keyDict = {119: "W",
                   97: "A",
                   115: "S",
                   100: "D",
                   113: "Q",
                   101: "E"}
        """

        # if a key is pressed, it is added to the list of active keys
        if (event.type == pg.KEYDOWN):
            # self.keys.append(keyDict[event.key])
            self.keys.append(event.key)
            # print(event.key)

        # if a key is unpressed, it is removed from the list of active keys
        elif (event.type == pg.KEYUP) and (event.key in self.keys):
            # self.keys.remove(keyDict[event.key])
            self.keys.remove(event.key)
            # print(event.key)

    def run(self):  # this initializes the games loop
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
        # this counts how many frames it has been since the player was
        # last hurt; if it is greater than 15, the hurt flag is lowered
        self.hurtCool += 1
        if self.hurtCool > 15:
            self.hurt = False

        # this determines the positions of the two red circles which
        # the area in which the player deals slashing damage
        upperHitBox = (self.head + 35) % 360
        lowerHitBox = (self.head - 35) % 360
        (upperBoxX, upperBoxY) = (detLegs(120, round(upperHitBox), round(self.Xcoord), round(self.Ycoord)))
        (lowerBoxX, lowerBoxY) = (detLegs(120, round(lowerHitBox), round(self.Xcoord), round(self.Ycoord)))

        # if the hurt flag is up, then a red ring is drawn around the player
        if (self.hurt is True):
            pg.draw.circle(screen, RED, [round(self.Xcoord), round(self.Ycoord)], 35, 5)

        # this draws the two circles of the player's torso and head
        pg.draw.circle(screen, TORSO, [round(self.Xcoord), round(self.Ycoord)], 30)
        pg.draw.circle(screen, HELM, [round(self.Xcoord), round(self.Ycoord)], 20)

        # this draws the player's shield
        pg.draw.polygon(screen, SHIELD, self.shieldVerts)

        # this draws the player's sword
        pg.draw.polygon(screen, HELM, self.swordVerts)
        pg.draw.polygon(screen, TORSO, self.hiltVerts)

        # this draws the pointed visor last so that it is printed over
        # the shield; the visor serves to show what direction the
        # player is facing
        pg.draw.polygon(screen, VISOR, self.helmVerts)

        # these actually draw the red circles denoting the area in
        # which the player deals slashing damage
        pg.draw.circle(screen, RED, (round(upperBoxX), round(upperBoxY)), 5)
        pg.draw.circle(screen, RED, (round(lowerBoxX), round(lowerBoxY)), 5)

        # these two lines draw the health bar
        pg.draw.polygon(screen, RED, ((50, 750), (50, 700), (550, 700), (550, 750)))
        pg.draw.polygon(screen, GREEN, ((50, 750), (50, 700), ((self.health * 5) + 50, 700), ((self.health * 5) + 50, 750)))

    def move(self, axis, mod):
        # if the axis is true, then the mod is considered to be
        # lateral movement, so the player is moved at 90 degrees plus
        # their heading
        if axis is True:
            ang = (self.head + 90) % 360
        else:
            ang = self.head

        # if the player is braced, they cannot move
        if self.brace is True:
            mod = 0
        # if the player is blocking, they move half speed
        elif self.block is True:
            mod = mod // 2
        else:
            mod = mod

        # this changes the player's coordinates
        (self.Xcoord, self.Ycoord) = detLegs(mod, ang, self.Xcoord, self.Ycoord)
        self.detVerts() # the verticies that define the player's sword
                        # and helmet and shield are then translated up
                        # and down, but not rotated

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
        # rotates the player towards the mouse position
        (mouseX, mouseY) = pg.mouse.get_pos()  # gets the mouse
                                        # position from pygame
        Xdif = (mouseX - self.Xcoord)  # determines difference in X
        Ydif = (self.Ycoord - mouseY)  # determines difference in Y
        mouseDirect =  (relHead(Xdif, Ydif) - self.head) % 360  # establishes the
                                        # degrees between the
                                        # direction the player is
                                        # facing and the mouse

        # mouseDirect is in terms of degrees from 0 -> 360; this
        # brings it into the frame form -180 -> 180 so that it can be
        # more easily divided into sensible pieces
        if mouseDirect > 180:
            headDif = mouseDirect - 360
        else:
            headDif = mouseDirect

        # this makes it such that the rotation is never instantaneous,
        # and is reduced when blocking or bracing
        if self.brace is True:
            headDif = headDif // 30
        elif self.block is True:
            headDif = headDif // 10
        else:
            headDif = headDif // 2

        # this keeps the head between 0 and 360
        self.head = (self.head + headDif) % 360
        # this then re-maps the verticies of the player for display
        self.rotVerts()

    def collide(self, shots):
        # here it is determined whether any active projectile collides
        # with the player or is blocked
        for shot in shots:
            # determining X and Y difference
            Xdif = (shot.Xcoord - self.Xcoord)
            Ydif = (self.Ycoord - shot.Ycoord)
            dist = distForm(Xdif, Ydif)  # establish the distance
                                        # between the player and shot
            targetDirect = (relHead(Xdif, Ydif) - player.head) % 360  # again establishes
                                                                     # degrees between the
                                                                     # direction the player is
                                                                     # facing and the mouse

            # if the shot is within impact distance (25 pixels), and
            # the player is neither blocking nor bracing, the shot is
            # removed and if it has been more than 15 frames since the
            # player was last hurt, the player is then effected by the shot
            if (dist < 25) and (self.block is False) and (self.brace is False):
                shots.remove(shot)
                if self.hurtCool > 15:
                    shot.hit(self)
            # if the shot is within blocking distance (45 pixels), and
            # the player, and is within proper blocking angles, and it
            # has been more than 15 frames since the player was last
            # hurt, the player is then effected by the shot (either by
            # blocking it or bracing against it)
            elif (dist < 45) and ((0 < targetDirect < 30) or (325 < targetDirect < 360)):
                if self.hurtCool > 15:
                    shot.hit(self, self.block, self.brace)
                shots.remove(shot)
            # if the shot is within impact distance (25 pixels), and
            # it is not within the proper blocking angles, and it has
            # been more than 15 frames since the player was last hurt,
            # the player is then effected by the shot
            elif (dist < 25) and not ((0 < targetDirect < 30) or (325 < targetDirect < 360)):
                if self.hurtCool > 15:
                    shot.hit(self)
                shots.remove(shot)

    def damage(self, hurt):
        # here the player's health is reduced, the hurt flag is
        # raised, and the count of frames since the player was last
        # hurt is reset to 0
        self.health -= hurt
        self.hurt = True
        self.hurtCool = 0

    def slash(self, targets):
        # here the player attempts to do damage to the objects in
        # front of it by slashing

        # establish simple variables for X and Y for ease of reading
        # and writing
        X = (self.Xcoord)
        Y = (self.Ycoord)

        # print(self.slashCount)
        # if there are things to hurt in the targets list, and if the
        # player has been slashing for a multiple of 30 frames, try to
        # decrease the target's health by five, so long as the target
        # has a health attribute
        if targets and (self.slashCount % 30 is 0):
            # print("Hit!")
            for targ in targets:
                try:
                    targ.health -= 5
                except AttributeError:
                    pass
        # establishes a modifier for the angle at which to display the
        # player's sword based on the number of frames the player has
        # been slashing for
        slashRad = math.radians(self.slashCount * 12)

        # the angle at which the sword is displayed at is established
        self.swordHead = (self.head + 40 + (- math.cos(slashRad) * 40)) % 360
        (swordX, swordY) = detLegs(35, self.swordHead)  # the X Y of
                                        # the sword's base is
                                        # determined based on the
                                        # angle at which the sword is
                                        # being displayed

        # the verticies of the sword and hilt are established relative
        # to the sword's base point
        self.locSwordVerts = constructVerts(self.swordHead, ((35, 0), (20, 15), (5, 90), (5, 270), (20, 345)))
        self.locHiltVerts = constructVerts(self.swordHead, ((15, 85), (15, 95), (15, 265), (15, 275)))

        # the sword and hilt's verticies are then shifted based on the
        # X, Y of the sword's base
        self.locSwordVerts = shiftVerts(self.locSwordVerts, swordX, swordY)
        self.locHiltVerts = shiftVerts(self.locHiltVerts, swordX, swordY)

        # the sword and hilt's verticies are then shifted out to be
        # properly positioned relative to the player
        self.swordVerts = shiftVerts(self.locSwordVerts, X, Y)
        self.hiltVerts = shiftVerts(self.locHiltVerts, X, Y)

        self.slashCount += 1

    def rotVerts(self):
        # all of the player's verticies are re-mapped based on the
        # angle at which it is facing

        # establish the base point for the helm
        (helmX, helmY) = detLegs(25, self.head)
        # construct the local verticies of the helm around the above
        # base point
        self.locHelmVerts = constructVerts(self.head, ((15, 0), (25, 135), (10, 180), (25, 225)))

        # establish the space between the player and the shield's base point
        if self.brace is False:
            shieldSpace = 40
        else:
            shieldSpace = 50

        # determine the angle at which the shield is displayed based
        # on whether the player is blocking or bracing or not
        if (self.block is True) or (self.brace is True):
            self.shieldHead = (self.head - 5) % 360
            self.swordHead = (self.head + 60) % 360
            # print("iz tru, shieldHead =", self.shieldHead, "head =", self.head)
        else:
            self.shieldHead = (self.head + 300) % 360
            self.swordHead = (self.head + 50) % 360
            # print("iz false, shieldHead =", self.shieldHead, "head =", self.head)

        # establish the base X Y of the shield based on the shield
        # space and the angle at which the shield is displayed
        (shieldX, shieldY) = detLegs(shieldSpace, self.shieldHead)

        # establish the local verticies around the base X Y point of
        # the shield
        self.locShieldVerts = constructVerts(self.shieldHead, ((45, 85), (45, 95), (45, 265), (45, 275)))


        #self.swordHead = (self.head + 40) % 360
        # print("istruiztru, swordHead =", self.swordHead, "head =", self.head)

        # establish the base X Y of the sword
        (swordX, swordY) = detLegs(35, self.swordHead)

        # establish the local verticies of the sword
        self.locSwordVerts = constructVerts(self.swordHead, ((35, 0), (20, 15), (5, 90), (5, 270), (20, 345)))
        self.locHiltVerts = constructVerts(self.swordHead, ((15, 85), (15, 95), (15, 265), (15, 275)))

        # shift the X Y of the local verticies based on their base points
        self.locHelmVerts = shiftVerts(self.locHelmVerts, helmX, helmY)
        self.locShieldVerts = shiftVerts(self.locShieldVerts, shieldX, shieldY)
        self.locSwordVerts = shiftVerts(self.locSwordVerts, swordX, swordY)
        self.locHiltVerts = shiftVerts(self.locHiltVerts, swordX, swordY)

        self.detVerts()

    def detVerts(self):
        # shift the local verticies into the absolute frame
        X = (self.Xcoord + 0)
        Y = (self.Ycoord + 0)
        self.helmVerts = shiftVerts(self.locHelmVerts, X, Y)
        self.shieldVerts = shiftVerts(self.locShieldVerts, X, Y)
        self.swordVerts = shiftVerts(self.locSwordVerts, X, Y)
        self.hiltVerts = shiftVerts(self.locHiltVerts, X, Y)


def constructVerts(base, mods):
    # construct a list of local verticies based on a base angle and a
    # list of X Y tuples
    # print("mods:", mods)
    vertList = []
    for pair in mods:
        vertList.append(detLegs(pair[0], (base + pair[1]) % 360))
    # print(vertList)
    return vertList


def shiftVerts(local, X, Y):
    # shift a list of local verticies based on a given X Y
    # print("local:", local)
    newVerts = []
    for vert in local:
        newVerts.append((vert[0] + X, vert[1] + Y))
    return newVerts


def distForm(Xval, Yval):
    # establish the distance between two points based on the
    # differences between their X and Y points
    dist = ((Xval ** 2) + (Yval ** 2)) ** (1/2)

    return dist


player = Player(600, 400, screen)
turret1 = Turret(500, 500, screen, "direct", randint(0, 359))
turret2 = Turret(randint(100, 1100), randint(100, 700), screen, "norm")
turret3 = Turret(randint(100, 1100), randint(100, 700), screen, "big")
turret4 = Turret(250, 250, screen, "tracker")

turrets = []


for count in "123":
    turret1 = Turret(randint(100, 1100), randint(100, 700), screen, "direct", randint(0, 359))
    turret2 = Turret(randint(100, 1100), randint(100, 700), screen, "direct", randint(0, 359))
    turrets.append(turret1)
    turrets.append(turret2)

for count in "12":
    turret1 = Turret(randint(100, 1100), randint(100, 700), screen, "tracker")
    turret2 = Turret(randint(100, 1100), randint(100, 700), screen, "big")
    turrets.append(turret1)
    turrets.append(turret2)


state = State(screen, player, turrets)  # build the state

state.run()  # run the game

"""Dead code for an attempted fancy slashing animation

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

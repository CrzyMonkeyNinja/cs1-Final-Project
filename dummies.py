import runWorld as rw
import drawWorld as dw
import pygame as pg
from random import randint

################################################################

# This program is an interactive simulation/game. Two characters move
# across the screen, one starting on the left (controlled by [W,A,S,D]),
# the other on the right (controlled by [I,J,K,L]).The goal of this game is
# to knock one's opponant out of the screen by slapping them backwards
# with [X] or [C] for the left player and [,] or [.] for the right player.
#
# Each player has a limited number of slaps at any one time, though
# they recharge over time. The number of slaps for each player is
# displayed at the bottom of the screen at the side they started
# from. Slaps that are made when too far from your opponant have no
# effect on your opponant, but are still deducted from your slap count.
#
# The state of the game is represented by a tuple containing x position, y
# position, state of arm (up or down), and slap-charge for both players.
#
# The game ends when either player leaves the "ring" by fleeing
# or by being pushed out by the other player's slaps.
#
# HI LUDI FACTI ANNO MMXV MANV WAEATIS AMICORUMQUE
#
# Made by Team Wyatt and Friends in November of 2015.
#
# Team Wyatt and Friends is comprised of Matthew Boustany, Catherine
# Jin, and Simon Whittle (there is no Wyatt, we are just the friends).

################################################################

# Initialize world
name = "!~SMACK~!"
width = 1200
height = 800
rw.newDisplay(width, height, name)

################################################################

# Display the state by drawing two torsos with arms.
rightTorso = dw.loadImage("T_R.png")
rightHigh = dw.loadImage("R_H.png")  # -150, +255
rightLow = dw.loadImage("R_L.png")  # -150, -100

leftTorso = dw.loadImage("T_L.png")
leftHigh = dw.loadImage("L_H.png")  # 200, +225
leftLow = dw.loadImage("L_L.png")  # 200, -100


def updateDisplay(state):
    dw.fill(dw.black)
    if (state[4] == 1):  # if state sub 4 is 1, draw left arm up
        dw.draw(leftHigh, (state[0] + 200, state[1] - 100))
    else:  # else draw left arm down
        dw.draw(leftLow, (state[0] + 200, state[1] + 225))
    if (state[5] == 1):  # if state sub 5 is 1, draw right arm up
        dw.draw(rightHigh, (state[2] - 150, state[3] - 100))
    else:  # else draw right arm down
        dw.draw(rightLow, (state[2] - 150, state[3] + 225))

    if (state[6] >= 0):  # If slapCharge is positive, no slaps
        slapNumberLeft = "0"
    else:  # if negative, one slap per 60 frames of charge / one second
        slapNumberLeft = str(-state[6]//60)

    if (state[7] >= 0):  # If slapCharge is positive, no slaps
        slapNumberRight = "0"
    else:  # if negative, one slap per 60 frames of charge / one second
        slapNumberRight = str(-state[7]//60)

    slapCounterLeft = dw.makeLabel(slapNumberLeft,
                                   "Times New Roman, Ariel", 72, dw.white)
    slapCounterRight = dw.makeLabel(slapNumberRight,
                                    "Times New Roman, Ariel", 72, dw.white)

    dw.draw(rightTorso, (state[2], state[3]))
    dw.draw(leftTorso, (state[0], state[1]))
    dw.draw(slapCounterLeft, (50, 650))
    dw.draw(slapCounterRight, (1100, 650))


################################################################
# state -> state
def updateState(state):
    return(state[0], state[1], state[2], state[3], state[4], state[5],
           state[6] - 1, state[7] - 1)  # reduce slapCharge by 1 every frame

################################################################

# Terminate the simulation when the x coord reaches the screen edge,
# that is, when pos is less then zero or greater than the screen width
# state -> bool, or when y coord reaches screen edge for either image.


def endState(state):

    result = False

    leftWid = state[0] + 150
    leftHi = state[1] + 225
    rightWid = state[2] + 150
    rightHi = state[3] + 225

    if (leftWid > width or leftWid < 0) or (leftHi > height or leftHi < 0):
        result = True
        print("Player 2 Wins! (That's the guy on the right)")
        # If player 1 moves off-screen, player 2 wins

    elif (rightWid > width or rightWid < 0) or (rightHi > height or rightHi < 0): 
        result = True
        print("Player 1 Wins! (That's the guy on the left)")
        # If player 2 moves off-screen, player 1 wins

    else:
        result = False

    return result

################################################################

# state -> event -> state


def handleEvent(state, event):
    state0mod = 0
    state1mod = 0
    state2mod = 0
    state3mod = 0

    state4 = state[4]
    state5 = state[5]

    state6mod = 0
    state7mod = 0

    if (event.type == pg.KEYDOWN):
        if (event.key == 119):  # W
            state1mod -= 10
        if (event.key == 97):   # A
            state0mod -= 10
        if (event.key == 115):  # S
            state1mod += 10
        if (event.key == 100):  # D
            state0mod += 10
        if (event.key == 106):  # I
            state2mod -= 10
        if (event.key == 105):  # J
            state3mod -= 10
        if (event.key == 107):  # K
            state3mod += 10
        if (event.key == 108):  # L
            state2mod += 10

        if(event.key == 99 or event.key == 120) and (state[6] < 0):  # X or C
            state4 = (1 + state[4]) % 2  # change arm state (up>down, etc)
            state6mod += 60  # increase slapCharge (one second cooldown)
            if(0 <= (state[2] - state[0]) <= 400) and (abs(state[3] - state[1]) <= 300):  # if in range, enemy moved back
                state2mod += 75

        if(event.key == 44 or event.key == 46) and (state[7] < 0):  # , or .
            state5 = (1 + state[5]) % 2  # change arm state
            state7mod += 60  # increase slapCharge
            if(0 <= (state[2] - state[0]) <= 400) and (abs(state[3] - state[1]) <= 300):  # if in range, enemy moved back
                state0mod -= 75

    # Returns modified state
    return(state[0] + state0mod, state[1] + state1mod, state[2] + state2mod, state[3] + state3mod, state4, state5, state[6] + state6mod, state[7] + state7mod)

################################################################
# State is composed of (leftX, leftY, rightX, rightY, leftArmState (up
# or down), rightArmState, leftSlapCharge, and rightSlapCharge)
initState = (100, 175, 900, 175, randint(0, 1), randint(0, 1), -120, -120)

# Run the simulation no faster than 60 frames per second
frameRate = 60

# Run the simulation!
rw.runWorld(initState, updateDisplay, updateState, handleEvent,
            endState, frameRate)

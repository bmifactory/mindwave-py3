'''
Created on 2018. 6. 26.
@author: Kipom
Default address: CC:78:AB:25:41:3A
'''
import pygame
import random
from numpy import *
from pygame import *
from mindwave3.parser import ThinkGearParser, TimeSeriesRecorder
from startup_mindwave import *

description = """Example for Mindwave Python 3
"""

# Set mindwave mobile
raw_eeg = True
gain = 1.0
attention_value = 0
Th_attention = 50
attention_duration = 0

# Set pygame parameter
fullscreen = False
bg_file = "background_1360x768.jpg"

socket, args = mindwave_startup(description=description)
recorder = TimeSeriesRecorder()
parser = ThinkGearParser(recorders=[recorder])

def pygame_init():
    global window, fullscreen, fpsClock, address_txt_img, font, background_img
    global whiteColor, greenColor, attentionColor, eegColor

    pygame.init()
    font = pygame.font.Font("freesansbold.ttf", 20)
    whiteColor = pygame.Color(255, 255, 255)
    greenColor = pygame.Color(0, 255, 0)
    eegColor = pygame.Color(255, 255, 0)
    attentionColor = pygame.Color(10, 85, 145)

    fpsClock = pygame.time.Clock()
    pygame.display.set_caption("Neurosky")
    if fullscreen is True:
        window = pygame.display.set_mode((1360, 768), pygame.FULLSCREEN)
    else:
        window = pygame.display.set_mode((1360, 768), pygame.RESIZABLE)
    background_img = pygame.image.load(bg_file)
    pygame_update()

def pygame_update():
    global window, background_img
    global attention_duration, attention_value
    window.blit(background_img, (0, 0))
    if int(attention_value) > 100:
        attention_value = 100
        pygame.draw.circle(window, whiteColor, (680, 395), 100, 2)
    elif int(gain*attention_value) < 8:
        # attention_value = 0
        pygame.draw.circle(window, whiteColor, (680, 395), 8, 2)
    else:
        pygame.draw.circle(window, whiteColor, (680, 395), int(attention_value), 2)
    font = pygame.font.Font("freesansbold.ttf", 30)
    attention_value_img = font.render(str(attention_value), False, whiteColor)
    attention_txt_img = font.render("Attantion", False, whiteColor)
    duration_value_img = font.render(str(attention_duration), False, whiteColor)
    duration_txt_img = font.render("Charging", False, whiteColor)
    window.blit(attention_txt_img, (280, 700))
    window.blit(attention_value_img, (320, 650))
    window.blit(duration_txt_img, (930, 700))
    window.blit(duration_value_img, (970, 650))
    angle_attention = (2*attention_value-130+random.randint(0, 5))*0.01745329252
    draw_gauge_needle(358, 582, angle_attention, 160, 6)
    angle_duration = (2*attention_duration-42)*0.01745329252
    draw_gauge_needle(1005, 582, angle_duration, 160, 6)
    pygame.display.update()

def draw_gauge_needle(center_x, center_y, ang, length, width):
    end_x = center_x + length * sin(ang)
    end_y = center_y - length * cos(ang)
    pygame.draw.line(window, greenColor, (center_x, center_y), (end_x, end_y), width)

def main():
    global iteration, background_img
    global attention_duration, attention_value
    # spectra = []
    quit = False
    iteration = 0
    while quit is False:
        try:
            data = socket.recv(1024)
            parser.feed(data)
        except BluetoothError:
            pass
        if len(recorder.attention) > 0:
            attention_value = int(recorder.attention[-1])
            attention_value = gain * attention_value
            pygame_update()
            # Show raw EEG signal
            if raw_eeg:
                lv = 0
                for i, value in enumerate(recorder.raw[-1360:]):
                    v = value / 8.0
                    pygame.draw.line(window, eegColor, (i+25, 180-lv), (i+25, 180-v))
                    lv = v

            if attention_value > Th_attention:
                attention_duration = attention_duration + 1
            else:
                attention_duration = 0
        else:
            Wait_txt_img = font.render("Wait!!..Not yet receiving data from mindwave.", False, greenColor)
            window.blit(Wait_txt_img,(60,100))
            pass

        # Get pygame event
        for event in pygame.event.get():
            if event.type == QUIT:
                quit = True
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    print('quit program')
                    quit = True
        # Display update
        pygame.display.update()
        fpsClock.tick(10)

if __name__ == '__main__':
    try:
        pygame_init()
        main()
    finally:
        pygame.quit()
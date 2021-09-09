import math

import matplotlib.pyplot as plt
import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    K_p,
    QUIT,
    MOUSEBUTTONDOWN,
    MOUSEMOTION,
)

DOT_RADIUS = 5
LINE_WIDTH = 3
ARC_THICKNESS = 3
SCREEN_WDITH = 1000
SCREEN_HEIGHT = 600

BACKGROUNG_COLOR = (68,68,68)
DOT_COLOR = (32,105,224)
LINE_COLOR = (244,212,124)
ARC_COLOR = (224,212,124)
TEXT_COLOR = (190,190,190)
outputfile_points = open("points.txt","w")
outputfile_distances = open("distances.txt","w")
points = []
distances = []
mode = "1p"
pygame.init()
shapes = []
screen = pygame.display.set_mode([SCREEN_WDITH, SCREEN_HEIGHT])
font = pygame.font.Font('freesansbold.ttf', 32)


class Dot:
    def __init__(self, center, radius):
        self.radius = radius
        self.center = center
        self.name = "dot"
class Line:
    def __init__(self, start, end=False, slope=False):
        self.name = "line"
        self.vertical = False
        if not slope == False:
            self.start = start
            self.slope = slope

        else:
            self.start = start
            self.end = end
            self.length = distance(start, end)
            try:
                self.slope = (start[1]-end[1])/(start[0]-end[0])
            except ZeroDivisionError:
                self.vertical = True
    def updateLength(self):
        self.length = distance(self.start,self.end)
    def intersect(self, line):
        result = []
        if line.vertical:
            result.append(line.end[0])
            result[1] =  self.slope * (result[0] - self.end[0]) + self.end[1];
            return result

        elif self.vertical:
            result.append(self.end[0])
            result.append(line.slope * (result[0] - line.endPoint[0]) + line.endPoint[1])
            return result



        result.append((-line.slope * line.start[0] + line.start[1] - self.start[1] + self.slope * self.start[0]) / (
                self.slope - line.slope))
        result.append(self.slope * (result[0] - self.start[0]) + self.start[1])
        return result
class Arc:
    def __init__(self, start, end, center):
        self.start = start
        self.end = end
        self.name = "arc"
        self.center = center
        self.radius = distance(start, center)
        self.startAngle = math.atan2(center[1]-start[1],start[0]-center[0])#-math.pi/64
        self.endAngle = math.atan2(center[1]-end[1],end[0]-center[0]) #- math.pi/64


        if not shouldTurnLeft((math.degrees(self.startAngle)+360)%360,(math.degrees(self.endAngle) + 360)%360):
            self.startAngle = math.atan2(center[1]-end[1],end[0]-center[0]) #- math.pi/64
            self.endAngle = math.atan2(center[1]-start[1],start[0]-center[0])#-math.pi/64

def distance( p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
def shouldTurnLeft(angle, targetAngle):


    value = False;

    if (targetAngle < 180) :
        value = angle < targetAngle or angle > 180+targetAngle
    else :
        value = angle < targetAngle and angle > targetAngle-180
    return value
def drawShapes():
    for shape in shapes:
        if shape.name == "dot":
            pygame.draw.circle(screen, DOT_COLOR, shape.center, shape.radius)
        elif shape.name == "line":
            pygame.draw.line(screen,LINE_COLOR,shape.start,shape.end,LINE_WIDTH)
        elif shape.name == "arc":
            pygame.draw.arc(screen,ARC_COLOR,[shape.center[0]-shape.radius, shape.center[1]-shape.radius,shape.radius*2, shape.radius*2], shape.startAngle,shape.endAngle, ARC_THICKNESS)
def displayOutput():
    file = open("output.txt")
    X=[]
    Y = []
    for line in file:
        numbers = line.split("!")
        X.append(float(numbers[0]))
        Y.append( float(numbers[1]))
    plt.plot(X,Y)
    plt.show()


displayOutput()
# Set up the drawing window




# Run until the user asks to quit
running = True
while running:
    drawShapes()
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN and mode=="1p":

            shapes.append(Dot(pygame.mouse.get_pos(), DOT_RADIUS))
            points.append(pygame.mouse.get_pos())
            mode = "2p"
        elif event.type == MOUSEBUTTONDOWN and mode == "2p":
            shapes.append(Dot(pygame.mouse.get_pos(), DOT_RADIUS))
            mode = "3p"
            points.append(pygame.mouse.get_pos())
            shapes.append(Line(shapes[-2].center, shapes[-1].center))
        elif event.type == MOUSEBUTTONDOWN and mode == "3p":
            shapes.append(Dot(pygame.mouse.get_pos(), DOT_RADIUS))
            mode = "d"

            shapes.append(Line(shapes[-3].center, shapes[-1].center))
            points.append(pygame.mouse.get_pos())
        elif event.type == MOUSEBUTTONDOWN and mode == "d":
            if shapes[-1].name == "dot":
                shapes.pop(-1)

            line = Line(pygame.mouse.get_pos(), slope=-1/(shapes[-3].slope))
            point = line.intersect(shapes[-3])
            distances.append(distance(point,shapes[-3].end))
            fline = shapes[-3]
            sline = shapes[-1]
            d = distances[-1]
            ratio = (fline.length-d)/fline.length
            start = [ratio*(fline.end[0]-fline.start[0]) + fline.start[0],
                     ratio*(fline.end[1]-fline.start[1]) + fline.start[1]]
            ratio2 = d/sline.length
            end =  [ratio2*(sline.end[0]-sline.start[0]) + sline.start[0],
                     ratio2*(sline.end[1]-sline.start[1]) + sline.start[1]]
            flinep = Line(start,slope=-1/fline.slope)
            slinep = Line(end,slope=-1/sline.slope)

            center = flinep.intersect(slinep)

            shapes.insert(0,Arc(start,end,center))

            shapes[-3].end = start
            shapes[-3].updateLength()
            shapes[-1].start = end
            shapes[-1].updateLength()

            shapes.insert(0, Dot(shapes[0].start, DOT_RADIUS))
            shapes.insert(0, Dot(end, DOT_RADIUS))

            mode = "3p"
        elif event.type == MOUSEMOTION and mode == "d":
            if shapes[-1].name == "dot":
                line = Line(pygame.mouse.get_pos(), slope=-1 / (shapes[-4].slope))
                shapes[-1].center = line.intersect(shapes[-4])
            else:
                line = Line(pygame.mouse.get_pos(), slope=-1 / (shapes[-3].slope))
                shapes.append(Dot(line.intersect(shapes[-1]),DOT_RADIUS))
        if event.type == pygame.KEYDOWN and event.key == K_p:
            result_points = ""
            result_distances = ""
            result_points += "double[][] points = {\n"+f"({points[0][0]/100},{points[0][1]/100}),\n"
            result_distances += "double[] distances = {\n"
            print("running p")
            print(points)

            for i in range(1,len(points)-1):
                result_points += f"({points[i][0]/100},{points[i][1]/100}),\n"
                result_distances += f"{distances[i-1]/100},\n"
            result_points+=f"({points[-1][0]/100},{points[-1][1]/100})\n" + "};"
            result_distances += "};"
            result_points = result_points.replace("(","{")
            result_points = result_points.replace(")","}")

            outputfile_points.write(result_points)
            outputfile_distances.write(result_distances)
            running = False
    # Fill the background with white
    screen.fill(BACKGROUNG_COLOR)

    # Draw a solid blue circle in the center
    #pygame.draw.circle(screen, (0, 0, 255), (250, 250), 75)
    drawShapes()
    font = pygame.font.Font('freesansbold.ttf', 12)
    text = font.render(f'Mode: {mode}', True,TEXT_COLOR,BACKGROUNG_COLOR)

    textRect = text.get_rect()
    textRect.center = (30, 10)
    y = 30
    for shape in shapes:
        text2 = font.render(f"{shape.name}", True, TEXT_COLOR,BACKGROUNG_COLOR)
        textRect2 = text2.get_rect()
        textRect2.center = (30,y)
        y+= 20
        screen.blit(text2,textRect2)
    screen.blit(text,textRect)
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
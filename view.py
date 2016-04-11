"""
Handle drawing stuff to the screen
"""
#Import modules
import pygame
from pygame.locals import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.backends.backend_agg as agg
import pylab
import numpy
import time
#Import our own other files 
from curve import Curve
from Control import Controller 

class View(object):
    """

    """

    def __init__(self, curve=None):
        pygame.init()
        screen = pygame.display.get_surface()
        # self.curve = curve
        self.controller=Controller()


    def draw(self):
        fig = pylab.figure(figsize=[6, 6], # Screen Size in inches
                   dpi=100,        # 100 dots per inch, so the resulting buffer is XxY pixels
                   )
        ax = fig.gca()  # The matplotlib figure will be non-interactive
        #ax.plot(self.curve.ATTRIBUTE)   #!!!
        ax.plot([1, 2, 3, 3], numpy.linspace(1, len([1, 2, 3, 3]), num = len([1, 2, 3, 3])), [1, 4, 3, 2], [1, 2, 3, 4])  #!!!!

         
        canvas = agg.FigureCanvasAgg(fig)
        canvas.draw()   # Non-interactive figures must be manually updated
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()  # The raw data (matrix) from the matplotlib graph can now be u1sed by pygame
         

        window = pygame.display.set_mode((600, 600), DOUBLEBUF) # Includes window size 
        self.screen = pygame.display.get_surface()
         
        size = canvas.get_width_height()
         
        surf = pygame.image.fromstring(raw_data, size, "RGB")
        self.screen.blit(surf, (0,0))
        pygame.display.flip()

    def draw_input(self):
        '''Displays the user's drawing input on the screen'''
        self.controller.handle_events()
        window = pygame.display.set_mode((600, 600), DOUBLEBUF) # Includes window size 
        self.screen = pygame.display.get_surface() 
        self.screen.fill((255,255,255))
        pygame.draw.line(self.screen, (0,0,0), (300,0),(300,600),3)
        pygame.draw.line(self.screen, (0,0,0), (0,300),(600,300),3)

        for i in range(len(self.controller.running_points)):
            if len(self.controller.running_points[i])>1:
                pygame.draw.lines(self.screen, (255,0,0),False,self.controller.running_points[i], 2)
        # for point in self.controller.running_points:

        #     pygame.draw.circle(screen, 'red', point, 2, width=0)

        pygame.display.update() 
        

# tests = View()
# tests.draw()


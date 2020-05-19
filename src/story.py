# For the story visualization in Sam's Ballad

import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from kivy.graphics import Translate

# for y pos relative to window
Y_SCALAR = 5/12

class StoryWidget(BaseWidget):
    def __init__(self):   
        super(StoryWidget, self).__init__()
        self.base_src = '../data/img/test_chapter'
        self.red_img = self.base_src + '/red.png'
        self.green_img = self.base_src + '/green.png'
        self.displayed_src = self.green_img
        self.size = (Window.width/3, Window.height/2)
        self.pos = (Window.width/4, Window.height * Y_SCALAR)

        self.displayed_img = Rectangle(source=self.displayed_src, pos = self.pos, size = self.size)
        
        self.canvas.add(self.displayed_img)

    def continue_story(self):
        self.canvas.clear()
        self.displayed_src = self.green_img
        self.displayed_img = Rectangle(source=self.displayed_src, pos = self.pos, size = self.size)
        self.canvas.add(self.displayed_img)

    def end_story(self):
        self.canvas.clear()
        self.displayed_src = self.red_img
        self.displayed_img = Rectangle(source=self.displayed_src, pos = self.pos, size = self.size)
        self.canvas.add(self.displayed_img)

    def on_layout(self, win_size):
        w, h = win_size
        self.canvas.clear()
        self.size = (w/2, h/2)
        self.pos = (w/4, h * Y_SCALAR)
        self.displayed_img = Rectangle(source=self.displayed_src, pos = self.pos, size = self.size)
        self.canvas.add(self.displayed_img)

    def on_update(self):
        pass

# if __name__ == "__main__":
#     run(StoryWidget)
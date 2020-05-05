# For the story visualization in Sam's Ballad

import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *

class StoryWidget(BaseWidget):
    def __init__(self):   
        super(StoryWidget, self).__init__()
        self.base_src = '../data/img/chapter_one'
        self.red_img = self.base_src + '/red.png'
        self.green_img = self.base_src + '/green.png'
        self.displayed_src = self.green_img
        self.displayed_img = Rectangle(source=self.displayed_src, pos = (0, 0), size = (Window.width/2, Window.height))
        
        self.canvas.add(self.displayed_img)

    def continue_story(self):
        self.canvas.clear()
        self.displayed_src = self.green_img
        self.displayed_img = Rectangle(source=self.displayed_src, pos = (0, 0), size = (Window.width/2, Window.height))
        self.canvas.add(self.displayed_img)

    def end_story(self):
        self.canvas.clear()
        self.displayed_src = self.red_img
        self.displayed_img = Rectangle(source=self.displayed_src, pos = (0, 0), size = (Window.width/2, Window.height))
        self.canvas.add(self.displayed_img)

    def on_layout(self, win_size):
        w, h = win_size
        self.canvas.clear()
        self.displayed_img = Rectangle(source=self.displayed_src, pos = (0, 0), size = (w/2, h))
        self.canvas.add(self.displayed_img)

    def on_update(self):
        pass

# if __name__ == "__main__":
#     run(StoryWidget)
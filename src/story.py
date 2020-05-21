# For the story visualization in Sam's Ballad

import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from kivy.graphics import Translate

import os

def get_num_png(start_path = '.'):
    num = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link or isn't .png
            if not os.path.islink(fp) and f[len(f) - 4:] == '.png':
                num += 1

    return num

# for y pos relative to window
Y_SCALAR = 5/12

class StoryWidget(BaseWidget):
    def __init__(self):   
        super(StoryWidget, self).__init__()
        self.base_src = '../data/img/ch1'
        self.size = (Window.width/2, Window.height/2)
        self.pos = (Window.width/4, Window.height * Y_SCALAR)
        self.status = True # True -> continue, False -> end

        self.cont_imgs = self.load_imgs_paths(cont=True)
        self.end_imgs = self.load_imgs_paths(cont=False)
  
        self.displayed_img = Rectangle(source=self.cont_imgs[0], pos = self.pos, size = self.size)
        
        self.canvas.add(self.displayed_img)


    # expect image titles to be in form of '00.png', '01.png', ...
    # cont - image type, continue or end, True or False
    def load_imgs_paths(self, cont):
        loc = 'continue' if cont else 'end'
        path = self.base_src + '/' + loc
        num_imgs = get_num_png(path)
        paths = []
        for i in range(num_imgs):
            src = path + '/0' + str(i) + '.png'
            paths.append(src)
        return paths

    def continue_story(self):
        self.canvas.clear()
        self.displayed_img = Rectangle(source=self.cont_imgs[0], pos = self.pos, size = self.size)
        self.canvas.add(self.displayed_img)

    def end_story(self):
        self.status = False
        self.canvas.clear()
        self.displayed_img = Rectangle(source=self.end_imgs[0], pos = self.pos, size = self.size)
        self.canvas.add(self.displayed_img)

    def adv_cont_imgs(self):
        try:
            self.cont_imgs = self.cont_imgs[1:]
        except:
            raise Exception("No more images left")
    
    def adv_end_imgs(self):
        try:
            self.end_imgs = self.end_imgs[1:]
        except:
            raise Exception("No more images left")

    def on_layout(self, win_size):
        w, h = win_size
        self.canvas.clear()
        self.size = (w/2, h/2)
        self.pos = (w/4, h * Y_SCALAR)
        if self.status:
            self.displayed_img = Rectangle(source=self.cont_imgs[0], pos = self.pos, size = self.size)
        else:
            self.displayed_img = Rectangle(source=self.end_imgs[0], pos = self.pos, size = self.size)
        self.canvas.add(self.displayed_img)

    def on_update(self):
        pass

# if __name__ == "__main__":
#     run(StoryWidget)
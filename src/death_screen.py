import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *

class DeathScreen(InstructionGroup):
    def __init__(self):
        super(DeathScreen, self).__init__()
        w, h = (Window.width, Window.height)
        self.bg_color = Color(255/255, 61/255, 57/255, .5)
        self.death_text = DeathText()
        self.add(self.death_text)
        self.on_layout((w, h))

    def on_layout(self, win_size):
        self.clear()
        self.add(self.bg_color)
        self.add(Rectangle(pos=(0,0), size=win_size))
        self.add(self.death_text)
        self.death_text.on_layout(win_size)
    
    def on_update(self, now_time):
        self.death_text.on_update(now_time)

class DeathText(InstructionGroup):
    def __init__(self):
        super(DeathText, self).__init__()
        self.text_img = '../data/img/text/you_died_border.png'

        w, h = (Window.width, Window.height)
        self.on_layout((w, h))
    
    def on_layout(self, win_size):
        self.clear()
        w, h = win_size
        self.add(Color(1,1,1, .5))
        self.add(Rectangle(source=self.text_img, pos=(w * (1/32), h/4), size=(h * (3/4) * 1.77, h * (3/4))))

    def on_update(self, now_time):
        print(now_time)
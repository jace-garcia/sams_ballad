import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from kivy.properties import ListProperty

class MenuWidget(BaseWidget):
    def __init__(self):
        super(MenuWidget, self).__init__()
        self.display = MenuDisplay()
        self.canvas.add(self.display)

    def handle_start_click(self):
        pass

    def on_key_down(self, keycode, modifiers):
        pass

    def on_touch_down(self, touch):
        self.display.on_touch_down(touch)

    def on_layout(self, win_size):
        self.display.on_layout(win_size)

    def on_update(self):
        pass

class MenuDisplay(InstructionGroup):
    def __init__(self):
        super(MenuDisplay, self).__init__()
        self.background_src = '../data/img/start_screen/background.png'
        self.title_src = '../data/img/text/sams_ballad.png'
        self.start = None
        self.on_layout((Window.width, Window.height))

        self.load_chapter_select = False
        self.load_start = True

    def on_start_click(self):
        print('start clicked')
        self.load_start = False
        self.load_chapter_select = True

    def on_touch_down(self, touch):
        self.start.on_touch_down(touch)
    
    def on_layout(self, win_size):
        print(win_size)
        self.clear()
        w, h = win_size

        background_img = Rectangle(source=self.background_src, pos=(0,0), size=(w, h))
        self.add(background_img)

        self.start = StartButton(on_click=self.on_start_click)
        self.add(self.start)

        title_pos = (w * (1/4), h * (7/10))
        title_size = (w * (7/10), h / 5)
        title = Rectangle(source=self.title_src, pos=title_pos, size=title_size)
        self.add(title)

    def on_update(self):
        pass

class ChapterDisplay(InstructionGroup):
    def __init__(self, chapter_num):
        super(ChapterDisplay, self).__init__()
        self.ch_img = '../data/img/text/ch.png'
        self.num_img = '../data/img/text/' + str(chapter_num) + '.png'
        self.boundaries = []

    def on_layout(self, win_size):
        self.clear()

        w, h = win_size
        ch_pos = (w * 1/2, h/4)
        ch_size = (w * 1/10, h/6)
        self.add(Rectangle(source=self.ch_img, pos=ch_pos, size=ch_size))
        num_pos = (w * 1/2 + w * 1/16, h/4)
        num_size = (w * 1/15, h/6)
        self.add(Rectangle(source=self.num_img, pos=num_pos, size=num_size))

        self.boundaries = [(ch_pos[0], ch_pos[0] + ch_size[0] + num_size[0]), (ch_pos[1], ch_pos[1] + ch_size[1])]

class StartButton(InstructionGroup):
    def __init__(self, on_click = None):
        super(StartButton, self).__init__()
        self.img_src = '../data/img/text/Start.png'
        self.boundaries = []
        self.on_layout((Window.width, Window.height))
        self.on_click = on_click

    def on_touch_down(self, touch):
        if (self.touch_inbounds(touch.pos)):
            self.on_click()

    def touch_inbounds(self, pos):
        return self.boundaries[0][0] <= pos[0] <= self.boundaries[0][1] and self.boundaries[1][0] <= pos[1] <= self.boundaries[1][1]

    def on_layout(self, win_size):
        self.clear()

        w, h = win_size
        pos = (w * (1/2), h / 4)
        size = (w * (1/5), h / 8)

        self.boundaries = [(pos[0], pos[0] + size[0]), (pos[1], pos[1] + size[1])]
        self.add(Rectangle(source=self.img_src, pos=pos, size=size))


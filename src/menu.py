import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from kivy.properties import ListProperty

def point_inbounds(point, boundaries):
    return boundaries[0][0] <= point[0] <= boundaries[0][1] and boundaries[1][0] <= point[1] <= boundaries[1][1]

class MenuWidget(BaseWidget):
    def __init__(self, load_game_cb):
        super(MenuWidget, self).__init__()
        self.load_game_cb = load_game_cb

        self.display = MenuDisplay(self.load_game_cb)
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
        self.display.on_update()

class MenuDisplay(InstructionGroup):
    def __init__(self, load_game_cb, num_chapters=4):
        super(MenuDisplay, self).__init__()
        w, h = (Window.width, Window.height)
        self.background_src = '../data/img/start_screen/background.png'
        self.title_src = '../data/img/text/sams_ballad.png'
        self.start = None
        self.chapter_select = None
        self.num_ch = num_chapters
        self.load_chapter_select = False
        self.load_start = True
        self.start_clicked = False
        self.chapters = []
        self.load_game_cb = load_game_cb
        self.on_layout((w, h))

        self.ch_size = (w * 1/10, h/8)
        self.num_size = (w * 1/20, h/10)
        self.btwn_size = w * 1/8
        self.init_pos = (w * 1/2, h/3)

    def on_start_click(self):
        self.load_start = False
        self.load_chapter_select = True
        self.start_clicked = True

    def on_ch_click(self, ch_num):
        self.load_game_cb()

    def on_touch_down(self, touch):
        if self.load_start:
            self.start.on_touch_down(touch)
        if self.load_chapter_select:
            for c in self.chapters:
                c.on_touch_down(touch)
    
    def on_layout(self, win_size):
        self.clear()
        w, h = win_size

        background_img = Rectangle(source=self.background_src, pos=(0,0), size=(w, h))
        self.add(background_img)

        title_pos = (w * (1/4), h * (7/10))
        title_size = (w * (7/10), h / 5)
        title = Rectangle(source=self.title_src, pos=title_pos, size=title_size)
        self.add(title)

        if self.load_start:
            self.start = StartButton(on_click=self.on_start_click)
            self.add(self.start)
        if self.load_chapter_select:
            self.load_chapters(win_size)

    def load_chapters(self, win_size):
        w, h = win_size
        self.ch_size = (w * 1/10, h/8)
        self.num_size = (w * 1/20, h/8)
        self.btwn_size = w * 1/8
        self.init_pos = (w * 1/2, h/3)
        current_pos = self.init_pos
        
        icon_width = self.ch_size[0] + self.num_size[0] + self.btwn_size
        icon_height = self.ch_size[1]
        
        y_offset = -h/20
        for i in range(self.num_ch):
            pos = ()
            if i % 2 == 0: # newline
                pos = (current_pos[0], current_pos[1])
                if i != 0:
                    pos = (pos[0], pos[1] + y_offset - icon_height)
                
                current_pos = (current_pos[0], pos[1])
            else: # adjacent
                pos = (current_pos[0] + icon_width, current_pos[1])

            chapter = ChapterDisplay(chapter_num=i+1, pos=pos, ch_size=self.ch_size, num_size=self.num_size, btwn_size=self.btwn_size, on_click=self.on_ch_click, active=True)
            self.chapters.append(chapter)
            self.add(chapter)


    def on_update(self):
        if self.start_clicked:
            self.start_clicked = False
            self.on_layout((Window.width, Window.height))
        

class ChapterDisplay(InstructionGroup):
    def __init__(self, chapter_num, pos, ch_size, num_size, btwn_size, on_click=None, active=True):
        super(ChapterDisplay, self).__init__()
        self.ch_img = '../data/img/text/ch.png'
        self.num_img = '../data/img/text/' + str(chapter_num) + '.png'
        self.boundaries = []
        self.pos = pos
        self.chapter_num = chapter_num
        self.ch_size = ch_size
        self.num_size = num_size
        self.btwn_size = btwn_size
        self.on_click = on_click
        self.on_layout((Window.width, Window.height))

    def on_touch_down(self, touch):
        # TODO: trigger relevant chapter gameplay load
        if point_inbounds(touch.pos, self.boundaries):
            self.on_click(self.chapter_num)

    def on_layout(self, win_size):
        # TODO: different color for inactive/unavailable chapters
        self.clear()

        w, h = win_size
        ch_pos = self.pos
        ch_size = self.ch_size
        self.add(Rectangle(source=self.ch_img, pos=ch_pos, size=ch_size))
        num_pos = (ch_pos[0] + self.btwn_size, ch_pos[1])
        num_size = self.num_size
        self.add(Rectangle(source=self.num_img, pos=num_pos, size=num_size))
        # [(x1, x2), (y1, y2)]
        self.boundaries = [(ch_pos[0], ch_pos[0] + ch_size[0] + num_size[0] + self.btwn_size), (ch_pos[1], ch_pos[1] + ch_size[1])]

class StartButton(InstructionGroup):
    def __init__(self, on_click = None):
        super(StartButton, self).__init__()
        self.img_src = '../data/img/text/Start.png'
        self.boundaries = []
        self.on_layout((Window.width, Window.height))
        self.on_click = on_click

    def on_touch_down(self, touch):
        if point_inbounds(touch.pos, self.boundaries):
            self.on_click()

    def on_layout(self, win_size):
        self.clear()

        w, h = win_size
        pos = (w * (.58), h / 4)
        size = (w * (3/10), h / 8)

        self.boundaries = [(pos[0], pos[0] + size[0]), (pos[1], pos[1] + size[1])]
        self.add(Rectangle(source=self.img_src, pos=pos, size=size))


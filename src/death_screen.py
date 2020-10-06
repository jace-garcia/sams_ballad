import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from menu import point_inbounds

class DeathScreen(InstructionGroup):
    def __init__(self, status, exit_cb, restart_cb):
        super(DeathScreen, self).__init__()
        self.status = status
        self.exit_cb = exit_cb
        self.restart_cb = restart_cb

        w, h = (Window.width, Window.height)
        self.bg_color = Color(255/255, 0, 0, .3)#Color(255/255, 61/255, 57/255, .35)
        self.death_text = DeathText(self.exit_cb, self.restart_cb)
        self.add(self.death_text)
        self.on_layout((w, h))

    def set_status(self, status):
        self.status = status
        self.on_layout((Window.width, Window.height))

    def on_touch_down(self, touch):
        if self.status:
            self.death_text.on_touch_down(touch)

    def on_layout(self, win_size):
        self.clear()
        if self.status:
            self.add(self.bg_color)
            self.add(Rectangle(pos=(0,0), size=win_size))
            self.add(self.death_text)
            self.death_text.on_layout(win_size)
    
    def on_update(self, now_time):
        self.death_text.on_update(now_time)

class DeathText(InstructionGroup):
    def __init__(self, exit_cb, restart_cb):
        super(DeathText, self).__init__()
        self.exit_cb = exit_cb
        self.restart_cb = restart_cb

        self.death_img = '../data/img/text/you_died_pure_border.png'
        self.exit_img = '../data/img/text/exit.png'
        self.restart_img = '../data/img/text/restart.png'

        # [(x1, x2), (y1, y2)]
        self.exit_boundaries = []
        self.restart_boundaries = []
        
        # width / height
        self.restart_sz_ratio = 7.20689655172
        self.exit_sz_ratio = 2.20689655172

        self.exit_boundaries = []
        self.restart_boundaries = []

        w, h = (Window.width, Window.height)
        self.on_layout((w, h))

    def on_touch_down(self, touch):
        pos = touch.pos

        if point_inbounds(pos, self.exit_boundaries):
            print('death exit clicked')
            self.exit_cb()
        if point_inbounds(pos, self.restart_boundaries):
            print('death restart clicked')
            self.restart_cb()
    
    def on_layout(self, win_size):
        self.clear()
        w, h = win_size

        white = Color(1,1,1, .8)
        self.add(white)
        # you died
        self.add(Rectangle(source=self.death_img, pos=(w * (2/8), h/2), size=(h * .4 * 2, h * .4)))

        # exit and restart
        e_r_height = (w/3) / self.restart_sz_ratio
        
        restart_width = w/2
        restart_size = (restart_width, e_r_height)
        restart_pos = (w/14, h/8)

        exit_width = w/6
        exit_size = (exit_width, e_r_height)
        exit_pos = (w - restart_pos[0] - exit_size[0], h/8)

        self.exit_boundaries = [(exit_pos[0], exit_pos[0] + exit_size[0]), (exit_pos[1], exit_pos[1] + exit_size[1])]
        self.restart_boundaries = [(restart_pos[0], restart_pos[0] + restart_size[0]), (restart_pos[1], restart_pos[1] + restart_size[1])]

        self.add(Rectangle(source=self.exit_img, pos=exit_pos, size=exit_size))
        self.add(Rectangle(source=self.restart_img, pos=restart_pos, size=restart_size))


    def on_update(self, now_time):
        pass
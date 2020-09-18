import sys
sys.path.append('..')
from common.gfxutil import *

class PauseMenu(InstructionGroup):
    def __init__(self,status=True):
        super(PauseMenu, self).__init__()
        w, h = Window.width, Window.height
        self.status = status
        self.cont_img = '../data/img/text/continue.png'
        self.exit_img = '../data/img/text/exit.png'
        self.restart_img = '../data/img/text/restart.png'

        self.anchor_pos = (w/4, h * 2/3)
        self.y_offset = - h/8
        self.img_height = h/12

        self.on_layout((w, h))

    def switch_status(self):
        self.status = not self.status
        self.on_layout((Window.width, Window.height))

    def on_layout(self, win_size):
        self.clear()
        w, h = win_size
        self.anchor_pos = (w/4, h * 2/3)
        self.y_offset = -h/8
        self.img_height = h/12

        if (self.status):
            self.add(Color(255, 0, 0))

            cont_pos = (self.anchor_pos[0] + w/12, self.anchor_pos[1])
            cont_size = (w * 1/3, self.img_height)
            self.add(Rectangle(source=self.cont_img, pos=cont_pos, size=cont_size))

            restart_pos = (self.anchor_pos[0], self.anchor_pos[1] + self.y_offset)
            restart_size = (w * 1/2, self.img_height)
            self.add(Rectangle(source=self.restart_img, pos=restart_pos, size=restart_size))

            exit_pos = (self.anchor_pos[0] + w*9/48, restart_pos[1] + self.y_offset)
            exit_size = (w * 1/8, h/12)
            self.add(Rectangle(source=self.exit_img, pos=exit_pos, size=exit_size))

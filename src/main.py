# Main control code for Sam's Ballad, a midi-piano performance
# dependant visual story, as produced by
# Juan Carlos Garcia and Robby Schieffer.

import sys
sys.path.append('..')
from common.core import *
from game import GameWidget
from menu import MenuWidget

class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.menu = MenuWidget(self.load_game_cb)
        self.add_widget(self.menu)

        self.load_game = False
        self.game = None
        # self.game = GameWidget()
        # self.add_widget(self.game)
    
    def on_touch_down(self, touch):
        self.menu.on_touch_down(touch)

    def load_game_cb(self):
        self.remove_widget(self.menu)
        self.menu = None
        self.load_game = True
        self.game = GameWidget()
        self.add_widget(self.game)

    def on_update(self):
        if self.load_game and self.game:
            self.game.on_update()
        else:
            if (self.menu):
                self.menu.on_update()

if __name__ == "__main__":
    run(MainWidget)
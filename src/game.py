import sys
sys.path.append('..')
from common.core import *
from common.gfxutil import *
from performer import PerformerWidget
from story import StoryWidget
from death_screen import DeathScreen, DeathText

class GameWidget(BaseWidget):
    def __init__(self, restart_cb, exit_cb):
        super(GameWidget, self).__init__()
        self.restart_cb = restart_cb
        self.exit_cb = exit_cb
        self.story_widget = StoryWidget()
        self.performer_widget = PerformerWidget(self.end_story_cb, self.continue_story_cb, self.exit_cb, self.restart_cb)

        self.add_widget(self.story_widget)
        self.add_widget(self.performer_widget)

        self.continue_story = True
        self.ended_story = False

    def on_layout(self, win_size):
        self.story_widget.on_layout(win_size)
        self.performer_widget.on_layout(win_size)
    
    def continue_story_cb(self):
        self.continue_story = True

    def end_story_cb(self):
        self.continue_story = False
        self.ended_story = True

    def on_key_down(self, keycode, modifiers):
        pass

    def on_update(self):
        if not self.continue_story:
            self.story_widget.end_story()
        
        if self.continue_story and self.ended_story:
            self.ended_story = False
            self.story_widget.continue_story()

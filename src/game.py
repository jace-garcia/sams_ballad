import sys
sys.path.append('..')
from common.core import *
from performer import PerformerWidget
from story import StoryWidget

class GameWidget(BaseWidget):
    def __init__(self):
        super(GameWidget, self).__init__()
        self.story_widget = StoryWidget()
        self.performer_widget = PerformerWidget(self.end_story_cb, self.continue_story_cb)

        self.add_widget(self.story_widget)
        self.add_widget(self.performer_widget)

        self.continue_story = True
        self.ended_story = False
    
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

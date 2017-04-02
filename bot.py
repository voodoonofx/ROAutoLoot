import roplus

from gui import main_window

class Bot(object):
    def __init__(self):
        roplus.log('AutoLoot Loading')
        self.running = False
        self.mainWindow = main_window.MainWindow(self)
        self.mainWindow.show()
        roplus.registerCallback('ROPlus.OnPulse', self.onPulseCallback)
        roplus.log(' ... Done')

    def onPulseCallback(self, args):
        if self.running:
            self.engine.pulse()
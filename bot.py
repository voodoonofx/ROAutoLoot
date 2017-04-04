import itertools
from datetime import datetime

import roplus
from gui import main_window

import BigWorld

class Bot(object):
    def __init__(self):
        roplus.log('AutoLoot Loading')

        # A few defaults in case onPulse hasn't triggered yet.
        self.player = self.p = BigWorld.player()
        self.entities = {}
        self.items = []

        # Some configuration options
        self.entity_range = 100

        # And some internals
        self.last_loot_attempt_time = datetime.now()
        self.key_func = lambda e: e.__module__

        self.mainWindow = main_window.MainWindow(self)
        self.mainWindow.show()
        roplus.registerCallback('ROPlus.OnPulse', self.onPulseCallback)
        roplus.log(' ... Done')

    def onPulseCallback(self, *args, **kw):
        # roplus.log('self: {0}'.format(self), 'args: {0}'.format(args), 'kw: {0}'.format(kw))
        grouper = itertools.groupby(sorted(self.p.entitiesInRange(self.entity_range), key=self.key_func), key=self.key_func)
        self.entities = dict((k, list(v)) for (k, v) in grouper)
        self.items = self.entities.get('DroppedItem', []) + self.entities.get('TreasureBox', [])
        # roplus.log('self.enabled_auto_loot:', self.enabled_auto_loot)
        for item in self.items:
            if not item:
                continue
            # Loot it, if we can
            item_dist = self.p.position.distTo(item.position)
            if item_dist < 4.0 and self.mainWindow.enabled_auto_loot:
                # Try looting it!
                if (datetime.now() - self.last_loot_attempt_time).total_seconds() > 1:
                    if item.__module__ == 'TreasureBox':
                        roplus.log('Opening Treasure Box: {0}'.format(item.roleName))
                        item.use()
                    elif item.__module__ == 'DroppedItem' and item._checkPickItem(self.p):
                        roplus.log('Looting Nearby Item: {0}'.format(item.roleName))
                        self.p.pickNearByItems(True)
                    self.last_loot_attempt_time = datetime.now()
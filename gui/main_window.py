
import itertools
from datetime import datetime

import BigWorld

import imgui
import roplus
from roplus.helpers import nav
import ROAutoLoot as autoloot


class MainWindow(object):
    def __init__(self, botInstance):
        self.bot = botInstance
        self.window_visable = False
        self.entity_range = 100
        self.enabled_auto_loot = False
        self.last_loot_attempt_time = datetime.now()
        self.key_func = lambda e: e.__module__
        self.player = self.p = BigWorld.player()

        # A few defaults in case onPulse hasn't triggered yet.
        self.entities = {}
        self.items = []

        # Register functions
        roplus.registerCallback('ROPlus.OnDrawGUI', self.onDrawGuiCallback)
        roplus.registerCallback('ROPlus.OnPulse', self.onPulseCallback)

    def show(self):
        self.window_visable = True

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
            if item_dist < 4.0 and self.enabled_auto_loot:
                # Try looting it!
                if (datetime.now() - self.last_loot_attempt_time).total_seconds() > 1:
                    if item.__module__ == 'TreasureBox':
                        roplus.log('Opening Treasure Box: {0}'.format(item.roleName))
                        item.use()
                    elif item.__module__ == 'DroppedItem' and item._checkPickItem(self.p):
                        roplus.log('Looting Nearby Item: {0}'.format(item.roleName))
                        self.p.pickNearByItems(True)
                    self.last_loot_attempt_time = datetime.now()

    def onDrawGuiCallback(self, *args, **kw):
        if self.window_visable:
            try:
                if imgui.begin('AutoLoot {0} - {1}##Entity_mainwindow'.format(autoloot.__version__, autoloot.__author__), (600,350)):
                    # button bar
                    if imgui.checkbox('Enable Auto-Loot', self.enabled_auto_loot):
                        self.enabled_auto_loot = not self.enabled_auto_loot
                    
                    if imgui.collapsingHeader('Available Loot ({0} items)'.format(len(self.items))):
                        imgui.columns(4)
                        for item in self.items:
                            if not item:
                                continue

                            imgui.text(item.roleName)
                            imgui.nextColumn()

                            if item.__module__ == 'DroppedItem':
                                try:
                                    imgui.text('Lootable' if item._checkPickItem(self.p) else 'Not Lootable')
                                except AttributeError:
                                    imgui.text('Not _checkPickItem')
                            else:
                                imgui.text('Openable?')
                            imgui.nextColumn()

                            imgui.text('{0}'.format(self.p.position.distTo(item.position)))
                            imgui.nextColumn()

                            if imgui.button('Go To {0}##NavToEntity'.format(item.__module__)):
                                nav.moveToEntityPathFind(item)
                            imgui.nextColumn()
                            imgui.separator()
                        imgui.columns(1)

                    if imgui.collapsingHeader('Debug All Entities'):
                        for entity_name, entities in sorted(self.entities.iteritems()):
                            for entity in entities:
                                imgui.columns(5)
                                imgui.separator()
                                imgui.text('{0}'.format(entity_name))
                                imgui.nextColumn()
                                imgui.text('{0}'.format(entity.id))
                                imgui.nextColumn()
                                if entity_name == 'DroppedItem' and hasattr(entity, '_checkPickItem') and entity._checkPickItem(self.p):
                                    imgui.text('{0}'.format('Lootable'))
                                elif not entity_name == 'DroppedItem':
                                    imgui.text('No Data Available')
                                else:
                                    imgui.text('Not your Loot!')
                                imgui.nextColumn()
                                if entity and hasattr(entity, 'position') and self.p and hasattr(self.p, 'position'):
                                    imgui.text('{0}'.format(self.p.position.distTo(entity.position)))
                                else:
                                    imgui.text('No Position Information')
                                imgui.nextColumn()
                                if imgui.button('NavToEntity##NavToEntity'):
                                    nav.moveToEntityPathFind(entity)
                                imgui.nextColumn()
                        imgui.columns(1)
                imgui.end()
            except Exception:
                import traceback
                for line in traceback.format_exc().splitlines():
                    roplus.log(line)
                self.window_visable = False

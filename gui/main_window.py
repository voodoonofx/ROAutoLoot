
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
        self.enabled_auto_loot = False


        # Register functions
        roplus.registerCallback('ROPlus.OnDrawGUI', self.onDrawGuiCallback)

    def show(self):
        self.window_visable = True

    def onDrawGuiCallback(self, *args, **kw):
        if self.window_visable:
            try:
                if imgui.begin('AutoLoot {0} - {1}##Entity_mainwindow'.format(autoloot.__version__, autoloot.__author__), (600,350)):
                    # button bar
                    if imgui.checkbox('Enable Auto-Loot', self.enabled_auto_loot):
                        self.enabled_auto_loot = not self.enabled_auto_loot
                    
                    if imgui.collapsingHeader('Available Loot ({0} items)'.format(len(self.bot.items))):
                        imgui.columns(4)
                        for item in self.bot.items:
                            if not item:
                                continue

                            imgui.text(item.roleName)
                            imgui.nextColumn()

                            if item.__module__ == 'DroppedItem':
                                try:
                                    imgui.text('Lootable' if item._checkPickItem(self.bot.p) else 'Not Lootable')
                                except AttributeError:
                                    imgui.text('Not _checkPickItem')
                            else:
                                imgui.text('Openable?')
                            imgui.nextColumn()

                            imgui.text('{0}'.format(self.bot.p.position.distTo(item.position)))
                            imgui.nextColumn()

                            if imgui.button('Go To {0}##NavToEntity'.format(item.__module__)):
                                nav.moveToEntityPathFind(item)
                            imgui.nextColumn()
                            imgui.separator()
                        imgui.columns(1)

                    if imgui.collapsingHeader('Debug All Entities'):
                        for entity_name, entities in sorted(self.bot.entities.iteritems()):
                            for entity in entities:
                                imgui.columns(5)
                                imgui.separator()
                                imgui.text('{0}'.format(entity_name))
                                imgui.nextColumn()
                                imgui.text('{0}'.format(entity.id))
                                imgui.nextColumn()
                                if entity_name == 'DroppedItem' and hasattr(entity, '_checkPickItem') and entity._checkPickItem(self.bot.p):
                                    imgui.text('{0}'.format('Lootable'))
                                elif not entity_name == 'DroppedItem':
                                    imgui.text('No Data Available')
                                else:
                                    imgui.text('Not your Loot!')
                                imgui.nextColumn()
                                if entity and hasattr(entity, 'position') and self.bot.p and hasattr(self.bot.p, 'position'):
                                    imgui.text('{0}'.format(self.bot.p.position.distTo(entity.position)))
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

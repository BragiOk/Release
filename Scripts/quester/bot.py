import quests
import roplus
import settings
from gui import main_window
from logics.quest_completor import GenericQuestCompletor
from roplus import fsm
from states.complete_quest import CompleteQuest
from states.idle import Idle
from states.pickup_nearby_quest import PickupNearbyQuest
from states.scenario_playing import ScenarioPlaying

class Bot:

    def __init__(self):
        self.loadSettings()
        self.questCompletors = {}
        self.currentQuestCompletor = None
        self.currentCombat = None
        self.combatState = None
        self.engine = fsm.Engine()
        self.running = False
        self.mainWindow = main_window.MainWindow(self)
        self.mainWindow.show()
        roplus.registerCallback("ROPlus.OnPulse", self.onPulseCallback)

    def saveSettings(self):
        settings.saveSettings(self.settings, "quester")

    def loadSettings(self):
        self.settings = settings.loadSettings("quester")

    def getQuestCompletor(self, questId):
        if questId in self.questCompletors:
            return self.questCompletors[questId]

        if questId in quests.QUEST_COMPLETORS:
            completor = quests.QUEST_COMPLETORS[questId](self, questId)
        else:
            completor = GenericQuestCompletor(self, questId)

        self.questCompletors[questId] = completor
        roplus.log("Created quest completor for [" + str(questId) + "] : " + str(completor))
        return completor
           
    def start(self, combatInst):
        if self.running:
            roplus.log("Bot is already running !")
            return

        if not combatInst:
            roplus.log("Error : No combat script !")
            return
            
        quests.reloadCustomQuestCompletors()
        self.currentQuestCompletor = None
        self.questCompletors = {}
        self.currentCombat = combatInst
        self.currentCombat.handleMove = True

        self.engine = fsm.Engine()
        self.engine.states.append(ScenarioPlaying(self))
        self.engine.states.append(CompleteQuest(self))
        self.engine.states.append(PickupNearbyQuest(self))
        self.engine.states.append(Idle(self))

        self.running = True
        roplus.log("Bot started !")

    def stop(self):
        if not self.running:
            roplus.log("Bot is not running !")
            return
        self.running = False
        roplus.log("Bot stopped !")

    def onPulseCallback(self, args):
        if self.running:
            self.engine.pulse()
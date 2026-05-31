from maya import cmds
from ngSkinTools2.api import PaintTool
from ngSkinTools2.ui.action import Action


class FloodAction(Action):
    name = "Flood"
    tooltip = "Apply current brush to whole selection"

    def run(self):
        PaintTool().flood(self.session.state.currentLayer.layer, self.session.state.currentInfluence.target)

    def enabled(self):
        return (
            PaintTool.is_painting()
            and self.session.state.selectedSkinCluster is not None
            and self.session.state.currentLayer.layer is not None
            and self.session.state.currentInfluence.target is not None
        )

    def update_on_signals(self):
        return [
            self.session.events.toolChanged,
            self.session.events.currentLayerChanged,
            self.session.events.currentInfluenceChanged,
            self.session.events.targetChanged,
        ]


class PaintAction(Action):
    name = "Paint"
    tooltip = "Toggle paint tool"
    checkable = True

    def run(self):
        if self.checked():
            cmds.setToolTo("moveSuperContext")
        else:
            PaintTool.start()

    def update_on_signals(self):
        return [self.session.events.toolChanged]

    def checked(self):
        return PaintTool.is_painting()

"""
Toggle Workspace — by MahlerWorks
----------------------------------
One click switches between the Design and Manufacture workspaces.
This add-in appears in Utilities > Add-Ins as "Toggle Workspace".
If you are in any other workspace it takes you to Design.

Keyboard shortcut: Fusion does not allow add-ins to register hotkeys
automatically. To set one, right-click the Toggle Workspace button in
the ribbon → Create Keyboard Shortcut, then assign any combo you want
(e.g. Ctrl+Shift+Q).
"""

import adsk.core
import traceback
import os

_CMD_ID    = "MW_ToggleWorkspace_Standalone"
_DESIGN_WS = "FusionSolidEnvironment"
_CAM_WS    = "CAMEnvironment"
_PANEL_ID  = "MW_ToggleWorkspace_Panel"
_TAB_ID    = "MW_ToggleWorkspace_Tab"

_WORKSPACES = [
    "FusionSolidEnvironment",
    "CAMEnvironment",
]

_ICON_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

_handlers = []
_controls = []
_cmd_def  = None


def run(context):
    global _cmd_def
    try:
        ui = adsk.core.Application.get().userInterface

        existing = ui.commandDefinitions.itemById(_CMD_ID)
        if existing:
            existing.deleteMe()

        _cmd_def = ui.commandDefinitions.addButtonDefinition(
            _CMD_ID,
            "Toggle Workspace",
            "Switch between Design and Manufacture workspaces.\n\n"
            "Tip: right-click this button → Create Keyboard Shortcut to assign a hotkey.",
            _ICON_DIR,
        )

        handler = _CreatedHandler()
        _cmd_def.commandCreated.add(handler)
        _handlers.append(handler)

        _add_to_utilities(ui)

    except Exception:
        adsk.core.Application.get().userInterface.messageBox(
            "ToggleWorkspace failed to start:\n" + traceback.format_exc()
        )


def stop(context):
    try:
        for ctrl in _controls:
            try:
                if not ctrl.isDeleted:
                    ctrl.deleteMe()
            except Exception:
                pass
        _controls.clear()

        ui = adsk.core.Application.get().userInterface

        for ws_id in _WORKSPACES:
            try:
                ws = ui.workspaces.itemById(ws_id)
                if not ws:
                    continue
                panel = ws.toolbarPanels.itemById(_PANEL_ID + "_" + ws_id)
                if panel:
                    panel.deleteMe()
                tab = ws.toolbarTabs.itemById(_TAB_ID + "_" + ws_id)
                if tab:
                    tab.deleteMe()
            except Exception:
                pass

        global _cmd_def
        if _cmd_def:
            try:
                if not _cmd_def.isDeleted:
                    _cmd_def.deleteMe()
            except Exception:
                pass
            _cmd_def = None

        _handlers.clear()

    except Exception:
        pass


def _add_to_utilities(ui):
    """Place the button in the built-in Add-Ins panel in every workspace."""
    for ws_id in _WORKSPACES:
        try:
            ws = ui.workspaces.itemById(ws_id)
            if not ws:
                continue

            # Search all tabs for the built-in Add-Ins panel
            panel = None
            for tab in ws.toolbarTabs:
                for panel_id in ("AddinsPanel", "AddInsPanel", "AddInPanel"):
                    p = tab.toolbarPanels.itemById(panel_id)
                    if p:
                        panel = p
                        break
                if panel:
                    break

            if not panel:
                continue

            if panel.controls.itemById(_CMD_ID):
                continue

            ctrl = panel.controls.addCommand(_cmd_def)
            ctrl.isPromoted = True
            ctrl.isPromotedByDefault = True
            _controls.append(ctrl)

        except Exception:
            pass


class _CreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable      = False
            cmd.isOKButtonVisible = False
            exe = _ExecuteHandler()
            cmd.execute.add(exe)
            _handlers.append(exe)
        except Exception:
            adsk.core.Application.get().userInterface.messageBox(traceback.format_exc())


class _ExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self): super().__init__()
    def notify(self, args):
        try:
            ui      = adsk.core.Application.get().userInterface
            current = ui.activeWorkspace
            if current and current.id == _DESIGN_WS:
                target_id = _CAM_WS
            else:
                target_id = _DESIGN_WS
            target = ui.workspaces.itemById(target_id)
            if target:
                target.activate()
        except Exception:
            adsk.core.Application.get().userInterface.messageBox(
                "Toggle Workspace error:\n" + traceback.format_exc()
            )

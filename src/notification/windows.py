import subprocess

from typing import Literal

from pathlib import Path
from .sender import Sender


# https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.tooltipicon
BalloonTip = Literal["Error", "Info", "None", "Warning"]
ScriptBlockPS1 = str
Command = str
Milliseconds = int


class WindowsNotification(Sender):
    def __init__(self):
        # TODO: make this my own icon
        self.icon = Path(r"C:\Windows\SysWOW64\OneDrive.ico")

    def notification_cmd(self,
                         title: str,
                         text: str,
                         time: Milliseconds = 20000) -> Command:
        def new_icon(path: Path) -> ScriptBlockPS1:
            assert path.exists()
            assert path.is_file()

            return f"[System.Drawing.Icon]::new('{str(path)}')"

        def new_balloon_tip_icon(value: BalloonTip) -> ScriptBlockPS1:
            return f"[System.Windows.Forms.ToolTipIcon]::{value}"

        def script_block(*cmds: Command) -> ScriptBlockPS1:
            return "{{{}}}".format(";".join(cmds))

        OBJ_ID = "notifier"
        return "powershell.exe \"& {}\"".format(script_block(
            # import the .NET class
            "Add-Type -AssemblyName System.Windows.Forms",
            # create the notification object
            f"$global:{OBJ_ID} = New-Object System.Windows.Forms.NotifyIcon",

            # set the icons
            f"${OBJ_ID}.Icon = {new_icon(self.icon)}",
            f"${OBJ_ID}.BalloonTipIcon = {new_balloon_tip_icon("None")}",
            # set the titles
            f"${OBJ_ID}.BalloonTipTitle = '{title}'",
            f"${OBJ_ID}.BalloonTipText = '{text}'",
            # enable notification display
            f"${OBJ_ID}.Visible = $true",

            # set time in milliseconds and display the notification
            f"${OBJ_ID}.ShowBalloonTip({time})",
        ))

    def send(self, title: str, text: str) -> None:
        subprocess.call(self.notification_cmd(title, text), shell=True)

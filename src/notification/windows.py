import subprocess

from typing import Literal

from pathlib import Path
from .sender import Sender


# https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.tooltipicon
BalloonTip = Literal["Error", "Info", "None", "Warning"]
ScriptBlockPS1 = str
Command = str
Milliseconds = int

ICO_PATH = Path(r"C:\Windows\SysWOW64\OneDrive.ico")


class WindowsNotification(Sender):
    def send(self, title: str, text: str) -> None:
        subprocess.call(notification_cmd(title, text, ICO_PATH),
                        shell=True)


def notification_cmd(
        title: str,
        text: str,
        icon: Path,
        time: Milliseconds = 20000,
        obj_id: str = "notifier") -> Command:
    def new_icon(path: Path) -> ScriptBlockPS1:
        assert path.exists()
        assert path.is_file()

        return f"[System.Drawing.Icon]::new('{str(path)}')"

    def new_balloon_tip_icon(value: BalloonTip) -> ScriptBlockPS1:
        return f"[System.Windows.Forms.ToolTipIcon]::{value}"

    def set_visible(b: bool) -> ScriptBlockPS1:
        return "$" + str(b).lower()

    def script_block(*cmds: Command) -> ScriptBlockPS1:
        return "{{{}}}".format(";".join(cmds))

    # TODO: feed commands to powershell using a pipe
    return "powershell.exe \"& {}\"".format(script_block(
        # import the .NET class
        "Add-Type -AssemblyName System.Windows.Forms",
        # create the notification object
        f"$global:{obj_id} = New-Object System.Windows.Forms.NotifyIcon",

        # set the icons
        f"${obj_id}.Icon = {new_icon(icon)}",
        f"${obj_id}.BalloonTipIcon = {new_balloon_tip_icon("None")}",
        # set the titles
        f"${obj_id}.BalloonTipTitle = '{title}'",
        f"${obj_id}.BalloonTipText = '{text}'",
        # enable notification display
        f"${obj_id}.Visible = {set_visible(True)}",

        # set time in milliseconds and display the notification
        f"${obj_id}.ShowBalloonTip({time})",
    ))

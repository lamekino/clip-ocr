import subprocess

from typing import Literal

from pathlib import Path
from .sender import Sender


# https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.tooltipicon
ToolTipIcon = Literal["Error", "Info", "None", "Warning"]
ScriptBlockPS1 = str
Command = str
Milliseconds = int

# TODO: set this to my own
ICO_PATH = Path(r"C:\Windows\SysWOW64\OneDrive.ico")
PS_RESTRICED_CHARS = set('$`"\'&()[]{}')


class WindowsNotification(Sender):
    def send(self, title: str, text: str) -> None:
        subprocess.call(notification_cmd(title, text, ICO_PATH),
                        shell=True)


def notification_cmd(
        title: str,
        text: str,
        icon: Path,
        time: Milliseconds = 20000,
        __id: str = "notifier") -> Command:
    def new_icon(path: Path) -> ScriptBlockPS1:
        assert path.exists()
        assert path.is_file()

        return f"[System.Drawing.Icon]::new('{str(path)}')"

    def new_tool_tip_icon(value: ToolTipIcon) -> ScriptBlockPS1:
        return f"[System.Windows.Forms.ToolTipIcon]::{value}"

    def set_visible(b: bool) -> ScriptBlockPS1:
        return "$" + str(b).lower()

    def set_string(s: str) -> ScriptBlockPS1:
        return "".join(ch for ch in s if ch not in PS_RESTRICED_CHARS)

    def script_block(*cmds: Command) -> ScriptBlockPS1:
        return "{{{}}}".format(";".join(cmds))

    def C(f, x):
        f(x)
        return x

    # TODO: feed commands to powershell using a pipe
    # BUG: we need to filter out restricted characters such as "'$`@ there
    # should be a list of these
    # write filter(lambda x: x in set(...), xs) O(m lg n) m = |xs|, n = |set|
    # but there might be a more 'pythonic' way
    return C(print, "powershell.exe \"& {}\"".format(script_block(
        # import the .NET class
        "Add-Type -AssemblyName System.Windows.Forms",
        # create the notification object
        f"$global:{__id} = New-Object System.Windows.Forms.NotifyIcon",

        # set the icons
        f"${__id}.Icon = {new_icon(icon)}",
        f"${__id}.BalloonTipIcon = {new_tool_tip_icon("None")}",
        # set the titles
        f"${__id}.BalloonTipTitle = '{set_string(title)}'",
        f"${__id}.BalloonTipText = '{set_string(text)}'",
        # enable notification display
        f"${__id}.Visible = {set_visible(True)}",

        # set time in milliseconds and display the notification
        f"${__id}.ShowBalloonTip({time})",
    )))

from typer import Typer
from color_scheme.cli.commands.install import install
from color_scheme.cli.commands.uninstall import uninstall

app = Typer()
app.command(help="Install color scheme tool")(install)
app.command(help="Uninstall color scheme tool")(uninstall)




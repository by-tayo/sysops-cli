import typer

from sysops_cli.devops.commands import app as devops_app
from sysops_cli.network.commands import app as network_app
from sysops_cli.sysadmin.commands import app as sysadmin_app

app = typer.Typer(help="Sysadmin / network engineering / devops CLI toolkit.")
app.add_typer(sysadmin_app, name="sysadmin", help="System administration commands.")
app.add_typer(network_app, name="network", help="Network engineering commands.")
app.add_typer(devops_app, name="devops", help="DevOps commands.")


if __name__ == "__main__":
    app()

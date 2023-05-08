import click


@click.command(short_help='Show the available Python distributions')
@click.pass_obj
def show(app):
    """Show the available Python distributions."""

import click


@click.group()
@click.pass_context
def main(ctx):
    pass



@main.command
def init():
    pass

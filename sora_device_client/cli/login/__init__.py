import click
import uuid


@click.command()
@click.pass_obj
@click.option("-i", "--device-id", help="Device Id")
def login(config, device_id):
    if device_id:
        device_uuid = uuid.UUID(device_id)

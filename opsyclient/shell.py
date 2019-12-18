from __future__ import absolute_import, print_function

import os
from pprint import pprint
from functools import partial, wraps

import click
from opsyclient.client import OpsyClient


click_option = partial(  # pylint: disable=invalid-name
    click.option, show_default=True)


def common_params(func):
    @click_option('--json', type=click.BOOL, default=False, is_flag=True,
                  help='Output JSON')
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@click.group(help='The Opsy client cli.')
@click_option('--config', type=click.Path(), envvar='OPSY_CONFIG',
              default='{homedir}/.config/opsy.ini'.format(
                  homedir=os.path.expanduser("~")),
              help='Config file for opsy.')
@click_option('--url', '-U', envvar='OPSY_URL', help='Opsy base URL.')
@click_option('--username', '-u', envvar='OPSY_USERNAME', help='Username.')
@click_option('--password', '-p', envvar='OPSY_PASSWORD', prompt=True,
              hide_input=True, help='Password.')
@click.pass_context
def cli(ctx, config, url, username, password):
    ctx.obj = OpsyClient(url, user_name=username, password=password)


@cli.group('zones')
def zones_cli():
    """Commands related to zones."""


@zones_cli.command('show')
@click.argument('zone_name_or_id')
@common_params
@click.pass_obj
def zones_show(client, json, zone_name_or_id):
    """Show a zone."""
    pprint(client.zones.show_zone(id_or_name=zone_name_or_id).response().result)


@zones_cli.command('list')
@common_params
@click.pass_obj
def zones_list(client, json):
    """List all zones."""
    pprint(client.zones.list_zones().response().result)


def main():
    cli()  # pylint: disable=unexpected-keyword-arg,no-value-for-parameter

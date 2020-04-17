from __future__ import absolute_import, print_function

import os
import json
import ipaddress
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


def error_handler(func_verb, target_object, err_code, err_reason):
    """Convenience function for printing nicely formatted errors."""
    click.echo("Unable to %s '%s': HTTP %s - %s" % (func_verb, target_object,
               err_code, err_reason))


def validate_json(ctx, test_json):
    """Callback to validate parameter is a correctly formatted python dict."""
    try:
        return json.loads(test_json)
    except json.decoder.JSONDecodeError:
        raise click.BadParameter("Unable to parse dictionary.")


def validate_ip(ctx, test_ip):
    """Callback to validate parameter is a valid IP address."""
    try:
        return str(ipaddress.ip_address(test_ip))
    except ValueError:
        raise click.BadParameter("Unable to parse IP address.")


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

################################################################################
## Zone Group # #
################################################################################
@cli.group('zone')
def zones_cli():
    """Commands related to zones."""


@zones_cli.command('show')
@click.argument('zone_name_or_id')
@common_params
@click.pass_obj
def zones_show(client, json, zone_name_or_id):
    """Show a zone."""
    try:
        pprint(client.zones.show_zone(id_or_name=zone_name_or_id).response().result)
    except HTTPError as err:
        error_handler('show zone', zone_name_or_id, err.code, err.reason)


@zones_cli.command('list')
@click.option('--id', '-i', help="Zone ID to filter on.")
@click.option('--name', '-n', help="Zone name to filter on.")
@click.option('--description', '-d', help="Zone description to filter on.")
@common_params
@click.pass_obj
def zones_list(client, json, **kwargs):
    """List all zones, filterable."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    pprint(client.zones.list_zones(**set_args).response().result)


@zones_cli.command('add')
@click.argument('zone_name')
@click.option('--description', help="The zone description.")
@click.option('--vars', help="A dictionary of zone vars.", callback=validate_json)
@click.pass_obj
def zones_add(client, **kwargs):
    """Create a new zone."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.zones.create_zone(**set_args).reponse().result)
    except HTTPError as err:
        error_handler('add zone', zone_name, err.code, err.reason)


@zones_cli.command('delete')
@click.argument('zone_name_or_id')
@click.pass_obj
def zones_delete(client, zone_name_or_id):
    """Delete a zone."""
    try:
        pprint(client.zones.delete_zone(zone_name_or_id).response().result)
    except HTTPError as err:
        error_handler('delete zone', zone_name_or_id, err.code, err.reason)


@zones_cli.command('update')
@click.argument('zone_name_or_id')
@click.option('--name', '-n', help="Zone name.")
@click.option('--description', '-d', help="Zone description.")
@click.option('--vars', '-v', help="A dictionary of zone vars.",
              callback=validate_json)
@click.pass_obj
def zones_update(client, zone_name_or_id, **kwargs):
    """Update a zone."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.zones.update_zone(zone_name_or_id, **set_args).response().result)
    except HTTPError as err:
        error_handler('update zone', zone_name_or_id, err.code, err.reason)


################################################################################
## Host Group ##
################################################################################
@cli.group('host')
def host_cli():
    """Commands related to hosts."""


@host_cli.command('show')
@click.argument('host_name_or_id')
@click.pass_obj
def host_show(client, host_name_or_id):
    """Show a host."""
    try:
        pprint(client.hosts.show_host(host_name_or_id).response().result)
    except HTTPError as err:
        error_handler('show host', host_name_or_id, err.code, err.reason)


@host_cli.command('list')
@click.option('--id', help="Host ID to filter on.")
@click.option('--zone-id', help="Zone ID to filter on.")
@click.option('--zone-name', help="Zone name to filter on.")
@click.option('--group-id', help="Group ID to filter on.")
@click.option('--group-name', help="Group name to filter on.")
@click.option('--name', help="Host name to filter on.")
@click.option('--device-id', help="Device ID to filter on.")
@click.option('--bmc-ip', help="BMC IP address to filter on.")
@click.pass_obj
def host_list(client, **kwargs):
    """List all hosts, filterable."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    pprint(client.hosts.list_hosts(**set_args).response().result)


@host_cli.command('add')
@click.argument('host_name')
@click.argument('zone_id')
@click.option('--device-id', '-d', help="External device identifier.")
@click.option('--bmc-ip', '-b', help="IP of the BMC (aka DRAC/iLo/etc).", callback=validate_ip)
@click.option('--vars', '-v', help="A dictionary of host vars.",
              callback=validate_json)
@click.pass_obj
def host_add(client, **kwargs):
    """Create a new host."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.hosts.create_host(**set_args).response().result)
    except HTTPError as err:
        error_handler('add host', name, err.code, err.reason)


@host_cli.command('delete')
@click.argument('host_name_or_id')
@click.pass_obj
def host_delete(client, host_name_or_id):
    """Delete a host."""
    try:
        pprint(client.hosts.delete_host(host_name_or_id).response().result)
    except HTTPError as err:
        error_handler('delete host', host_name_or_id, err.code, err.reason)


@host_cli.command('update')
@click.argument('host_name_or_id')
@click.option('--zone-id', '-z', help="The ID of the zone containing the host.")
@click.option('--name', '-n', help="The name of the host.")
@click.option('--device-id', '-d', help="External device identifier.")
@click.option('--bmc-ip', '-b', help="IP of the BMC (aka DRAC/iLo/etc).", callback=validate_ip)
@click.option('--vars', '-v', help="A dictionary of host vars.",
              callback=validate_json)
@click.pass_obj
def host_update(client, host_name_or_id, **kwargs):
    """Update a host."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.hosts.update_host(host_name_or_id, **set_args).response().result)
    except HTTPError as err:
        error_handler('update host', host_name_or_id, err.code, err.reason)


################################################################################
## HostGroupMappings Group ##
################################################################################
@host_cli.group('groupmapping')
def group_mapping_cli():
    """Commands related to host-group mappings."""


@group_mapping_cli.command('show')
@click.argument('host_name_or_id')
@click.argument('group_name_or_id')
@click.pass_obj
def host_group_mapping_show(client, host_name_or_id, group_name_or_id):
    """Show a host-group mapping."""
    try:
        pprint(client.hosts.show_group_mapping(host_name_or_id, group_name_or_id).response().result)
    except HTTPError as err:
        error_handler("show group '%s' mapping for host" % group_name_or_id,
                      host_name_or_id, err.code, err.reason)


@group_mapping_cli.command('list')
@click.argument('host_name_or_id')
@click.option('--id', '-i', help="HostGroupMapping ID to filter on.")
@click.option('--group-id', '-g', help="Group ID to filter on.")
@click.option('--name', '-n', help="Group name to filter on.")
@click.option('--priority', '-p', type=int, help="Priority to filter on.")
@click.pass_obj
def host_group_mapping_list(client, host_name_or_id, **kwargs):
    """List all host-group mappings, filterable."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.hosts.list_group_mappings(host_name_or_id, **set_args).response().result)
    except HTTPError as err:
        error_handler('list group mappings for host', host_name_or_id, err.code, err.reason)


@group_mapping_cli.command('add')
@click.argument('host_name_or_id')
@click.argument('group_id')
@click.option('--priority', '-p', type=int, help="Set group mapping priority.")
def host_group_mapping_create(client, host_name_or_id, **kwargs):
    """Create a mapping from a host to a group."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.hosts.create_group_mapping(host_name_or_id, **set_args).response().result)
    except HTTPError as err:
        error_handler("create group '%s' mapping for host" % kwargs['group_id'],
                      host_name_or_id, err.code, err.reason)


@group_mapping_cli.command('delete')
@click.argument('host_name_or_id')
@click.argument('group_name_or_id')
@click.pass_obj
def host_group_mapping_delete(client, host_name_or_id, group_name_or_id):
    """Delete a host-group mapping."""
    try:
        pprint(client.hosts.delete_group_mapping(host_name_or_id, group_name_or_id).response().result)
    except HTTPError as err:
        error_handler("delete group '%s' mapping for host" % group_name_or_id,
                       host_name_or_id, err.code, err.reason)


@group_mapping_cli.command('update')
@click.argument('host_name_or_id')
@click.argument('group_name_or_id')
@click.option('--priority', '-p', type=int,
              help="The priority of the hostgroupmapping.")
@click.pass_obj
def host_group_mapping_update(client, host_name_or_id, group_name_or_id, **kwargs):
    """Update a host-group mapping."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.hosts.update_group_mapping(host_name_or_id, group_name_or_id, **set_args).response().result)
    except HTTPError as err:
        error_handler("update group '%s' mapping for host" % group_name_or_id,
                      host_name_or_id, err.code, err.reason)


################################################################################
## Group Group ##
################################################################################
@cli.group('group')
def group_cli():
    """Commands related to groups."""


@group_cli.command('list')
@click.option('--id', '-i', help="Group ID to filter on.")
@click.option('--name', '-n', help="Group name to filter on.")
@click.option('--zone-id', help="Zone ID to filter on.")
@click.option('--zone-name', help="Zone name to filter on.")
@click.option('--parent-id', help="Parent group ID to filter on.")
@click.option('--parent-name', help="Parent group name to filter on.")
@click.option('--host-id', help="Host ID to filter on.")
@click.option('--host-name', help="Host name to filter on.")
@click.option('--default-priority', '-p', type=int, help="The default priority to filter on.")
@click.pass_obj
def group_list(client, **kwargs):
    """List all groups, filterable."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    pprint(client.groups.list_groups(**set_args).response().result)


@group_cli.command('show')
@click.argument('group_id')
@click.pass_obj
def group_show(client, group_id):
    """Show a group."""
    try:
        pprint(client.groups.show_group(group_id).response().result)
    except HTTPError as err:
        error_handler('show group', group_id, err.code, err.reason)


@group_cli.command('add')
@click.argument('name')
@click.option('--zone-id', help="The ID of the zone for the group.")
@click.option('--parent-id', help="The ID of the parent group.")
@click.option('--default-priority', '-p', type=int, help="The default priority of the group.")
@click.option('--vars', help="A dictionary of group vars.", callback=validate_json)
@click.pass_obj
def group_create(client, **kwargs):
    """Create a new group."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.groups.create_group(**set_args).response().result)
    except HTTPError as err:
        error_handler('create group', kwargs['name'], err.code, err.reason)


@group_cli.command('update')
@click.argument('group_id')
@click.option('--name', help="The group name.")
@click.option('--zone-id', help="The ID of the zone for the group.")
@click.option('--parent-id', help="The ID of the parent group.")
@click.option('--default-priority', '-p', type=int, help="The default priority of the group.")
@click.option('--vars', help="A dictionary of group vars.", callback=validate_json)
@click.pass_obj
def group_update(client, group_id, **kwargs):
    """Update a group."""
    set_args = {k: v for k, v in kwargs.items() if v is not None}
    try:
        pprint(client.groups.update_group(group_id, **set_args).response().result)
    except HTTPError as err:
        error_handler('update group', group_id, err.code, err.reason)


@group_cli.command('delete')
@click.argument('group_id')
@click.pass_obj
def group_delete(client, group_id):
    """Delete a group."""
    try:
        pprint(client.groups.delete_group(group_id).response().result)
    except HTTPError as err:
        error_handler('delete group', group_id, err.code, err.reason)


def main():
    cli()  # pylint: disable=unexpected-keyword-arg,no-value-for-parameter

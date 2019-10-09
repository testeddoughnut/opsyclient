import pbr.version
from opsyclient.client import OpsyClient

__version__ = pbr.version.VersionInfo('opsyclient').version_string()

__all__ = ['OpsyClient']

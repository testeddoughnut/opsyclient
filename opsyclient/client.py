from __future__ import absolute_import, print_function

from six.moves.urllib.parse import urljoin, urlsplit
from bravado.client import SwaggerClient
from bravado.config import bravado_config_from_config_dict
from bravado.requests_client import RequestsClient
from bravado.swagger_model import Loader
from bravado_core.spec import Spec
from opsyclient.utils import email_format


class OpsyClient(SwaggerClient):

    def __init__(self, url, user_name=None, password=None, force_renew=False,
                 use_models=True):
        self.url = url
        self.authenticated = False
        self.use_models = use_models

        # This next part pretty much just goes through the motions of what
        # from_url() does in the parent class.

        # First let's make an http client
        self.http_client = RequestsClient()
        # Now let's get the spec
        spec_url = urljoin(self.url, '/docs/swagger.json')
        loader = Loader(self.http_client)
        spec_dict = loader.load_spec(spec_url)
        # Now we can create the spec client
        config = {
            'include_missing_properties': False,
            'formats': [email_format],
            'use_models': self.use_models
        }
        # Apply bravado config defaults
        bravado_config = bravado_config_from_config_dict(config)
        # set bravado config object
        config['bravado'] = bravado_config_from_config_dict(config)

        swagger_spec = Spec.from_dict(
            spec_dict, origin_url=spec_url, http_client=self.http_client,
            config=config)
        # Now that we have the spec client we can init the parent class
        super(OpsyClient, self).__init__(
            swagger_spec, bravado_config.also_return_response)

        # Go ahead and auth if we were passed creds.
        if user_name and password:
            self.authenticate(user_name, password, force_renew=force_renew)

    def authenticate(self, user_name, password, force_renew=False):
        host = urlsplit(self.url).hostname
        body = {'user_name': user_name,
                'password': password,
                'force_renew': force_renew}
        if self.use_models:
            token = self.login.create_login(body=body).response().result.token
        else:
            token = self.login.create_login(
                body=body).response().result['token']
        # in the future we should probably create our own authenticator
        # class that's intelligent enough to re-auth, but for now we can
        # just use the built in api key class from bravado through set_api_key.
        self.swagger_spec.http_client.set_api_key(
            host, token,
            param_name='X-AUTH-TOKEN', param_in='header'
        )
        self.authenticated = True

    def __dir__(self):
        # The parent class overrides __dir__ to only show the swagger resources
        # but we probably shouldn't hide everything.
        dir_keys = ['authenticate', 'authenticated', 'swagger_spec', 'url',
                    'get_model', 'http_client']
        dir_keys.extend(super(OpsyClient, self).__dir__())
        return dir_keys

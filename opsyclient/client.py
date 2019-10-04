from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient

class OpsyClient:


    def __init__(self, user_name, password=None, url=None):
        self.user_name = user_name
        self.password = password
        self.url = url
        self.create_login(user_name, password, url)


    def create_login(self, u, p, r):
        self.url = r + '/docs/swagger.json'
        self.config = {
            'include_missing_properties': False
        }
        
        self.http_client = RequestsClient()
        
        client = SwaggerClient.from_url(
            self.url,
            http_client=self.http_client,
            config=self.config
        )

        self.login = client.login.create_login(body={"user_name": u,
                                                       "password": p}).response().result
        return self.login


    def logout(self, l, u):
        pass

# OpsyClient
It's Opsy! A simple multi-user/role operations inventory system with aspirations, now in client form!

## Example Usage
    from opsyclient import OpsyClient
    client = OpsyClient('http://127.0.0.1:5000/', user_name='admin', password='password')
    my_zones = client.zones.list_zones().response().result


import base64
import requests
import datetime
from urllib.parse import urlencode
import pandas as pd


client_id = '3e263c6365414d75ada53c7cccbe623f'
client_secret = '68ea48bf8bec48d7b4bdf809e74e0f61'

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id: str, client_secret: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.client_secret = client_secret
        self.client_id = client_id
        
    def get_client_credentials(self):
        """
        Retorna un string en formato Base64
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception('Debes establecer un client_id y client_secret primero')
        client_creds = f'{client_id}:{client_secret}'
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {'Authorization': f'Basic {client_creds_b64}'}
    def get_token_data(self):
        return {'grant_type':'client_credentials'}
    
    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            print(r.status_code)
            raise Exception("No se pudo autenticar el cliente")
        data = r.json()
        access_token = data['access_token']
        now = datetime.datetime.now()
        token_expires = data['expires_in']
        expires = now + datetime.timedelta(seconds=token_expires)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
            token = self.access_token
            token_expired = self.access_token_expires
            now = datetime.datetime.now()
            if token_expired < now:
                self.perform_auth()
                return self.get_access_token()
            
            elif token == None:
                self.perform_auth()
                return self.get_access_token()
            return token

    def get_headers(self):
        access_token = self.get_access_token()
        headers= {'Authorization': f'Bearer {access_token}'}
        return headers

    def get_resource(self, resource_type, lookup_id,version = 'v1'):
        endpoint = f'https://api.spotify.com/{version}/{resource_type}/{lookup_id}'
        headers = self.get_headers()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()

    def get_album(self, _id):
        return self.get_resource(resource_type='albums', lookup_id=_id)
    
    def get_artist(self, _id):
        return self.get_resource(resource_type='artists', lookup_id=_id)

    def __base_search__(self, query_params):
        endpoint = 'https://api.spotify.com/v1/search'
        headers = self.get_headers()
        lookup_url = f'{endpoint}?{query_params}'

        r = requests.get(lookup_url, headers=headers)
        if r.status_code in range(200,299):
            print('La busqueda fue exitosa')
            return r.json()
        else: return {}

    def search(self, query=None, search_type='artists'):
        if query == None:
            raise Exception('Se necesita un query para ejecutar la busqueda')
        if isinstance(query, dict):
            query = " ".join([f'{k}:{v}' for k, v in query.items()])
        query_params = urlencode({'q':query, 'type': search_type.lower()})
        return self.__base_search__(query_params=query_params)

    def get_song_table(self, query=None, search_type='track'):
        content = self.search(query=query, search_type=search_type)
        table = []
        for i in content['tracks']['items']:
            table.append([i['name'],i['album']['name'], i['album']['artists'][0]['name'], i['album']['artists'][0]['id']])
        df = pd.DataFrame(table[0:], columns=['Song', 'Album', 'Artist', 'Artist_id'])
        
        return df




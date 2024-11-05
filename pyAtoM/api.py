"""
pyAtoM library for working with the AtoM API

author:     James Carr
licence:    Apache License 2.0

"""
import json
import os
import platform
import sys


import requests
from requests import Session
from requests.auth import HTTPBasicAuth

import pyAtoM

API_KEY_HEADER = "REST-API-Key"


class Authentication:

    def __init__(self, username: str = None, password: str = None, api_key: str = None, server: str = None,
                 protocol: str = "https"):
        """

        :param username:  username of the account for basic authentication. Optional if using API KEY
        :param password:  password of the account for basic authentication. Optional if using API KEY
        :param api_key:   The API key if not using basic authentication
        :param server:    The URL of the AtoM server
        """

        self.session: Session = requests.Session()
        self.api_token = api_key

        headers = {"Accept": "application/json"}
        if (username is not None) and (password is not None):
            self.auth = HTTPBasicAuth(username, password)
        else:
            if self.api_token is not None:
                headers['REST-API-Key'] = self.api_token
            self.auth = None

        self.session.headers.update({'User-Agent': f'pyAtoM SDK/({pyAtoM.__version__}) '
                                                   f' ({platform.platform()}/{os.name}/{sys.platform})'})

        self.base_url = f"{protocol}://{server}"
        path = "/api/informationobjects"
        url = f"{self.base_url}{path}"
        response = self.session.get(url, auth=self.auth, headers=headers)
        if response.status_code != requests.codes.ok:
            raise RuntimeError("Not Authenticated")

class AccessToMemory(Authentication):

    def search(self, query: str, sf_culture: str = None, **kwargs):
        """
        Search the repository for information objects matching the search


        :param query:
        :param sf_culture:  ISO 639-1 language code defaults to the default culture of the application.
        :return: A dict object containing the ISAD(g) metadata
        """
        headers = {"Accept": "application/json"}
        if self.api_token is not None:
            headers['REST-API-Key'] = self.api_token
        path = "/api/informationobjects"
        url = f"{self.base_url}{path}"
        response = self.session.get(url, auth=self.auth, headers=headers, params={'sf_culture': sf_culture})
        if response.status_code == requests.codes.ok:
            document = response.content.decode("utf-8")
            return json.loads(document)

    def get_by_identifier(self, identifier: str, sf_culture: str = None) -> dict | None:
        """
        Return an information object by its identifier, not the slug


        :param identifier:
        :param sf_culture:  ISO 639-1 language code defaults to the default culture of the application.
        :return: A dict object containing the ISAD(g) metadata
        """

        headers = {"Accept": "application/json"}
        if self.api_token is not None:
            headers['REST-API-Key'] = self.api_token
        path = "/api/informationobjects"
        url = f"{self.base_url}{path}"
        params = {'sq0': f'\"{identifier}\"', 'sf0': "identifier", 'sort': 'identifier', 'sf_culture': sf_culture}
        response = self.session.get(url, auth=self.auth, headers=headers, params=params)
        if response.status_code == requests.codes.ok:
            document = response.content.decode("utf-8")
            return json.loads(document)

    def get_parent(self, slug: str, sf_culture: str = None) -> dict | None:
        """
        This method will obtain all information object data available for the parent of the given slug


        :param slug:        the slug of the child object
        :param sf_culture:  ISO 639-1 language code defaults to the default culture of the application.
        :return: A dict object containing the ISAD(g) metadata
        """

        item: dict = self.get(slug, sf_culture=sf_culture)
        if item is not None:
            if 'parent' in item:
                return self.get(item['parent'])

        return None

    def get(self, slug: str, sf_culture: str = None) -> dict:
        """
        This method will obtain all information object data available for a particular slug

        :param slug:        the slug of the information object
        :param sf_culture:  ISO 639-1 language code defaults to the default culture of the application.
        :return: A dict object containing the ISAD(g) metadata
        """
        headers = {"Accept": "application/json"}
        if self.api_token is not None:
            headers['REST-API-Key'] = self.api_token
        path = "/api/informationobjects"
        url = f"{self.base_url}{path}/{slug}"
        response = self.session.get(url, auth=self.auth, headers=headers, params={'sf_culture': sf_culture})
        if response.status_code == requests.codes.ok:
            document = response.content.decode("utf-8")
            d: dict = json.loads(document)
            d['slug'] = slug
            return d

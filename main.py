from config import config
from onedrive_file_grabber import get_all_users
import pandas as pd
import requests
import json
import os

mfa_group_object_ids = [ENTER_YOUR_GROUP_IDS_HERE]


class Header:

    ACCEPT = '"accept": "application/json"'

    def __init__(self, tenant_id, app_id, app_secret, url):
        self._tenant_id = tenant_id
        self._app_id = app_id
        self._app_secret = app_secret
        self._url = url

    @property
    def tenant_id(self):
        return self._tenant_id

    @property
    def app_id(self):
        return self._app_id

    @property
    def app_secret(self):
        return self._app_secret

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, new_url):
        if isinstance(new_url, str):
            self._url = new_url


def azure_token():
    tenant = config.APIkeys.tenant_id
    token_header = Header(config.APIkeys.tenant_id, config.APIkeys.app_id, config.APIkeys.app_secret,
                          url=f"https://login.microsoftonline.com/{tenant}/oauth2/token")
    token_header.url = f"https://login.microsoftonline.com/{token_header.tenant_id}/oauth2/token"
    resource_app_id_uri = 'https://graph.microsoft.com'

    body = {
        'resource': resource_app_id_uri,
        'client_id': token_header.app_id,
        'client_secret': token_header.app_secret,
        'grant_type': 'client_credentials'
    }

    req = requests.post(token_header.url, body)
    response = req.text
    json_response = json.loads(response)
    return json_response['access_token']


def get_all_group_members(token):

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    def handle_pagination(url):
        """Nested function to handle MS Graph paginated data."""
        all_members = []
        while url:
            response = requests.get(url, headers=headers)
            try:
                response.raise_for_status()
                data = response.json()
                all_members.extend(data['value'])
                url = data.get('@odata.nextLink', None)
            except requests.RequestException as e:
                print(f"An error occurred: {e}")
                break
        return all_members

    all_groups_members = {}

    # Iterate over each group ID and fetch its members
    for group_id in mfa_group_object_ids:
        url = f'https://graph.microsoft.com/v1.0/groups/{group_id}/members?$select=id,displayName,mail,userPrincipalName'
        members = handle_pagination(url)
        all_groups_members[group_id] = members

    return all_groups_members


def sort_alphabetically(file):
    df = pd.read_csv(file, header=None, names=['Data'], sep='\t')
    df.sort_values(by='Data', inplace=True)
    df.to_csv(file, index=False, header=False, sep='\t')


# Calling both functions to create bearer token and get MFAd users
access_token = azure_token()
all_members = get_all_group_members(access_token)

if __name__ == '__main__':
    txt_cloud_path = get_all_users()
    all_umb_users_file = txt_cloud_path[0]

    with open('all_mfa_users.txt', 'w') as with_mfa:
        for group_id, members in all_members.items():
            for member in members:
                with_mfa.write(f"{member.get('userPrincipalName')}\n")

    # In-place sorting of the 'all_mfa_users.txt' file alphabetically
    sort_alphabetically('all_mfa_users.txt')
    sort_alphabetically('all_users.txt')

    with open('all_mfa_users.txt', 'r') as with_mfa, open(all_umb_users_file, 'r') as all_users_f:
        with_mfa_lines = set(with_mfa.read().splitlines())
        all_users_f_lines = set(all_users_f.read().splitlines())

    without_mfa_list = all_users_f_lines - with_mfa_lines

    with open('without_mfa.txt', 'w') as without_mfa:
        without_mfa.write("\n".join(without_mfa_list))
    sort_alphabetically('without_mfa.txt')
    final_path = os.path.join('ENTER_PROJECT_PATH_HERE',
                              'ENTER_USERS_WITHOUT_MFA_FILE_HERE')
    print(f"All users without MFA have been written to {final_path}")

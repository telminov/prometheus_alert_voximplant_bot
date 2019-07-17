from typing import List
import requests
import os
import tempfile
import settings


class Notifier:
    def __init__(self, phones: List[str], message: str):
        self.phones = phones
        self.message = message

    def create(self):
        params = {
            'account_id': settings.VOX_ACCOUNT_ID,
            'api_key': settings.VOX_API_KEY,
            'rule_id': settings.VOX_RULE_ID,
            'priority': '1',
            'max_simultaneous': '3',
            'num_attempts': '2',
            'name': 'callList',
        }
        url = 'https://api.voximplant.com/platform_api/CreateCallList/'
        file_path = self._create_call_list()
        with open(file_path, mode='rb') as f:
            response = requests.post(url, params=params, files={'file_content': f})
        os.unlink(file_path)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Create notification error: {response.content}')

    def _create_call_list(self) -> str:
        content = 'phone_number;message\n'
        content += '\n'.join([f'{phone};{self.message}' for phone in self.phones])

        _, file_path = tempfile.mkstemp(prefix='call_list_', suffix='.csv')
        with open(file_path, mode='w') as f:
            f.write(content)

        return file_path

from typing import List
import os
import tempfile
import settings
import aiohttp


class Notifier:
    def __init__(self, phones: List[str], message: str, rule_id: int):
        self.phones = phones
        self.message = message
        self.rule_id = rule_id

    async def create(self):
        params = {
            'account_id': settings.VOX_ACCOUNT_ID,
            'api_key': settings.VOX_API_KEY,
            'rule_id': self.rule_id,
            'priority': '1',
            'max_simultaneous': '3',
            'num_attempts': '2',
            'name': 'callList',
        }
        url = 'https://api.voximplant.com/platform_api/CreateCallList/'
        file_path = self._create_call_list()

        response_json = None
        with open(file_path, mode='rb') as f:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params, data={'file_content': f}) as response:
                    status_code = response.status
                    if status_code == 200:
                        response_json = await response.json()

        os.unlink(file_path)

        if status_code == 200:
            return response_json
        else:
            raise Exception(f'Create notification error: {response.content}')

    def _create_call_list(self) -> str:
        content = 'phone_number;message\n'
        content += '\n'.join([f'{phone};{self.message}' for phone in self.phones])

        _, file_path = tempfile.mkstemp(prefix='call_list_', suffix='.csv')
        with open(file_path, mode='w') as f:
            f.write(content)

        return file_path

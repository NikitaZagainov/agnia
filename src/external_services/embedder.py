import aiohttp
import json
from torch import Tensor
from src.settings import endpoints_settings, team_auth_settings


class Embedder:

    def __init__(self):
        self.url: str = endpoints_settings.embedder_endpoint

    async def get_response(self, json_data) -> Tensor:
        async with aiohttp.ClientSession() as session:
            json_data['team_id'] = team_auth_settings.team_id
            async with session.post(self.url, json=json_data) as response:
                text = await response.text()
                data = json.loads(text)
                if isinstance(data, list):
                    return Tensor(data)
                else:
                    return Tensor()
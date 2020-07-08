from storey import *

import aiohttp
import asyncio
import json
import time


class Setup(NeedsV3ioAccess):
    async def setup(self, table_path):
        connector = aiohttp.TCPConnector()
        client_session = aiohttp.ClientSession(connector=connector)
        for i in range(1, 10):
            request_body = json.dumps({'Item': {'secret': {'N': f'{10 - i}'}}})
            response = await client_session.request(
                'PUT', f'{self._webapi_url}/{table_path}/{i}', headers=self._put_item_headers, data=request_body, ssl=False)
            assert response.status == 200, f'Bad response {response} to request {request_body}'


def test_functional_flow():
    table_path = f'bigdata/{int(time.time_ns() / 1000)}'
    asyncio.run(Setup().setup(table_path))
    controller = build_flow([
        Source(),
        Map(lambda x: x + 1),
        Filter(lambda x: x < 8),
        JoinWithV3IOTable(lambda x: x, lambda x, y: y['secret'], table_path),
        Reduce(0, lambda x, y: x + y)
    ]).run()
    for i in range(10):
        controller.emit(i)

    controller.terminate()
    termination_result = controller.await_termination()
    assert termination_result == 42

from aiohttp import web
from voximplant import Notifier


async def index(request):
    text = "Prometheus alert voximplant bot"
    return web.Response(text=text)


async def alert(request):
    rule_id = request.match_info.get('rule_id')

    data = await request.post()
    phones = data.getall('phone')
    message = data['message']

    notifier = Notifier(phones=phones, message=message, rule_id=rule_id)
    result = await notifier.create()

    return web.json_response(data=result)


app = web.Application()
app.add_routes([web.get('/', index),
                web.post('/alert/{rule_id}', alert)])

web.run_app(app, port=8000)

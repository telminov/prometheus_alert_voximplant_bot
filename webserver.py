import datetime
from aiohttp import web
from voximplant import Notifier


async def index(request):
    print(f'{datetime.datetime.now()} index')
    text = "Prometheus alert voximplant bot"
    return web.Response(text=text)


async def metrics(request):
    print(f'{datetime.datetime.now()} metrics')
    text = "voximplant_bot_alive 1\n"
    return web.Response(text=text)


async def alert(request):
    print(f'{datetime.datetime.now()} alert')

    rule_id = request.match_info.get('rule_id')

    data = await request.json()
    print(data['commonAnnotations'])
    phones = [phone.strip() for phone in data['commonAnnotations']['phones'].split(',') if phone.strip()]
    message = data['commonAnnotations']['description']

    notifier = Notifier(phones=phones, message=message, rule_id=rule_id)
    result = await notifier.create()

    return web.json_response(data=result)


app = web.Application()
app.add_routes([web.get('/', index),
                web.get('/metrics', metrics),
                web.post('/alert/{rule_id}', alert)])

web.run_app(app, port=8000)

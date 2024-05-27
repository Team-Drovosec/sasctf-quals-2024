import time
import redis
import os
import sys
from subprocess import Popen
from base64 import b64encode
from aiohttp import web
from jinja2 import Template
from pydantic import BaseModel, Field, ValidationError

r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)
with open('templates/review.html') as f:
    review_template = Template(f.read())


class BookModel(BaseModel):
    name: str = Field(pattern=r"^[^\x00-\x1F<>\"'();]{3,55}$")
    time: int = Field(gt=int(time.time()))
    visitors: int = Field(ge=1, le=10)
    phone_number: str = Field(pattern=r"^\+?[0-9]{5,14}$")
    comment: str = Field(pattern=r"^[a-zA-Z0-9\x20',\.!\?]{0,500}$")


def add_booking(data):
    bid = r.incr('booking_id')
    r.hset(f'booking:{bid}', mapping=data)
    return bid


def get_booking(bid):
    return r.hgetall(f'booking:{bid}')


async def book(request):
    data = await request.post()
    try:
        qr_image = 'data:image/png;base64,' + b64encode(data['qr_image'].file.read()).decode()
    except AttributeError:
        return web.Response(text='Image not found!')

    try:
        data = BookModel(name=data['name'], time=data['time'], visitors=data['visitors'], phone_number=data['phone_number'], comment=data['comment'])
    except (KeyError, ValidationError):
        return web.Response(text='Validation error!')

    bid = add_booking(data.dict() | {'qr_image': qr_image})

    Popen(["node", "/bot/bot.js", str(bid)], stdout=sys.stdout, stderr=sys.stderr)

    return web.Response(text='OK')


async def review_booking(request):
    booking = request.match_info['booking']
    data = get_booking(booking)
    if data:
        return web.Response(content_type='text/html', text=review_template.render(name=data['name'], time=data['time'], visitors=data['visitors'], phone_number=data['phone_number'], comment=data['comment'], qr_image=data['qr_image']))
    else:
        return web.Response(text='Booking not found!')


def main():
    r.hset(f'booking:0', mapping={
        'name': 'Jessie Pinkman',
        'time': 1337,
        'visitors': 200,
        'phone_number': '+1',
        'comment': 'The flag is somewhere there!',
        'qr_image': os.environ['FLAG_IMAGE'] if 'FLAG_IMAGE' in os.environ else 'WHOOPS'
    })

    app = web.Application()
    app.add_routes([web.post('/book', book), web.get(r'/admin/review_booking/{booking:\d+}', review_booking)])
    web.run_app(app, host='127.0.0.1', port=5500)


if __name__ == '__main__':
    main()

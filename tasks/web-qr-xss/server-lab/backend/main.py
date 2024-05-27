import hashlib
import hmac
import json
import re
import time
from io import BytesIO

import qrcode
from aiohttp import web
from jinja2 import Template
from pydantic import BaseModel, Field, ValidationError
from qrcode.image.pure import PyPNGImage

hmac_secret = b'In the deep bosom of the ocean buried'


with open('templates/warning.html') as f:
    warning_template = Template(f.read())


class QRRequestModel(BaseModel):
    birth_date: str = Field(pattern=r"^[12][0-9]{3}-[01][0-9]-[0-3][0-9]$")
    fullname: str = Field(pattern=r"^[^\x00-\x1F<>\"'();]{3,55}$")
    id_number: int = Field(ge=1000000, le=999999999)


class QRVerifyModel(QRRequestModel):
    expire: int
    authorized_center: str = Field(max_length=60)
    sign: str = Field(min_length=40, max_length=40)


async def verify(request):
    data = await request.post()
    try:
        data = QRVerifyModel(birth_date=data['birth_date'], fullname=data['fullname'], id_number=data['id_number'],
                             expire=data['expire'], authorized_center=data['authorized_center'], sign=data['sign'])
    except (KeyError, ValidationError):
        return web.Response(text='Validation error!')

    payload = f'{data.birth_date}|{data.fullname}|{data.id_number}|{data.expire}|{data.authorized_center}'
    if hmac.new(hmac_secret, payload.encode(), hashlib.sha1).hexdigest() == data.sign:
        return web.Response(text='OK', headers={'Access-Control-Allow-Origin': '*'})
    else:
        return web.Response(text='FAIL', headers={'Access-Control-Allow-Origin': '*'})


async def get_qr(request):
    data = await request.post()
    try:
        data = QRRequestModel(birth_date=data['birth_date'], fullname=data['fullname'], id_number=data['id_number'])
    except (KeyError, ValidationError):
        return web.Response(text='Validation error!')
    expire = int(time.time()) + 604800
    authorized_center = 'LiquidLab PCRMobile'

    payload = f'{data.birth_date}|{data.fullname}|{data.id_number}|{expire}|{authorized_center}'
    sign = hmac.new(hmac_secret, payload.encode(), hashlib.sha1).hexdigest()
    json_data = json.dumps(data.dict() | {'expire': expire, 'authorized_center': authorized_center, 'sign': sign})
    img = qrcode.make(json_data, image_factory=PyPNGImage)
    img_bytes = BytesIO()
    img.save(img_bytes)

    return web.Response(headers={'Content-Disposition': 'attachment'}, content_type='image/png', body=img_bytes.getvalue())


async def issue_warning(request):
    phone = request.query['phone_number'] if 'phone_number' in request.query else 'undefined'
    phone = re.sub(r'[\(\)\:\/\'\"\`\[\]{}\$]', '', phone)
    return web.Response(content_type='text/html', text=warning_template.render(phone_number=phone))


def main():
    app = web.Application()
    app.add_routes([web.post('/get_qr', get_qr), web.post('/verify', verify), web.get('/issue_warning', issue_warning)])
    web.run_app(app, host='127.0.0.1', port=12228)


if __name__ == '__main__':
    main()

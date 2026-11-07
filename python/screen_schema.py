"""Equivalent bounded validation for the bundled ScreenCore schema 1 model."""
import base64
import copy
import json
import math
import re
from validation import fail, obj

def validate_screen(raw):
    if raw is None:
        return None
    obj(raw, 'format version producer name device settings pages assets'.split())
    if raw.get('format') != 'zth-screen-project' or type(raw.get('version')) is not int or raw['version'] != 1:
        fail('SCREEN_SCHEMA')
    encoded = json.dumps(raw, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')
    if len(encoded) > 12 * 1024 * 1024:
        fail('SCREEN_LIMIT')
    def number(value, low, high, integer=False):
        if type(value) not in (int, float) or not math.isfinite(value) or not low <= value <= high or integer and value != int(value):
            fail('SCREEN_NUMBER')
        return value
    def string(value, limit):
        if not isinstance(value, str) or len(value) > limit:
            fail('SCREEN_TEXT')
        return value
    def identifier(value):
        if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,79}', value):
            fail('SCREEN_ID')
        return value
    def boolean(value):
        if type(value) is not bool:
            fail('SCREEN_BOOLEAN')
    def color(value):
        if not isinstance(value, str) or not re.fullmatch(r'#[A-Fa-f0-9]{6}', value):
            fail('SCREEN_COLOR')
    producer = string(raw.get('producer'), 48)
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?', producer):
        fail('SCREEN_PRODUCER')
    string(raw.get('name'), 100)
    d = obj(raw.get('device'), 'board display rotation depth invert i2cAddress pins sd'.split())
    if d.get('board') not in ('s3n16r8', 'c3mini', 's3mini') or d.get('display') not in ('st7789_240', 'st7789_320', 'st7789_135', 'ili9341', 'ssd1306_64', 'ssd1306_32'):
        fail('SCREEN_DEVICE')
    number(d.get('rotation'), 0, 3, True)
    if type(d.get('depth')) is not int or d['depth'] not in (1, 8, 16) or d['display'].startswith('ssd1306') and d['depth'] != 1:
        fail('SCREEN_DEPTH')
    for k in ('invert', 'sd'):
        boolean(d.get(k))
    if type(d.get('i2cAddress')) is not int or d['i2cAddress'] not in (60, 61):
        fail('SCREEN_ADDRESS')
    pin_keys = 'sck mosi miso cs dc rst bl sda scl sdcs'.split()
    pins = obj(d.get('pins'), pin_keys)
    for key in pin_keys:
        number(pins.get(key), -1, 48, True)
    settings = obj(raw.get('settings'), 'grid snap refreshMs demo'.split())
    number(settings.get('grid'), 1, 32)
    number(settings.get('refreshMs'), 100, 10000)
    boolean(settings.get('snap'))
    boolean(settings.get('demo'))
    assets = raw.get('assets')
    if not isinstance(assets, dict) or len(assets) > 40:
        fail('SCREEN_ASSETS')
    for key, asset in assets.items():
        identifier(key)
        obj(asset, ('name', 'data'))
        string(asset.get('name'), 160)
        value = string(asset.get('data'), 3 * 1024 * 1024)
        match = re.fullmatch(r'data:image/(png|jpeg);base64,((?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?)', value)
        if not match:
            fail('SCREEN_IMAGE')
        data = base64.b64decode(match[2], validate=True)
        if not 12 <= len(data) <= 2 * 1024 * 1024:
            fail('SCREEN_IMAGE')
        if match[1] == 'png' and not data.startswith(b'\x89PNG\r\n\x1a\n') or match[1] == 'jpeg' and not (data.startswith(b'\xff\xd8\xff') and data.endswith(b'\xff\xd9')):
            fail('SCREEN_IMAGE')
    pages = raw.get('pages')
    if not isinstance(pages, list) or not 1 <= len(pages) <= 20:
        fail('SCREEN_PAGES')
    ids = set()
    for page in pages:
        obj(page, ('id', 'name', 'background', 'nodes'))
        identity = identifier(page.get('id'))
        if identity in ids:
            fail('SCREEN_DUPLICATE')
        ids.add(identity)
    page_ids = set(ids)
    count, pixels = 0, 0
    for page in pages:
        string(page.get('name'), 100)
        color(page.get('background'))
        if not isinstance(page.get('nodes'), list):
            fail('SCREEN_NODES')
        for n in page['nodes']:
            obj(n, 'id type name x y w h text fontSize color fill radius value min max decimals unit binding target event hidden locked asset'.split())
            identity = identifier(n.get('id'))
            if identity in ids:
                fail('SCREEN_DUPLICATE')
            ids.add(identity)
            count += 1
            if count > 400 or n.get('type') not in ('text', 'button', 'value', 'rect', 'progress', 'circle', 'line', 'image'):
                fail('SCREEN_NODES')
            for key in ('x', 'y'):
                number(n.get(key), -1024, 2048)
            for key in ('w', 'h'):
                number(n.get(key), 1, 1024)
            for key in ('color', 'fill'):
                color(n.get(key))
            number(n.get('radius'), 0, 128)
            number(n.get('fontSize'), 1, 8, True)
            string(n.get('text'), 2000)
            string(n.get('name'), 100)
            if not re.fullmatch(r'[\x20-\x7e]{0,24}', string(n.get('unit'), 24)):
                fail('SCREEN_UNIT')
            for key in ('value', 'min', 'max'):
                number(n.get(key), -1e6, 1e6)
            if n['max'] <= n['min']:
                fail('SCREEN_RANGE')
            number(n.get('decimals'), 0, 4, True)
            if n.get('binding') not in ('', 'temperature', 'battery', 'counter'):
                fail('SCREEN_SIGNAL')
            target = string(n.get('target'), 80)
            if target and target not in page_ids:
                fail('SCREEN_TARGET')
            event = string(n.get('event'), 80)
            if event:
                identifier(event)
            for key in ('hidden', 'locked'):
                boolean(n.get(key))
            if 'asset' in n:
                string(n['asset'], 80)
                if n['asset']:
                    identifier(n['asset'])
                if n['type'] == 'image' and n['asset'] and n['asset'] not in assets:
                    fail('SCREEN_IMAGE_MISSING')
            if not n['hidden'] and n['type'] in ('text', 'button', 'image'):
                pixels += math.floor(n['w'] + 0.5) * math.floor(n['h'] + 0.5)
                if pixels > 1500000:
                    fail('SCREEN_PIXELS')
    return copy.deepcopy(raw)

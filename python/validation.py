"""Bounded, allowlisted project format. No user-supplied file access."""
import base64
import binascii
import datetime as dt
import ipaddress
import re
from urllib.parse import urlsplit


class DeskError(Exception):
    def __init__(self, code, message):
        self.code, self.message = code, message
        super().__init__(message)


def fail(code="PROJECT_INVALID", message="项目格式或字段无效 / Invalid project format or field."):
    raise DeskError(code, message)


def obj(value, allowed):
    if not isinstance(value, dict) or set(value) - set(allowed):
        fail()
    return value


def text(value, maximum, required=False):
    if not isinstance(value, str) or len(value) > maximum or any((ord(c) < 32 and c not in "\n\r\t") or ord(c) == 127 for c in value):
        fail()
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    if required and not value.strip():
        fail()
    return value


def choice(value, values):
    if value not in values or not isinstance(value, str):
        fail()
    return value


def boolean(value):
    if type(value) is not bool:
        fail()
    return value


def ident(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", value):
        fail()
    if re.fullmatch(r'(con|prn|aux|nul|com[1-9]|lpt[1-9])', value, re.I):
        fail('RESERVED_NAME')
    return value


def array(value, limit):
    if not isinstance(value, list) or len(value) > limit:
        fail()
    return value


def unique(values, key="id"):
    ids = [v[key] for v in values]
    if len(ids) != len(set(ids)):
        fail("DUPLICATE_ID", "编号重复 / Duplicate identifier.")
    return values


def domain(value):
    value = text(value, 253).strip()
    if not value:
        return ""
    if value.endswith('.') or any(c in value for c in "/\\:@?#%") or any(c.isspace() for c in value):
        fail("DOMAIN_INVALID", "只填域名，不含协议、路径或端口 / Enter a hostname without protocol, path or port.")
    try:
        value = value.encode("idna").decode("ascii").lower()
        ipaddress.ip_address(value)
    except ValueError:
        pass
    except UnicodeError:
        fail("DOMAIN_INVALID")
    else:
        fail("DOMAIN_INVALID", "请使用公共域名 / Use a public hostname.")
    if len(value) > 253 or "." not in value or value.endswith((".local", ".localhost", ".internal")) or not all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", part) for part in value.split(".")):
        fail("DOMAIN_INVALID")
    return value


def link(value):
    value = text(value, 2048).strip()
    if not value:
        return ""
    if re.search(r"[\x00-\x20\\<>\"'`]|%0[ad]|%00", value, re.I):
        fail("LINK_INVALID", "链接包含不安全字符 / Link contains unsafe characters.")
    if re.fullmatch(r"(?:\./)?[a-z0-9]+(?:-[a-z0-9]+)*\.html(?:#[A-Za-z][A-Za-z0-9_-]{0,63})?", value):
        return value
    if value.lower().startswith("https://"):
        try:
            parsed = urlsplit(value)
            if not parsed.hostname or parsed.username or parsed.password or parsed.port not in (None, 443):
                fail("LINK_INVALID")
            domain(parsed.hostname)
        except ValueError:
            fail("LINK_INVALID")
        return value
    if re.fullmatch(r"mailto:[A-Za-z0-9.!#$&*+\-/=?^_{}|~]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", value):
        domain(value.rsplit("@", 1)[1])
        return value
    if re.fullmatch(r"tel:\+?[0-9().-]{3,30}", value):
        return value
    fail("LINK_INVALID", "链接仅支持 HTTPS、邮件、电话或本项目 HTML 页面 / Use HTTPS, email, phone or a project HTML page.")


def timestamp(value):
    value = text(value, 40)
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?Z', value):
        fail()
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        fail()
    return value


def validate(project):
    p = obj(project, "format schema producer id name updatedAt settings operations site".split())
    if p.get("format") != "zth-desk-project" or type(p.get("schema")) is not int or p["schema"] != 1:
        fail("SCHEMA_UNSUPPORTED", "项目版本不受支持；原文件未修改 / Unsupported project version; original file is unchanged.")
    producer = p.get('producer')
    if not isinstance(producer, str) or len(producer) > 48 or not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?', producer):
        fail('PRODUCER_INVALID')
    settings = obj(p.get("settings"), "language theme autoBuild".split())
    operations = obj(p.get("operations"), "tasks drafts".split())
    site = obj(p.get("site"), "title description language theme accent domain basePath pages assets".split())
    result = {"format": "zth-desk-project", "schema": 1, "producer": producer, "id": ident(p.get("id")), "name": text(p.get("name"), 120, True), "updatedAt": timestamp(p.get("updatedAt", "")), "settings": {"language": choice(settings.get("language", "zh"), ("zh", "en")), "theme": choice(settings.get("theme", "warm"), ("warm", "light", "dark")), "autoBuild": boolean(settings.get("autoBuild", False))}, "operations": {}, "site": {}}
    tasks = []
    for task in array(operations.get("tasks", []), 500):
        t = obj(task, "id title owner due status channel notes".split())
        due = text(t.get("due", ""), 10)
        if due:
            try:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due):
                    raise ValueError()
                dt.date.fromisoformat(due)
            except ValueError:
                fail("DATE_INVALID")
        tasks.append({"id": ident(t.get("id")), "title": text(t.get("title"), 160, True), "owner": text(t.get("owner", ""), 80), "due": due, "status": choice(t.get("status", "idea"), ("idea", "doing", "review", "done")), "channel": choice(t.get("channel", "other"), ("web", "wechat", "canva", "event", "other")), "notes": text(t.get("notes", ""), 8000)})
    drafts = []
    for draft in array(operations.get("drafts", []), 200):
        d = obj(draft, "id title body tags updatedAt".split())
        tags = [text(t, 40, True) for t in array(d.get("tags", []), 20)]
        if len(set(tags)) != len(tags):
            fail('DUPLICATE_TAG')
        drafts.append({"id": ident(d.get("id")), "title": text(d.get("title"), 160, True), "body": text(d.get("body", ""), 64000), "tags": tags, "updatedAt": timestamp(d.get("updatedAt", ""))})
    result["operations"] = {"tasks": unique(tasks), "drafts": unique(drafts)}
    accent = text(site.get("accent", "#16806a"), 7)
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", accent):
        fail()
    base = text(site.get("basePath", ""), 100)
    if base and not re.fullmatch(r"/[A-Za-z0-9][A-Za-z0-9_-]{0,96}/", base):
        fail("BASE_PATH_INVALID")
    if base in ("/../", "/./"):
        fail("BASE_PATH_INVALID")
    public = {"title": text(site.get("title"), 160, True), "description": text(site.get("description", ""), 2000), "language": choice(site.get("language", "zh-CN"), ("zh-CN", "en")), "theme": choice(site.get("theme", "studio"), ("studio", "editorial", "portfolio")), "accent": accent.lower(), "domain": domain(site.get("domain", "")), "basePath": base, "assets": [], "pages": []}
    total = 0
    for asset in array(site.get("assets", []), 20):
        a = obj(asset, "id name mime data alt".split())
        mime = choice(a.get("mime"), ("image/png", "image/jpeg", "image/webp"))
        encoded = text(a.get("data"), 6990508)
        try:
            data = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            fail("IMAGE_INVALID")
        if not 12 <= len(data) <= 5 * 1024 * 1024:
            fail("IMAGE_LIMIT")
        magic = (mime == "image/png" and data.startswith(b"\x89PNG\r\n\x1a\n")) or (mime == "image/jpeg" and data.startswith(b"\xff\xd8\xff") and data.endswith(b'\xff\xd9')) or (mime == "image/webp" and data.startswith(b"RIFF") and data[8:12] == b"WEBP")
        if not magic:
            fail("IMAGE_INVALID", "图片格式与文件头不符 / Image signature does not match its type.")
        total += len(data)
        if total > 20 * 1024 * 1024:
            fail("IMAGE_LIMIT")
        public["assets"].append({"id": ident(a.get("id")), "name": text(a.get("name"), 160, True), "mime": mime, "data": encoded, "alt": text(a.get("alt", ""), 500)})
    unique(public["assets"])
    asset_ids = {a["id"] for a in public["assets"]}
    def image(value):
        value = text(value, 64)
        if value and value not in asset_ids:
            fail("IMAGE_MISSING", "页面引用了不存在的图片 / A page references a missing image.")
        return value
    for page in array(site.get("pages", []), 20):
        pg = obj(page, "id slug title nav sections".split())
        slug = text(pg.get("slug"), 64, True)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            fail("SLUG_INVALID")
        if re.fullmatch(r'(con|prn|aux|nul|com[1-9]|lpt[1-9])', slug, re.I):
            fail('RESERVED_NAME')
        sections = []
        for section in array(pg.get("sections", []), 30):
            s = obj(section, "id type title body image items link label".split())
            items = []
            for item in array(s.get("items", []), 30):
                i = obj(item, "title body image link".split())
                items.append({"title": text(i.get("title", ""), 160), "body": text(i.get("body", ""), 16000), "image": image(i.get("image", "")), "link": link(i.get("link", ""))})
            sections.append({"id": ident(s.get("id")), "type": choice(s.get("type"), ("hero", "text", "cards", "gallery", "faq", "cta", "contact")), "title": text(s.get("title", ""), 160), "body": text(s.get("body", ""), 16000), "image": image(s.get("image", "")), "items": items, "link": link(s.get("link", "")), "label": text(s.get("label", ""), 160)})
        public["pages"].append({"id": ident(pg.get("id")), "slug": slug, "title": text(pg.get("title"), 160, True), "nav": boolean(pg.get("nav", True)), "sections": unique(sections)})
    unique(public["pages"])
    unique(public["pages"], "slug")
    if sum(p["slug"] == "index" for p in public["pages"]) != 1:
        fail("INDEX_REQUIRED", "网站需要且仅需要一个 index 首页 / Exactly one index home page is required.")
    result["site"] = public
    return result

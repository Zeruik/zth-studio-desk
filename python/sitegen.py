"""Deterministic public-only static site generation; no third-party runtime."""
import base64
import hashlib
import html
import json
import re
from urllib.parse import urlsplit

CSS = r"""*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:6rem}body{--bg:#f6f4ee;--card:#fffefa;--ink:#202b27;--muted:#68736d;--line:#dce2d7;margin:0;background:var(--bg);color:var(--ink);font:17px/1.75 ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}a{color:var(--link);text-underline-offset:.22em;overflow-wrap:anywhere}a:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:5px}img{display:block;width:100%;height:auto;object-fit:cover;border-radius:18px}h1,h2,h3,p{margin-top:0}h1,h2,h3{line-height:1.16;letter-spacing:-.035em}h1{font-size:clamp(2.8rem,7vw,6.3rem);max-width:15ch;font-weight:650;margin-bottom:1.4rem}h2{font-size:clamp(1.8rem,3.5vw,3.2rem);font-weight:600}h3{font-size:1.28rem;font-weight:620}p{overflow-wrap:anywhere;white-space:normal}.muted,.eyebrow{color:var(--muted)}.eyebrow{font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;font-weight:700}.wrap{width:min(1200px,calc(100% - 64px));margin:auto}.skip{position:fixed;left:1rem;top:-8rem;padding:1rem;background:var(--card);z-index:20}.skip:focus{top:1rem}.header{position:sticky;top:0;z-index:10;border-bottom:1px solid var(--line);background:var(--bg)}.header-inner{min-height:88px;display:flex;align-items:center;justify-content:space-between;gap:2rem}.brand{font-weight:750;font-size:1.13rem;letter-spacing:-.03em;text-decoration:none;color:var(--ink);max-width:40%;line-height:1.3}.brand:before{content:'';display:inline-block;width:12px;height:12px;margin-right:10px;border-radius:4px;background:var(--accent)}nav{display:flex;gap:.45rem;flex-wrap:wrap;justify-content:flex-end}nav a{font-size:.87rem;text-decoration:none;color:var(--muted);padding:.5rem .8rem;border-radius:99px}nav a[aria-current]{background:var(--ink);color:var(--bg)}.page-intro{padding:clamp(56px,8vw,120px) 0 48px;display:grid;grid-template-columns:1fr minmax(230px,.45fr);align-items:end;gap:2rem}.page-intro .lead{font-size:1.06rem;color:var(--muted);max-width:44ch}.intro-mark{height:170px;border-radius:90px 90px 25px 90px;background:linear-gradient(135deg,var(--accent),#b2c6a8);position:relative;overflow:hidden;opacity:.9}.intro-mark:before{content:'';position:absolute;border:1px solid #ffffff70;border-radius:50%;width:230px;height:230px;top:-70px;left:20%}.intro-mark:after{content:'';position:absolute;width:80px;height:80px;background:#fff5;border-radius:50%;right:25px;bottom:25px}.section{padding:64px 0;border-top:1px solid var(--line)}.section-head{max-width:760px;margin-bottom:28px}.section-head p{color:var(--muted)}.hero-layout{display:grid;grid-template-columns:1.1fr 1fr;align-items:center;gap:60px}.hero-layout.no-image{grid-template-columns:1fr;max-width:900px}.hero-layout img{aspect-ratio:4/3}.button{display:inline-block;border-radius:99px;padding:.75rem 1.35rem;background:var(--accent);color:var(--accent-ink);text-decoration:none;font-size:.9rem;font-weight:650;margin-top:.5rem}.button:hover{filter:brightness(.9)}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.card{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:26px;overflow:hidden}.card img{aspect-ratio:4/3;margin-bottom:22px}.card p{color:var(--muted);font-size:.94rem}.number{display:block;font-size:.73rem;color:var(--muted);margin-bottom:22px;font-variant-numeric:tabular-nums}.gallery .card{padding:12px}.gallery .caption{padding:12px}.gallery img{aspect-ratio:1/1;margin-bottom:0}.text-body{max-width:780px;font-size:1.05rem}.text-body img{max-height:550px;margin:32px 0}.faq-list{max-width:900px}.faq-list details{padding:22px 0;border-bottom:1px solid var(--line)}summary{cursor:pointer;font-size:1.15rem;font-weight:600}.faq-list details p{margin:18px 0 0;color:var(--muted)}.callout{padding:48px;border-radius:28px;background:var(--card);border:1px solid var(--line);display:flex;gap:2rem;justify-content:space-between;align-items:center}.callout .section-head{margin-bottom:0}.contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:30px}.footer{margin-top:70px;padding:30px 0;border-top:1px solid var(--line);font-size:.8rem;color:var(--muted)}.footer .wrap{display:flex;justify-content:space-between;gap:1rem}.theme-editorial{--bg:#fbfaf7;--card:#fff;--ink:#292822;--muted:#79766d;--line:#dedbd1}.theme-editorial h1,.theme-editorial h2,.theme-editorial .brand{font-family:Georgia,'Noto Serif SC',serif;font-weight:500}.theme-editorial .intro-mark{border-radius:0;background:repeating-linear-gradient(135deg,var(--accent),var(--accent) 3px,transparent 3px,transparent 18px);opacity:.35}.theme-editorial .card,.theme-editorial img,.theme-editorial .callout{border-radius:2px}.theme-editorial .page-intro{padding-top:90px}.theme-portfolio{--bg:#141e20;--card:#1e2c2e;--ink:#edf4ec;--muted:#b6c2ba;--line:#354544}.theme-portfolio .page-intro h1{font-weight:760}.theme-portfolio .card{border-radius:10px}.theme-portfolio .intro-mark{background:radial-gradient(circle at 35% 50%,#d8efcb,var(--accent) 42%,transparent 70%);border-radius:0;filter:saturate(.7)}.theme-portfolio .intro-mark:before,.theme-portfolio .intro-mark:after{display:none}.theme-portfolio .gallery .grid{grid-template-columns:repeat(2,minmax(0,1fr))}@media(max-width:800px){.wrap{width:calc(100% - 36px)}.header-inner{padding:17px 0;min-height:76px;gap:12px;align-items:flex-start}.brand{max-width:42%;font-size:1rem}nav{gap:0}nav a{padding:.35rem .5rem;font-size:.8rem}.page-intro{grid-template-columns:1fr;padding-top:50px}.intro-mark{height:90px;max-width:260px}.hero-layout,.contact-grid{grid-template-columns:1fr;gap:28px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.section{padding:40px 0}.callout{padding:28px;display:block}.footer .wrap{flex-direction:column}}@media(max-width:480px){.grid,.theme-portfolio .gallery .grid{grid-template-columns:1fr}.header-inner{flex-direction:column}.brand{max-width:100%}nav{justify-content:flex-start}.page-intro h1{font-size:2.7rem}.card{padding:20px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{.header{position:static}.intro-mark{display:none}.section,.card{break-inside:avoid}body{--bg:#fff;--ink:#111;--muted:#444;--card:#fff}.button{background:none;color:#111;border:1px solid}}
"""
ESC = lambda value: html.escape(str(value), quote=True)



def css_for(site):
    rgb = tuple(int(site['accent'][i:i + 2], 16) for i in (1, 3, 5))
    def luminance(color):
        linear = [v / 255 / 12.92 if v / 255 <= 0.04045 else ((v / 255 + 0.055) / 1.055) ** 2.4 for v in color]
        return sum(v * w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))
    def contrast(a, b):
        a, b = luminance(a), luminance(b)
        return (max(a, b) + 0.05) / (min(a, b) + 0.05)
    white, black = (255, 255, 255), (0, 0, 0)
    ink = '#ffffff' if contrast(rgb, white) >= contrast(rgb, black) else '#000000'
    dark = site['theme'] == 'portfolio'
    background = (20, 30, 32) if dark else (246, 244, 238)
    link_rgb = rgb
    for _ in range(30):
        if contrast(link_rgb, background) >= 4.5:
            break
        link_rgb = tuple(min(255, round(v * 0.85 + 255 * 0.15)) if dark else round(v * 0.85) for v in link_rgb)
    link_color = '#' + ''.join(format(v, '02x') for v in link_rgb)
    return ':root{--accent:' + site['accent'] + ';--accent-ink:' + ink + ';--link:' + link_color + '}\n' + CSS


def paragraphs(value):
    return "".join("<p>" + ESC(p).replace("\n", "<br>") + "</p>" for p in re.split(r"\n\s*\n", value) if p.strip())


def audit(site):
    errors, warnings = [], []
    pages = {p["slug"] + ".html": p for p in site["pages"]}
    assets = {a["id"]: a for a in site["assets"]}
    used = set()
    for page in site["pages"]:
        if not page["sections"]:
            warnings.append({"code": "EMPTY_PAGE", "page": page["slug"], "message": "页面没有内容区块 / Page has no sections."})
        for section in page["sections"]:
            for item in [section] + section["items"]:
                if item.get("image"):
                    used.add(item["image"])
                    if not assets[item["image"]]["alt"].strip():
                        warnings.append({"code": "ALT_MISSING", "page": page["slug"], "message": "图片缺少替代文本 / An image has no alternative text."})
                href = item.get("link", "")
                if href and not urlsplit(href).scheme:
                    filename, _, anchor = href.removeprefix("./").partition("#")
                    target = pages.get(filename)
                    if target is None or anchor and anchor not in {s["id"] for s in target["sections"]}:
                        errors.append({"code": "BROKEN_LINK", "page": page["slug"], "link": href, "message": "内部页面或锚点不存在 / Internal page or fragment is missing."})
    if not site["domain"]:
        warnings.append({"code": "NO_CANONICAL", "message": "未设置域名，暂不生成绝对规范链接和 sitemap / No domain: absolute canonical URLs and sitemap are omitted."})
    if not site["description"].strip():
        warnings.append({"code": "DESCRIPTION_MISSING", "message": "建议填写网站描述 / Add a website description."})
    if len(used) < len(assets):
        warnings.append({"code": "UNUSED_ASSETS", "message": "未引用的图片不会进入网站包 / Unreferenced images are excluded from the website."})
    return {"errors": errors, "warnings": warnings}, used


def render(site, page, paths, preview=False):
    lang = site["language"]
    zh = lang == "zh-CN"
    words = {"skip": "跳至内容" if zh else "Skip to content", "view": "了解更多" if zh else "Explore", "footer": "由 ZTH Studio Desk 构建" if zh else "Built with ZTH Studio Desk"}
    def picture(asset_id):
        if not asset_id:
            return ""
        asset = next(a for a in site["assets"] if a["id"] == asset_id)
        src = "data:" + asset["mime"] + ";base64," + asset["data"] if preview else "./" + paths[asset_id]
        return '<img src="' + ESC(src) + '" alt="' + ESC(asset["alt"]) + '" loading="lazy" decoding="async">'
    def action(item):
        return '<a class="button" href="' + ESC(item["link"]) + '">' + ESC(item.get("label") or words["view"]) + '</a>' if item.get("link") else ""
    first_hero = page['sections'][0] if page['sections'] and page['sections'][0]['type'] == 'hero' else None
    intro_title = (first_hero['title'] or page['title']) if first_hero else page['title']
    intro_body = first_hero['body'] if first_hero else site['description']
    intro_art = picture(first_hero['image']) if first_hero and first_hero['image'] else '<div class="intro-mark" aria-hidden="true"></div>'
    intro_id = ' id="' + ESC(first_hero['id']) + '"' if first_hero else ''
    intro = '<div class="page-intro"' + intro_id + '><div><p class="eyebrow">' + ESC(site['title']) + '</p><h1>' + ESC(intro_title) + '</h1><div class="lead">' + paragraphs(intro_body) + '</div>' + (action(first_hero) if first_hero else '') + '</div>' + intro_art + '</div>'
    sections = []
    for s in page["sections"][1:] if first_hero else page["sections"]:
        heading = ('<h2>' + ESC(s["title"]) + '</h2>' if s["title"] else "") + paragraphs(s["body"])
        head = '<div class="section-head">' + heading + '</div>'
        kind = s["type"]
        if kind == "hero":
            body = '<div class="hero-layout' + (" no-image" if not s["image"] else "") + '"><div>' + head + action(s) + '</div>' + picture(s["image"]) + '</div>'
        elif kind in ("cards", "gallery"):
            cards = []
            for n, item in enumerate(s["items"], 1):
                cards.append('<article class="card">' + picture(item["image"]) + '<div class="caption"><span class="number">' + str(n).zfill(2) + '</span><h3>' + ESC(item["title"]) + '</h3>' + paragraphs(item["body"]) + action(item) + '</div></article>')
            body = head + '<div class="grid">' + ''.join(cards) + '</div>' + action(s)
        elif kind == "faq":
            body = head + '<div class="faq-list">' + ''.join('<details><summary>' + ESC(i["title"]) + '</summary>' + paragraphs(i["body"]) + action(i) + '</details>' for i in s["items"]) + '</div>'
        elif kind == "cta":
            body = '<div class="callout">' + head + action(s) + '</div>'
        elif kind == "contact":
            body = '<div class="contact-grid"><div>' + head + action(s) + '</div><div>' + ''.join('<article><h3>' + ESC(i["title"]) + '</h3>' + paragraphs(i["body"]) + action(i) + '</article>' for i in s["items"]) + picture(s["image"]) + '</div></div>'
        else:
            body = '<div class="text-body">' + heading + picture(s["image"]) + action(s) + '</div>'
        sections.append('<section class="section ' + kind + '" id="' + ESC(s["id"]) + '">' + body + '</section>')
    main_id = 'zth-main-content'
    while main_id in {s['id'] for s in page['sections']}:
        main_id += '-x'
    nav = ''.join('<a href="./' + ESC(p["slug"]) + '.html"' + (' aria-current="page"' if p["id"] == page["id"] else '') + '>' + ESC(p["title"]) + '</a>' for p in site["pages"] if p["nav"])
    css = css_for(site)
    style = '<style>' + css + '</style>' if preview else '<link rel="stylesheet" href="./assets/site.css">'
    canonical = ""
    if site["domain"]:
        base = 'https://' + site["domain"] + (site["basePath"] or '/')
        canonical = '<link rel="canonical" href="' + ESC(base + ('' if page["slug"] == 'index' else page["slug"] + '.html')) + '">'
    csp = "default-src 'none'; img-src data:; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'" if preview else "default-src 'none'; img-src 'self' data:; style-src 'self'; base-uri 'none'; form-action 'none'"
    title = site["title"] if page["slug"] == "index" else page["title"] + " · " + site["title"]
    return '<!doctype html>\n<html lang="' + lang + '"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="' + ESC(csp) + '"><title>' + ESC(title) + '</title><meta name="description" content="' + ESC(site["description"]) + '"><meta name="generator" content="ZTH Studio Desk 1.0.0"><meta name="color-scheme" content="' + ('dark' if site["theme"] == 'portfolio' else 'light') + '">' + canonical + style + '</head><body class="theme-' + site["theme"] + '"><a class="skip" href="#' + main_id + '">' + words["skip"] + '</a><header class="header"><div class="wrap header-inner"><a class="brand" href="./index.html">' + ESC(site["title"]) + '</a><nav aria-label="' + ('主导航' if zh else 'Main navigation') + '">' + nav + '</nav></div></header><main id="' + main_id + '" class="wrap">' + intro + ''.join(sections) + '</main><footer class="footer"><div class="wrap"><span>' + ESC(site["title"]) + '</span><span>' + words["footer"] + '</span></div></footer></body></html>\n'


def generate(site, preview_slug="index", custom_domain=None):
    report, used = audit(site)
    files, paths = {}, {}
    extensions = {"image/png": "png", "image/jpeg": "jpg", "image/webp": "webp"}
    for asset in site["assets"]:
        if asset["id"] in used:
            data = base64.b64decode(asset["data"])
            filename = 'assets/image-' + hashlib.sha256(data).hexdigest() + '.' + extensions[asset["mime"]]
            files[filename], paths[asset["id"]] = data, filename
    files['assets/site.css'] = css_for(site).encode('utf-8')
    for page in site["pages"]:
        files[page["slug"] + '.html'] = render(site, page, paths).encode('utf-8')
    if site["domain"]:
        base = 'https://' + site["domain"] + (site["basePath"] or '/')
        urls = [base + ('' if p["slug"] == 'index' else p["slug"] + '.html') for p in site["pages"]]
        files['sitemap.xml'] = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + ESC(u) + '</loc></url>' for u in urls) + '</urlset>\n').encode()
        files['robots.txt'] = ('User-agent: *\nAllow: /\nSitemap: ' + base + 'sitemap.xml\n').encode()
    else:
        files['robots.txt'] = b'User-agent: *\nAllow: /\n'
    cname = site["domain"] if custom_domain is None else custom_domain
    if cname:
        files['CNAME'] = (cname + '\n').encode()
    files['.nojekyll'] = b''
    manifest = {"format": "zth-public-site", "version": 1, "files": [{"path": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()} for name, data in sorted(files.items())]}
    files['site-manifest.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    page = next((p for p in site["pages"] if p["slug"] == preview_slug), None)
    if page is None:
        from validation import fail
        fail("PAGE_MISSING", "预览页面不存在 / Preview page does not exist.")
    return files, render(site, page, paths, True), report

"""앱의 PRIVACY.md(한·영·일을 한 파일에 담은 원고)를 <앱>/privacy/index.html로 만든다.

쓰는 법 (이 저장소 루트에서):
    python tools/build_privacy.py dday ../dday-android/PRIVACY.md

원고의 모양: '# 제목' 한 줄, 언어마다 '## 한국어'·'## English'·'## 日本語' 절,
절 안은 '### 소제목'·문단·'- [글](주소)' 목록. HTML 주석과 '---' 줄은 버린다.
원고에 'TODO(출시 전)'이 남은 자리(시행일·문의처)는 출시 전 안내 문구로 바꿔 보여준다.
원고에 값이 들어가면 그 값이 그대로 나온다.
"""
import html
import io
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# 앱마다 한 줄: 언어별 앱 이름
APPS = {
    "dday": {"ko": "나의 디데이", "en": "My D-Day", "ja": "マイD-Day"},
}

# (원고의 '## ' 제목, html lang·id, 방침 제목)
LANGS = [
    ("한국어", "ko", "개인정보처리방침"),
    ("English", "en", "Privacy Policy"),
    ("日本語", "ja", "プライバシーポリシー"),
]

PENDING = {
    "ko": {
        "date": "시행일: 앱을 출시하는 날부터예요. 날짜는 출시할 때 적어요.",
        "contact": "문의처 이메일은 앱을 출시하기 전에 이 자리에 적어요.",
    },
    "en": {
        "date": "Effective date: the day the app is released. The date will be added at release.",
        "contact": "A contact email address will be added here before the app is released.",
    },
    "ja": {
        "date": "施行日：アプリをリリースする日からです。日付はリリース時に記載します。",
        "contact": "お問い合わせ用のメールアドレスは、アプリのリリース前にここに記載します。",
    },
}
DATE_PREFIXES = ("시행일", "Effective date", "施行日")
TODO_MARK = "TODO(출시 전)"

# 귤 마크 (brand/svg/mark.svg와 같은 모양)
MARK = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" aria-hidden="true">'
    '<path d="M10,59 a40,40 0 1,0 80,0 a40,40 0 1,0 -80,0 Z" fill="#F6A13A"/>'
    '<path d="M26.5,43 a7.5,7.5 0 1,0 15.0,0 a7.5,7.5 0 1,0 -15.0,0 Z" fill="#FFFFFF" fill-opacity="0.35"/>'
    '<path d="M44,25 V11 a6,6 0 0,1 12,0 V25 Z" fill="#8A5A2B"/>'
    '<path d="M54,16 Q63,-2 92,3 Q85,24 54,16 Z" fill="#5FAE5C"/>'
    "</svg>"
)


def inline(text: str) -> str:
    """글자를 HTML로 바꾸고 [글](주소)를 링크로."""
    out = html.escape(text, quote=False)
    return re.sub(
        r"\[([^\]]+)\]\(([^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" rel="noopener">{m.group(1)}</a>',
        out,
    )


def blocks(body: str, lang: str) -> str:
    out: list[str] = []
    para: list[str] = []
    items: list[str] = []
    first = True  # 절의 첫 문단은 시행일 줄

    def flush() -> None:
        nonlocal para, items, first
        if para:
            text = " ".join(para)
            if TODO_MARK in text:
                kind = "date" if first else "contact"
                cls = "meta" if first else "pending"
                out.append(f'<p class="{cls}">{html.escape(PENDING[lang][kind], quote=False)}</p>')
            elif first and text.startswith(DATE_PREFIXES):
                out.append(f'<p class="meta">{inline(text)}</p>')
            else:
                out.append(f"<p>{inline(text)}</p>")
            first = False
            para = []
        if items:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in items) + "</ul>")
            items = []

    for line in body.splitlines():
        s = line.strip()
        if not s or s == "---":
            flush()
        elif s.startswith("### "):
            flush()
            out.append(f"<h3>{inline(s[4:])}</h3>")
        elif s.startswith("- "):
            if para:
                flush()
            items.append(s[2:])
        else:
            if items:
                flush()
            para.append(s)
    flush()
    return "\n".join(out)


def build(app: str, source: pathlib.Path) -> pathlib.Path:
    names = APPS[app]
    md = io.open(source, encoding="utf-8").read()
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    parts = re.split(r"^## (.+)$", md, flags=re.M)
    sections = {parts[i].strip(): parts[i + 1] for i in range(1, len(parts), 2)}
    missing = [name for name, _, _ in LANGS if name not in sections]
    if missing:
        raise SystemExit(f"원고에 없는 언어 절: {missing}")

    nav = "".join(f'<a href="#{code}" lang="{code}">{name}</a>' for name, code, _ in LANGS)
    panels = []
    for name, code, title in LANGS:
        panels.append(
            f'<section class="policy" id="{code}" lang="{code}">\n'
            f"<h2>{html.escape(names[code])} {html.escape(title)}</h2>\n"
            f"{blocks(sections[name], code)}\n</section>"
        )
    # 언어마다 lang을 달아야 브라우저가 그 언어의 글꼴을 고른다(한국어 문서 안의 가나가 엉뚱한 글꼴로 나오지 않게)
    lede = " · ".join(f'<span lang="{code}">{html.escape(title)}</span>' for _, code, title in LANGS)
    page = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{html.escape(names["ko"])} 개인정보처리방침 · MildChoco</title>
<meta name="description" content="MildChoco의 Android 앱 '{html.escape(names["ko"])}'({html.escape(names["en"])}) 개인정보처리방침. 한국어 · English · 日本語">
<link rel="icon" href="../../assets/mark.svg" type="image/svg+xml">
<link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
<div class="wrap">
<header class="brand"><a href="../../" aria-label="MildChoco 앱">{MARK}<span class="name">MildChoco</span></a></header>
<main>
<h1>{html.escape(names["ko"])}</h1>
<p class="lede">{lede}</p>
<nav class="langs" aria-label="언어 · Language">{nav}</nav>
{chr(10).join(panels)}
</main>
<footer>© MildChoco · <a href="https://mildchoco.tistory.com/">귤 실험실</a></footer>
</div>
</body>
</html>
"""
    target = ROOT / app / "privacy" / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    io.open(target, "w", encoding="utf-8", newline="\n").write(page)
    return target


if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in APPS:
        raise SystemExit(f"쓰는 법: python tools/build_privacy.py <{'|'.join(APPS)}> <PRIVACY.md 경로>")
    made = build(sys.argv[1], pathlib.Path(sys.argv[2]))
    left = io.open(made, encoding="utf-8").read().count(TODO_MARK)
    print(f"만듦: {made.relative_to(ROOT)} (남은 TODO 표시 {left}개)")

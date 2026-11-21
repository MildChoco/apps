# MildChoco 앱 페이지

MildChoco 앱들의 공개 웹 페이지. 지금은 개인정보처리방침만 있다. GitHub Pages로 올린다: <https://mildchoco.github.io/apps/>

| 주소 | 내용 | 원고 |
| --- | --- | --- |
| `/apps/` | 앱 목록 | `index.html` (직접 고침) |
| `/apps/dday/privacy/` | 나의 디데이 개인정보처리방침 (한·영·일) | 앱 저장소의 `PRIVACY.md` |

## 방침을 고칠 때

방침 글은 각 앱 저장소의 `PRIVACY.md`가 원고다. 여기 HTML을 직접 고치지 않는다.

```powershell
python tools/build_privacy.py dday ..\dday-android\PRIVACY.md
git add -A; git commit -m "나의 디데이 방침 갱신"; git push
```

- 원고에 `TODO(출시 전)`이 남은 자리(시행일·문의처)는 출시 전 안내 문구로 바뀌어 나온다. 원고에 값을 넣고 다시 만들면 그 값이 나온다.
- 앱 안의 '앱 정보 → 개인정보처리방침 → 웹에서 보기'와 Play 콘솔의 개인정보처리방침 주소가 이 페이지를 가리킨다.
- 새 앱을 더할 때: `tools/build_privacy.py`의 `APPS`에 한 줄, `index.html`의 목록에 한 칸, `assets/`에 아이콘.

## 모양

색과 모서리는 앱 테마와 같다(라이트: 크림 `#FFF4E3` 바탕에 초코 `#3B2416` 글자, 다크: `#16161B`). 바깥 글꼴·스크립트·추적 코드를 쓰지 않는다.

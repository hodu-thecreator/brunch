"""Platform-specific writing prompts and guidelines for 전정호(호두)."""

from .base import AUTHOR_CONTEXT

BLOG_PROMPT = f"""
{AUTHOR_CONTEXT}
블로그(네이버)는 호두님의 '개인 욕망을 펼치는 공간'이다.
커리어보다 더 솔직하고 개인적인 이야기, 일상의 관찰, 취미, 관심사를 자유롭게 표현한다.

[블로그 글쓰기 스타일]
- 톤: 친한 친구에게 말하듯 편안하고 솔직한 구어체
- 주제 범위: 안티그래피티 활동, 해외 이민 고민, 일상 관찰, AI 툴 써본 후기, 먹고 마시는 것 등 뭐든
- 개인 감정 솔직하게: "솔직히 좀 무서웠는데", "이게 뭔지 모르겠어서 그냥 해봤다"
- SEO보다 진정성 우선. 정답 없이 열린 결말도 OK
- 마무리: "아직 모르겠다", "좀 더 해봐야 알 것 같다" 같은 미완의 느낌도 자연스럽게
- 분량: 500~900자 (자유)
"""

BRUNCH_PROMPT = f"""
{AUTHOR_CONTEXT}
브런치는 커리어·성장을 다루는 전문가 채널이다. 진지하되 친근하고, 전문적이되 솔직한 톤.
아래 호두의 실제 글쓰기 패턴을 철저히 따라서 작성해줘.

[호두의 브런치 글쓰기 패턴]
1. 시작: 실제 경험/대화/사건에서 출발
   예: "얼마 전 실장님과 점심을 먹으며...", "연간 평가 발표가 올해도 어김없이 찾아왔다"
2. 인용구 블록 + 솔직한 반응: "순간, 뜨끔했다", "네..? 순간 멍해졌다"
3. 자기 고백적 솔직함 + 가벼운 자기비하 유머: "또 순살이 되었다는 나의 슬픈 스토리"
4. 소제목 2~4개로 구조화: 경험 → 깨달음 → 다짐 흐름
5. 마무리: 거창하지 않은 다짐 + 현재진행형 여운 ("허허", "올해는 기대해본다")
6. 독자: 디자이너, 직장인 시니어, 성장 고민하는 사람
- 분량: 700~1000자
"""

INSTAGRAM_PROMPT = f"""
{AUTHOR_CONTEXT}
인스타그램(@hodu_thecreator)은 개인 욕망 채널. 바이오: "가정부 및 집사 / 호주머니의 사생활 👀"
일상·취미·감각적인 순간들을 꾸밈없이 공유하는 공간. 팔로워 약 1,300명.

[인스타그램 캡션 스타일]
- 톤: 꾸밈없이 편안한 내 말투. 과하게 예쁘게 쓰지 않아도 됨
- 첫 줄: 피드에서 멈추게 하는 한 문장 (질문, 독백, 짧은 관찰)
- 본문: 3~5줄. 솔직한 감정·상황·생각. 완성되지 않아도 됨
- 이모지: 1~3개 자연스럽게
- 관심사 반영: 그래피티/거리 감성, 일상 관찰, AI 써본 느낌, 배민 디자이너의 하루 등
- 해시태그: 15~20개, 한국어+영어 혼합, 본문 아래 분리
- 분량: 본문 150자 이내 + 해시태그
"""

LINKEDIN_PROMPT = f"""
{AUTHOR_CONTEXT}
링크드인은 커리어 전문가 채널. 주 독자: 디자인 업계 종사자, 시니어 디자이너, 리더십 고민하는 직장인.
전문적·신뢰감 있되, 딱딱하지 않고 호두님 특유의 따뜻한 에너지가 느껴지는 톤.

[링크드인 포스트 스타일]
- 첫 줄: 선언형 또는 질문형 한 문장으로 스크롤 멈추기
  예: "디자인만 잘하면 된다는 생각, 저도 오래 했습니다."
- 본문: 구체적 경험(1~2문장) → 핵심 인사이트(3가지 이내) → 12년차 실무자 관점
- 주제: 디자인 리더십, 시니어 성장 방향, AI와 디자인, 협업 노하우, 커리어 전환
- 마무리: 독자에게 던지는 질문 또는 댓글 유도
- 이모지: 2~3개, 포인트로만
- 해시태그: 5개 이내, 마지막에
- 분량: 300~500자
"""


def get_platform_prompt(platform: str) -> str:
    """Return the writing prompt for the specified platform."""
    prompts = {
        "brunch": BRUNCH_PROMPT,
        "blog": BLOG_PROMPT,
        "instagram": INSTAGRAM_PROMPT,
        "insta": INSTAGRAM_PROMPT,   # alias
        "linkedin": LINKEDIN_PROMPT,
    }
    return prompts.get(platform.lower(), "")


def get_platform_display_name(platform: str) -> str:
    """Return a human-readable platform name."""
    names = {
        "brunch": "☕ 브런치 (커리어 채널)",
        "blog": "📝 블로그 네이버 (개인 채널)",
        "instagram": "📸 인스타그램 @hodu_thecreator (개인 채널)",
        "insta": "📸 인스타그램 @hodu_thecreator (개인 채널)",
        "linkedin": "💼 링크드인 (커리어 채널)",
    }
    return names.get(platform.lower(), platform)

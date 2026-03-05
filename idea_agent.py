"""
글감 추천 에이전트 - 호두(@hodu) 맞춤형
- 블로그: 전자기기/카메라/인테리어 → 애드포스트+협찬 목적
- 브런치/링크드인: 커리어+AI 시대 대비 전문가
- 인스타: 철학+일상 브랜딩
"""

import anthropic
from config import Config

config = Config()
client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

IDEA_SYSTEM_PROMPT = """
당신은 콘텐츠 크리에이터 '전정호(호두)'의 글감 큐레이터입니다.

[작가 정보]
- 12년차 시니어 그래픽 디자이너, 우아한형제들(배민) 코어그래픽파트
- 얼리어답터: 카메라·전자기기·인테리어 소품에 강한 관심, 협찬/수익화 목적
- AI 툴(Claude, MCP 등) 적극 실험 중
- 안티그래피티/그래피티, 뉴질랜드 이주 준비, 심리 성장 등 개인 관심사 다양

[플랫폼별 방향]
- 블로그: 전자기기(카메라 포함), 인테리어 가구·소품 리뷰/추천 → SEO + 협찬 유치
- 브런치/링크드인: 커리어 성장 + AI 시대를 능동적으로 대비하는 시니어 디자이너
- 인스타: 철학과 일상을 녹인 퍼스널 브랜딩, 영상 스토리 콘텐츠

[임무]
아래 형식에 맞춰 각 플랫폼별 글감 5개씩 추천하세요.
매번 새롭고 구체적인 주제를 제안하세요. 트렌드, 계절, 최근 이슈를 반영하면 더 좋습니다.

[출력 형식 - 반드시 이 형식으로]

📝 *블로그* (제품 리뷰/추천 · 협찬 목적)
1. 제목 아이디어
2. 제목 아이디어
3. 제목 아이디어
4. 제목 아이디어
5. 제목 아이디어

☕ *브런치 & 링크드인* (커리어 + AI)
1. 제목 아이디어
2. 제목 아이디어
3. 제목 아이디어
4. 제목 아이디어
5. 제목 아이디어

📸 *인스타그램* (철학+일상 브랜딩)
1. 주제 아이디어 (영상 콘셉트 한 줄 포함)
2. 주제 아이디어
3. 주제 아이디어
4. 주제 아이디어
5. 주제 아이디어

---
💡 마음에 드는 번호와 플랫폼을 알려주세요.
예) "블로그 3번" 또는 "브런치 2번, 브런치로"
"""


class IdeaAgent:

    async def generate_ideas(self) -> str:
        """오늘의 글감 추천 생성"""
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=IDEA_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": "오늘 날짜 기준으로 트렌디하고 구체적인 글감을 추천해줘."
            }]
        )
        return message.content[0].text

    async def generate_ideas_with_context(self, context: str) -> str:
        """특정 맥락/키워드 기반 글감 추천"""
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=IDEA_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"아래 맥락/키워드를 참고해서 글감을 추천해줘:\n{context}"
            }]
        )
        return message.content[0].text

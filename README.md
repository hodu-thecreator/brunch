# ✍️ 멀티플랫폼 콘텐츠 관리 에이전트

**브런치 ☕ | 블로그 📝 | 인스타그램 📸 | 링크드인 💼**

Claude AI를 활용해 각 플랫폼에 최적화된 콘텐츠를 생성·관리하는 에이전트입니다.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| `generate` | 플랫폼별 최적화 콘텐츠 자동 생성 |
| `repurpose` | 하나의 글을 다른 플랫폼 형식으로 변환 |
| `topics` | 분야별 콘텐츠 주제 추천 |
| `drafts` | 저장된 초안 목록 관리 |
| `chat` | 에이전트와 대화형 콘텐츠 작업 |

---

## 플랫폼별 최적화 전략

### ☕ 브런치
- 감성적·문학적 에세이 스타일
- 개인 경험 중심의 공감형 서술
- 1,500~3,000자 깊이 있는 글

### 📝 블로그
- SEO 최적화 키워드 배치
- H2/H3 체계적 구조
- 검색 의도에 맞는 정보 제공

### 📸 인스타그램
- 훅 문장 + 핵심 메시지 구조
- 이모지 활용 시각적 흐름
- 플랫폼별 해시태그 전략

### 💼 링크드인
- 전문적 인사이트 + 개인 스토리
- 비즈니스 가치 중심 서술
- 토론 유도 마무리

---

## 설치 및 설정

```bash
# 패키지 설치
pip install -r requirements.txt

# API 키 설정
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 입력
```

---

## 사용법

### 대화형 모드 (추천)
```bash
# 전체 대화
python main.py chat

# 특정 플랫폼 모드
python main.py chat --platform brunch
python main.py chat --platform instagram
```

### 콘텐츠 즉시 생성
```bash
# 브런치 글 생성
python main.py generate "번아웃을 극복하는 방법" --platform brunch

# 인스타그램 캡션 생성 (저장까지)
python main.py generate "봄 카페 추천" --platform instagram --save

# 키워드·톤 지정
python main.py generate "파이썬 비동기 처리" \
  --platform blog \
  --keywords "asyncio,python,비동기" \
  --tone "친근하고 실용적인"
```

### 콘텐츠 재활용 (Repurpose)
```bash
# 브런치 글 → 링크드인 변환
python main.py repurpose --from brunch --to linkedin "여기에 원본 텍스트..."

# 파일로 변환
python main.py repurpose --from blog --to instagram --file my_post.md
```

### 주제 추천
```bash
# 자기계발 분야 주제 5개
python main.py topics "자기계발"

# 특정 플랫폼용 10개 추천
python main.py topics "IT/스타트업" --platform linkedin --count 10
```

### 초안 관리
```bash
# 전체 초안 목록
python main.py drafts

# 플랫폼별 필터
python main.py drafts --platform instagram
```

---

## 프로젝트 구조

```
.
├── main.py                  # CLI 진입점
├── requirements.txt
├── .env.example
├── agent/
│   ├── agent.py             # 핵심 에이전트 (agentic loop)
│   ├── tools.py             # 도구 정의 및 실행
│   └── prompts/
│       ├── base.py          # 에이전트 시스템 프롬프트
│       └── platforms.py     # 플랫폼별 글쓰기 가이드
└── content/
    ├── drafts/              # 저장된 초안
    │   ├── brunch/
    │   ├── blog/
    │   ├── instagram/
    │   └── linkedin/
    └── published/           # 발행 완료 콘텐츠
```

---

## 에이전트 도구 목록

| 도구 | 역할 |
|------|------|
| `generate_content` | 플랫폼 최적화 콘텐츠 생성 |
| `refine_content` | 기존 콘텐츠 개선 |
| `repurpose_content` | 플랫폼 간 콘텐츠 변환 |
| `suggest_topics` | 트렌드 기반 주제 추천 |
| `save_draft` | 초안 파일 저장 |
| `list_drafts` | 초안 목록 조회 |

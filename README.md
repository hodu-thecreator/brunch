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

## 내 말투 학습시키기

에이전트가 내 글쓰기 스타일을 학습하면, 마치 내가 직접 쓴 것 같은 글을 생성합니다.

### 학습 방법

```bash
# 1. 브런치에 올린 글을 파일로 저장 후 학습
python main.py learn --platform brunch --file my_brunch_post.txt

# 2. 직접 붙여넣기 (Ctrl+D로 완료)
python main.py learn --platform instagram

# 3. 여러 번 반복할수록 정확해짐 (샘플 누적)
python main.py learn --platform linkedin --file post1.txt
python main.py learn --platform linkedin --file post2.txt

# 학습된 프로필 확인
python main.py style-profiles
```

### 학습 후 효과

- `generate`, `chat`, `repurpose` 모든 명령에 자동 적용
- 샘플이 많을수록 말투 재현 정확도 향상
- 플랫폼별로 독립적으로 학습 (브런치 에세이체 / 링크드인 전문가체 분리)

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

## 사용법 (빠른 시작)

```bash
# 1단계: 내 글 학습
python main.py learn --platform brunch --file my_post.txt

# 2단계: 내 말투로 글 생성
python main.py generate "요즘 번아웃에 대한 단상" --platform brunch
```

---

## 전체 사용법

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

### 말투 학습 (Style Learning)
```bash
# 파일로 학습
python main.py learn --platform brunch --file essay.txt

# 직접 붙여넣기
python main.py learn --platform instagram

# 학습된 프로필 확인
python main.py style-profiles
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
│   ├── style_learner.py     # 말투 학습 & 프로필 관리
│   ├── tools.py             # 도구 정의 및 실행
│   └── prompts/
│       ├── base.py          # 에이전트 시스템 프롬프트
│       └── platforms.py     # 플랫폼별 글쓰기 가이드
├── style_profiles/          # 학습된 말투 프로필 (플랫폼별 JSON)
│   ├── brunch.json
│   ├── instagram.json
│   └── linkedin.json
└── content/
    ├── drafts/              # 저장된 초안
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

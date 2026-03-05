"""Style profile analyzer and manager.

Learns the user's writing style from provided samples and saves profiles
per platform. The agent uses these profiles to mimic the user's voice.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import anthropic

PROFILES_DIR = Path(__file__).parent.parent / "style_profiles"
MODEL = "claude-opus-4-6"


def _profile_path(platform: str) -> Path:
    return PROFILES_DIR / f"{platform}.json"


def load_style_profile(platform: str) -> dict | None:
    """Load an existing style profile for a platform. Returns None if not found."""
    path = _profile_path(platform)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def list_profiles() -> list[dict]:
    """List all existing style profiles."""
    profiles = []
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(PROFILES_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            profiles.append({
                "platform": path.stem,
                "samples_count": data.get("samples_count", 0),
                "updated": data.get("updated", ""),
                "has_profile": bool(data.get("style_dna")),
            })
        except Exception:
            pass
    return profiles


def add_sample_and_analyze(platform: str, new_sample: str, api_key: str | None = None) -> dict:
    """Add a writing sample and re-analyze the style profile.

    Loads any existing profile, appends the new sample, then calls Claude
    to extract and update the style DNA.
    """
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing profile or create fresh one
    existing = load_style_profile(platform) or {
        "platform": platform,
        "samples": [],
        "samples_count": 0,
        "style_dna": None,
        "created": datetime.now().isoformat(),
        "updated": datetime.now().isoformat(),
    }

    # Append the new sample
    existing["samples"].append({"text": new_sample, "added": datetime.now().isoformat()})
    existing["samples_count"] = len(existing["samples"])
    existing["updated"] = datetime.now().isoformat()

    # Analyze all samples together for a holistic style profile
    all_samples = "\n\n---\n\n".join(
        f"[샘플 {i+1}]\n{s['text']}" for i, s in enumerate(existing["samples"])
    )

    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    analysis_prompt = f"""다음은 {platform} 플랫폼에 올린 실제 글 샘플입니다.
이 글들을 분석해서 작성자의 고유한 글쓰기 스타일 DNA를 추출해주세요.

## 글 샘플들
{all_samples}

## 분석 요청
다음 항목을 JSON 형식으로 정확하게 분석해주세요:

{{
  "tone": "전반적인 톤앤매너 (예: 따뜻하고 솔직한, 유머러스하면서 진지한 등)",
  "sentence_style": "문장 스타일 특징 (길이, 구조, 리듬감 등)",
  "vocabulary": "자주 쓰는 어휘 패턴과 표현 방식",
  "opening_pattern": "글/게시물을 시작하는 방식의 패턴",
  "closing_pattern": "글/게시물을 마무리하는 방식의 패턴",
  "emotional_expression": "감정 표현 방식 (직접적/간접적, 온도감 등)",
  "humor_style": "유머나 위트 사용 방식 (없으면 '없음')",
  "unique_expressions": ["작성자만의 독특한 표현, 자주 쓰는 문구 최대 10개"],
  "paragraph_rhythm": "단락 구성과 호흡 방식",
  "topics_themes": "주로 다루는 주제와 테마",
  "persona": "글에서 드러나는 작성자의 페르소나",
  "do_use": ["이 스타일을 흉내낼 때 반드시 사용해야 할 요소 5-8개"],
  "dont_use": ["이 스타일에서 절대 쓰지 않는 요소 3-5개"],
  "style_summary": "이 작성자의 글쓰기 스타일을 한 단락으로 요약"
}}

JSON만 출력하세요. 다른 설명은 필요 없습니다."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": analysis_prompt}],
    )

    # Extract JSON from response
    raw = next((b.text for b in response.content if hasattr(b, "text")), "")
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip().rstrip("```").strip()

    style_dna = json.loads(raw)
    existing["style_dna"] = style_dna

    # Save profile
    path = _profile_path(platform)
    path.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")

    return existing


def build_style_system_prompt(platform: str) -> str:
    """Build a system prompt injection from the saved style profile."""
    profile = load_style_profile(platform)
    if not profile or not profile.get("style_dna"):
        return ""

    dna = profile["style_dna"]
    samples_count = profile.get("samples_count", 0)

    prompt = f"""
## 작성자 고유 말투 & 스타일 학습 결과 ({platform.upper()}, 샘플 {samples_count}개 기반)

**스타일 요약:** {dna.get('style_summary', '')}

**페르소나:** {dna.get('persona', '')}

**톤앤매너:** {dna.get('tone', '')}

**문장 스타일:** {dna.get('sentence_style', '')}

**어휘 패턴:** {dna.get('vocabulary', '')}

**감정 표현:** {dna.get('emotional_expression', '')}

**유머/위트:** {dna.get('humor_style', '')}

**글 시작 패턴:** {dna.get('opening_pattern', '')}

**글 마무리 패턴:** {dna.get('closing_pattern', '')}

**단락 리듬:** {dna.get('paragraph_rhythm', '')}

**작성자만의 표현:**
{chr(10).join(f'  - "{expr}"' for expr in dna.get('unique_expressions', []))}

**반드시 사용할 요소:**
{chr(10).join(f'  - {item}' for item in dna.get('do_use', []))}

**절대 쓰지 않는 것:**
{chr(10).join(f'  - {item}' for item in dna.get('dont_use', []))}

**중요:** 위 스타일 분석을 바탕으로, 마치 작성자 본인이 쓴 것처럼 자연스럽게 글을 작성하세요.
어투, 호흡, 표현 방식을 최대한 동일하게 유지하세요.
"""
    return prompt

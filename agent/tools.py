"""Tool definitions for the content management agent."""

import json
import os
from datetime import datetime
from pathlib import Path

DRAFTS_DIR = Path(__file__).parent.parent / "content" / "drafts"

TOOLS = [
    {
        "name": "generate_content",
        "description": (
            "플랫폼에 최적화된 콘텐츠를 생성합니다. "
            "주제, 대상 플랫폼, 추가 지시사항을 입력받아 완성된 콘텐츠를 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["brunch", "blog", "instagram", "linkedin"],
                    "description": "콘텐츠를 생성할 플랫폼",
                },
                "topic": {
                    "type": "string",
                    "description": "글의 주제 또는 핵심 아이디어",
                },
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "포함할 키워드 목록 (선택사항)",
                },
                "tone": {
                    "type": "string",
                    "description": "글의 톤앤매너 (예: 따뜻한, 전문적인, 유머러스한)",
                },
                "additional_instructions": {
                    "type": "string",
                    "description": "추가 작성 지침 (선택사항)",
                },
            },
            "required": ["platform", "topic"],
        },
    },
    {
        "name": "refine_content",
        "description": (
            "기존 콘텐츠를 개선합니다. "
            "원본 텍스트와 개선 방향을 입력받아 수정된 버전을 반환합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["brunch", "blog", "instagram", "linkedin"],
                    "description": "대상 플랫폼",
                },
                "original_content": {
                    "type": "string",
                    "description": "개선할 원본 콘텐츠",
                },
                "refinement_goal": {
                    "type": "string",
                    "description": "개선 목표 (예: 더 감성적으로, SEO 강화, 더 간결하게)",
                },
            },
            "required": ["platform", "original_content", "refinement_goal"],
        },
    },
    {
        "name": "repurpose_content",
        "description": (
            "하나의 콘텐츠를 다른 플랫폼 형식으로 변환합니다. "
            "원본 플랫폼의 글을 타깃 플랫폼에 맞게 재구성합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "source_platform": {
                    "type": "string",
                    "enum": ["brunch", "blog", "instagram", "linkedin"],
                    "description": "원본 콘텐츠의 플랫폼",
                },
                "target_platform": {
                    "type": "string",
                    "enum": ["brunch", "blog", "instagram", "linkedin"],
                    "description": "변환할 대상 플랫폼",
                },
                "original_content": {
                    "type": "string",
                    "description": "변환할 원본 콘텐츠",
                },
            },
            "required": ["source_platform", "target_platform", "original_content"],
        },
    },
    {
        "name": "suggest_topics",
        "description": (
            "플랫폼과 관심사를 기반으로 콘텐츠 주제를 추천합니다. "
            "트렌드와 타깃 독자를 고려한 5-10개의 주제를 제안합니다."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["brunch", "blog", "instagram", "linkedin", "all"],
                    "description": "주제를 추천받을 플랫폼 (all이면 전체)",
                },
                "niche": {
                    "type": "string",
                    "description": "관심 분야 또는 전문 영역 (예: IT, 자기계발, 여행, 육아)",
                },
                "count": {
                    "type": "integer",
                    "description": "추천받을 주제 수 (기본값: 5)",
                    "default": 5,
                },
            },
            "required": ["platform", "niche"],
        },
    },
    {
        "name": "save_draft",
        "description": "생성된 콘텐츠를 초안으로 저장합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["brunch", "blog", "instagram", "linkedin"],
                    "description": "대상 플랫폼",
                },
                "title": {
                    "type": "string",
                    "description": "콘텐츠 제목",
                },
                "content": {
                    "type": "string",
                    "description": "저장할 콘텐츠 내용",
                },
            },
            "required": ["platform", "title", "content"],
        },
    },
    {
        "name": "list_drafts",
        "description": "저장된 초안 목록을 조회합니다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "platform": {
                    "type": "string",
                    "enum": ["brunch", "blog", "instagram", "linkedin", "all"],
                    "description": "조회할 플랫폼 (all이면 전체)",
                    "default": "all",
                },
            },
        },
    },
]


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the result as a string."""
    if tool_name == "save_draft":
        return _save_draft(**tool_input)
    elif tool_name == "list_drafts":
        return _list_drafts(tool_input.get("platform", "all"))
    else:
        # generate_content, refine_content, repurpose_content, suggest_topics
        # are handled by the LLM itself through conversation context
        return json.dumps({"status": "delegated_to_llm", "tool": tool_name, "input": tool_input})


def _save_draft(platform: str, title: str, content: str) -> str:
    """Save content as a draft file."""
    platform_dir = DRAFTS_DIR / platform
    platform_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title)
    safe_title = safe_title[:50].strip()
    filename = f"{timestamp}_{safe_title}.md"
    filepath = platform_dir / filename

    metadata = f"""---
platform: {platform}
title: {title}
created: {datetime.now().isoformat()}
status: draft
---

"""
    filepath.write_text(metadata + content, encoding="utf-8")
    return json.dumps({"status": "saved", "path": str(filepath), "filename": filename})


def _list_drafts(platform: str = "all") -> str:
    """List all draft files."""
    drafts = []
    platforms_to_check = (
        ["brunch", "blog", "instagram", "linkedin"] if platform == "all" else [platform]
    )

    for p in platforms_to_check:
        platform_dir = DRAFTS_DIR / p
        if platform_dir.exists():
            for f in sorted(platform_dir.iterdir(), reverse=True):
                if f.suffix == ".md":
                    drafts.append(
                        {
                            "platform": p,
                            "filename": f.name,
                            "size": f.stat().st_size,
                            "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime(
                                "%Y-%m-%d %H:%M"
                            ),
                        }
                    )

    if not drafts:
        return json.dumps({"status": "empty", "message": "저장된 초안이 없습니다."})
    return json.dumps({"status": "ok", "count": len(drafts), "drafts": drafts})

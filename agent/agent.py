"""Core content management agent using Claude API with tool use."""

import json
import os

import anthropic

from .prompts.base import AGENT_SYSTEM_PROMPT
from .prompts.platforms import get_platform_prompt
from .style_learner import build_style_system_prompt
from .tools import TOOLS, execute_tool

MODEL = "claude-opus-4-6"
MAX_TOKENS = 8096


class ContentAgent:
    """Multi-platform content management agent powered by Claude."""

    def __init__(self, api_key: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.conversation_history: list[dict] = []

    def _build_system_prompt(self, platform: str | None = None) -> str:
        base = AGENT_SYSTEM_PROMPT
        if platform:
            platform_guide = get_platform_prompt(platform)
            if platform_guide:
                base += f"\n\n## 현재 작업 플랫폼 가이드\n{platform_guide}"

            # Inject learned personal style profile if available
            style_injection = build_style_system_prompt(platform)
            if style_injection:
                base += f"\n\n{style_injection}"

        return base

    def _run_agentic_loop(
        self,
        user_message: str,
        platform: str | None = None,
        on_text: callable | None = None,
    ) -> str:
        """Run the agent loop with tool use support."""
        self.conversation_history.append({"role": "user", "content": user_message})
        system_prompt = self._build_system_prompt(platform)

        while True:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                thinking={"type": "adaptive"},
                system=system_prompt,
                tools=TOOLS,
                messages=self.conversation_history,
            )

            # Collect assistant message
            assistant_content = response.content
            self.conversation_history.append({"role": "assistant", "content": assistant_content})

            # If stop reason is end_turn or no tool use, we're done
            if response.stop_reason == "end_turn":
                text_parts = [b.text for b in assistant_content if hasattr(b, "text")]
                final_text = "\n".join(text_parts)
                if on_text:
                    on_text(final_text)
                return final_text

            # Process tool calls
            if response.stop_reason == "tool_use":
                tool_results = []
                for block in assistant_content:
                    if block.type == "tool_use":
                        tool_result = execute_tool(block.name, block.input)

                        # For LLM-delegated tools, inject the platform prompt context
                        if (
                            isinstance(tool_result, str)
                            and "delegated_to_llm" in tool_result
                        ):
                            input_data = block.input
                            tool_platform = input_data.get("platform") or input_data.get(
                                "target_platform"
                            )
                            result_str = self._handle_llm_tool(block.name, input_data, tool_platform)
                        else:
                            result_str = tool_result

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result_str,
                            }
                        )

                self.conversation_history.append({"role": "user", "content": tool_results})
            else:
                # Unexpected stop reason
                text_parts = [b.text for b in assistant_content if hasattr(b, "text")]
                return "\n".join(text_parts)

    def _handle_llm_tool(self, tool_name: str, tool_input: dict, platform: str | None) -> str:
        """Handle tools that require LLM generation, with personal style injection."""
        platform_guide = get_platform_prompt(platform) if platform else ""
        style_guide = build_style_system_prompt(platform) if platform else ""

        style_section = f"\n\n## 작성자 개인 말투 적용\n{style_guide}" if style_guide else ""

        prompts = {
            "generate_content": (
                f"다음 요청에 맞는 {platform} 콘텐츠를 작성하세요.\n\n"
                f"## 플랫폼 가이드라인\n{platform_guide}"
                f"{style_section}\n\n"
                f"## 요청\n"
                f"- 주제: {tool_input.get('topic', '')}\n"
                f"- 키워드: {', '.join(tool_input.get('keywords', []))}\n"
                f"- 톤: {tool_input.get('tone', '자연스러운')}\n"
                f"- 추가 지침: {tool_input.get('additional_instructions', '')}\n\n"
                "완성된 콘텐츠만 출력하세요."
            ),
            "refine_content": (
                f"다음 콘텐츠를 {tool_input.get('refinement_goal')} 방향으로 개선하세요.\n\n"
                f"## 플랫폼 가이드라인\n{platform_guide}"
                f"{style_section}\n\n"
                f"## 원본 콘텐츠\n{tool_input.get('original_content', '')}\n\n"
                "개선된 콘텐츠만 출력하세요."
            ),
            "repurpose_content": (
                f"{tool_input.get('source_platform')} 용 콘텐츠를 "
                f"{tool_input.get('target_platform')} 플랫폼에 맞게 재구성하세요.\n\n"
                f"## 대상 플랫폼 가이드라인\n{platform_guide}"
                f"{style_section}\n\n"
                f"## 원본 콘텐츠\n{tool_input.get('original_content', '')}\n\n"
                "변환된 콘텐츠만 출력하세요."
            ),
            "suggest_topics": (
                f"{tool_input.get('niche')} 분야에서 {tool_input.get('platform')} 플랫폼에 "
                f"적합한 콘텐츠 주제를 {tool_input.get('count', 5)}개 추천해주세요.\n\n"
                "각 주제에 대해 제목과 한 줄 설명을 포함해주세요."
            ),
        }

        prompt = prompts.get(tool_name, f"{tool_name} 요청을 처리해주세요: {tool_input}")

        resp = self.client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            thinking={"type": "adaptive"},
            messages=[{"role": "user", "content": prompt}],
        )
        text_parts = [b.text for b in resp.content if hasattr(b, "text")]
        return "\n".join(text_parts)

    def chat(self, message: str, platform: str | None = None) -> str:
        """Send a message to the agent and get a response."""
        return self._run_agentic_loop(message, platform)

    def reset(self):
        """Reset conversation history."""
        self.conversation_history = []

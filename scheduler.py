"""
호두 글쓰기 봇 - 양방향 텔레그램 봇

기능:
  - 매일 08:00 자동으로 글감 추천 전송
  - 언제든 메시지/명령으로 즉시 요청 가능

명령어:
  /글감           — 지금 바로 글감 추천
  /글감 [키워드]  — 키워드 기반 글감 추천  예) /글감 카메라 소니
  /써줘 [플랫폼] [주제]  — 바로 초안 작성   예) /써줘 블로그 소니 ZV-E10 II 리뷰
  /도움말         — 명령어 안내

실행:
    python scheduler.py

환경변수 (.env):
    TELEGRAM_BOT_TOKEN   — @BotFather 에서 발급
    TELEGRAM_CHAT_ID     — 본인 chat_id (아래 '설정 방법' 참고)
    ANTHROPIC_API_KEY    — Claude API 키

chat_id 확인 방법:
    봇에게 아무 메시지 전송 후
    https://api.telegram.org/bot<TOKEN>/getUpdates 접속 → "chat":{"id": 숫자}
"""

import asyncio
import logging
import os
from datetime import datetime, time
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from idea_agent import IdeaAgent
from writing_agent import WritingAgent

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID", "0"))
IDEAS_DIR = Path("content/ideas")

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

PLATFORM_ALIASES = {
    "블로그": "blog", "blog": "blog",
    "브런치": "brunch", "brunch": "brunch",
    "인스타": "insta", "인스타그램": "insta", "instagram": "insta",
    "링크드인": "linkedin", "linkedin": "linkedin",
}

HELP_TEXT = """
✍️ *호두 글쓰기 봇*

*즉시 요청 명령어*
/글감 — 오늘의 글감 추천 (4개 플랫폼 × 5개)
/글감 소니 카메라 — 키워드 기반 글감 추천
/써줘 블로그 소니 ZV-E10 리뷰 — 바로 초안 작성
/도움말 — 이 안내 보기

*지원 플랫폼*
블로그 · 브런치 · 인스타(그램) · 링크드인

*자동 발송*
매일 오전 8시에 글감 추천이 자동으로 도착합니다.
"""


# ── 유틸 ──────────────────────────────────────────────

def _save_ideas(content: str) -> Path:
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)
    path = IDEAS_DIR / f"{datetime.now().strftime('%Y%m%d')}.md"
    path.write_text(
        f"# {datetime.now().strftime('%Y년 %m월 %d일')} 글감 추천\n\n{content}",
        encoding="utf-8",
    )
    return path


async def _send_long(update_or_bot, chat_id: int, text: str) -> None:
    """4000자 초과 시 자동 분할 전송."""
    limit = 4000
    if hasattr(update_or_bot, "message"):
        send = update_or_bot.message.reply_text
        async def send(t): await update_or_bot.message.reply_text(t, parse_mode="Markdown")
    else:
        async def send(t): await update_or_bot.send_message(chat_id, t, parse_mode="Markdown")

    if len(text) <= limit:
        await send(text)
        return

    chunks, current = [], ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > limit:
            chunks.append(current.strip())
            current = line
        else:
            current += line
    if current.strip():
        chunks.append(current.strip())

    for chunk in chunks:
        await send(chunk)
        await asyncio.sleep(0.3)


# ── 핸들러 ────────────────────────────────────────────

async def cmd_idea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/글감 [키워드] — 즉시 글감 추천."""
    keyword = " ".join(context.args) if context.args else ""
    await update.message.reply_text("⏳ 글감 생성 중... 잠깐만요!")

    try:
        agent = IdeaAgent()
        if keyword:
            ideas = await agent.generate_ideas_with_context(keyword)
            header = f"✍️ *글감 추천* (키워드: {keyword})\n\n"
        else:
            ideas = await agent.generate_ideas()
            header = f"✍️ *{datetime.now().strftime('%m/%d')} 글감 추천*\n\n"

        _save_ideas(ideas)
        await _send_long(update, update.effective_chat.id, header + ideas)

    except Exception as e:
        log.error("글감 생성 오류: %s", e)
        await update.message.reply_text(f"❌ 오류가 발생했어요: {e}")


async def cmd_write(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/써줘 [플랫폼] [주제] — 즉시 초안 작성."""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "사용법: `/써줘 [플랫폼] [주제]`\n예) `/써줘 블로그 소니 ZV-E10 리뷰`",
            parse_mode="Markdown",
        )
        return

    platform_raw = context.args[0]
    topic = " ".join(context.args[1:])
    platform = PLATFORM_ALIASES.get(platform_raw.lower())

    if not platform:
        valid = " · ".join(PLATFORM_ALIASES.keys())
        await update.message.reply_text(f"❌ 지원하지 않는 플랫폼이에요.\n사용 가능: {valid}")
        return

    await update.message.reply_text(f"⏳ *{platform_raw}* 초안 작성 중...", parse_mode="Markdown")

    try:
        agent = WritingAgent()
        result = await agent.write(platform, topic)
        await _send_long(update, update.effective_chat.id, result)
    except Exception as e:
        log.error("글쓰기 오류: %s", e)
        await update.message.reply_text(f"❌ 오류가 발생했어요: {e}")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="Markdown")


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """명령어 외 일반 메시지 안내."""
    await update.message.reply_text(
        "명령어를 사용해주세요 😊\n`/도움말` 로 전체 목록 확인",
        parse_mode="Markdown",
    )


# ── 자동 스케줄 ───────────────────────────────────────

async def daily_ideas_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """매일 08:00 자동 발송."""
    log.info("자동 글감 추천 시작")
    try:
        agent = IdeaAgent()
        ideas = await agent.generate_ideas()
        _save_ideas(ideas)

        header = f"✍️ *{datetime.now().strftime('%m월 %d일')} 글감 추천* (자동 발송)\n\n"
        await _send_long(context.bot, CHAT_ID, header + ideas)
        log.info("자동 글감 추천 전송 완료")
    except Exception as e:
        log.error("자동 발송 오류: %s", e)
        await context.bot.send_message(CHAT_ID, f"❌ 자동 발송 오류: {e}")


# ── 메인 ─────────────────────────────────────────────

def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(".env 에 TELEGRAM_BOT_TOKEN 이 없습니다.")
    if not CHAT_ID:
        raise RuntimeError(".env 에 TELEGRAM_CHAT_ID 가 없습니다.")

    app = Application.builder().token(BOT_TOKEN).build()

    # 명령어 핸들러 등록
    app.add_handler(CommandHandler(["글감", "idea"], cmd_idea))
    app.add_handler(CommandHandler(["써줘", "write"], cmd_write))
    app.add_handler(CommandHandler(["도움말", "help", "start"], cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_unknown))

    # 매일 08:00 자동 발송
    app.job_queue.run_daily(
        daily_ideas_job,
        time=time(hour=8, minute=0),
        chat_id=CHAT_ID,
    )

    print("━" * 42)
    print("  호두 글쓰기 봇 시작")
    print("  /글감  /써줘  /도움말")
    print("  자동 발송: 매일 08:00")
    print("  종료: Ctrl+C")
    print("━" * 42)

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

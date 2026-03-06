"""
매일 오전 8시 글감 추천 → 텔레그램 봇 전송 스케줄러

실행:
    python scheduler.py

환경변수 (.env):
    TELEGRAM_BOT_TOKEN   텔레그램 봇 토큰 (@BotFather에서 발급)
    TELEGRAM_CHAT_ID     전송할 채팅 ID (본인 채팅 또는 그룹)
    ANTHROPIC_API_KEY    Claude API 키
"""

import asyncio
import os
import schedule
import time
from datetime import datetime
from pathlib import Path

import telegram
from dotenv import load_dotenv

from idea_agent import IdeaAgent

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
IDEAS_DIR = Path("content/ideas")
RUN_TIME = "08:00"  # 매일 실행 시각 (24h, KST 기준)


def _save_to_file(content: str) -> Path:
    """글감을 날짜별 마크다운 파일로 저장."""
    IDEAS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    path = IDEAS_DIR / f"{today}.md"
    header = f"# {datetime.now().strftime('%Y년 %m월 %d일')} 글감 추천\n\n"
    path.write_text(header + content, encoding="utf-8")
    return path


async def _send_telegram(text: str) -> None:
    """텔레그램으로 메시지 전송. 4096자 초과 시 자동 분할."""
    bot = telegram.Bot(token=BOT_TOKEN)
    limit = 4000  # 여유 있게 4000자 기준

    if len(text) <= limit:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="Markdown")
        return

    # 섹션(빈 줄 두 개 기준)으로 분할해서 순서대로 전송
    chunks = []
    current = ""
    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > limit:
            chunks.append(current.strip())
            current = line
        else:
            current += line
    if current.strip():
        chunks.append(current.strip())

    for chunk in chunks:
        await bot.send_message(chat_id=CHAT_ID, text=chunk, parse_mode="Markdown")
        await asyncio.sleep(0.5)  # 연속 전송 간 짧은 딜레이


async def run_daily_ideas() -> None:
    """글감 생성 → 파일 저장 → 텔레그램 전송."""
    today_str = datetime.now().strftime("%m월 %d일 (%a)")
    print(f"[{datetime.now().strftime('%H:%M')}] 글감 추천 생성 중...")

    agent = IdeaAgent()
    ideas = await agent.generate_ideas()

    # 파일 저장
    saved_path = _save_to_file(ideas)
    print(f"저장 완료: {saved_path}")

    # 텔레그램 전송
    if BOT_TOKEN and CHAT_ID:
        header = f"✍️ *{today_str} 글감 추천*\n\n"
        await _send_telegram(header + ideas)
        print("텔레그램 전송 완료")
    else:
        print("[경고] TELEGRAM_BOT_TOKEN 또는 TELEGRAM_CHAT_ID 미설정 — 파일에만 저장됨")
        print("\n" + ideas)


def job() -> None:
    asyncio.run(run_daily_ideas())


def main() -> None:
    print("━" * 40)
    print("  호두 글감 추천 스케줄러")
    print(f"  매일 {RUN_TIME} 자동 실행")
    print("━" * 40)

    # 시작하자마자 한 번 즉시 실행 (테스트 겸)
    job()

    # 이후 매일 지정 시각에 실행
    schedule.every().day.at(RUN_TIME).do(job)
    print(f"\n다음 실행: 내일 {RUN_TIME}  (Ctrl+C로 종료)\n")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()

"""Content Management Agent CLI - 멀티플랫폼 콘텐츠 관리 에이전트."""

import os
import sys
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich import box

load_dotenv()

app = typer.Typer(
    name="content-agent",
    help="브런치, 블로그, 인스타그램, 링크드인 콘텐츠 관리 에이전트",
    add_completion=False,
)
console = Console()

PLATFORM_COLORS = {
    "brunch": "bright_green",
    "blog": "bright_blue",
    "instagram": "bright_magenta",
    "linkedin": "bright_cyan",
}

PLATFORM_EMOJIS = {
    "brunch": "☕",
    "blog": "📝",
    "instagram": "📸",
    "linkedin": "💼",
}


def get_agent():
    """Initialize and return the content agent."""
    from agent.agent import ContentAgent

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print(
            "[bold red]오류:[/] ANTHROPIC_API_KEY 환경 변수가 설정되지 않았습니다.\n"
            ".env 파일을 생성하거나 환경 변수를 설정해주세요."
        )
        raise typer.Exit(1)
    return ContentAgent(api_key=api_key)


def print_header():
    """Print the application header."""
    console.print(
        Panel.fit(
            "[bold]✍️  멀티플랫폼 콘텐츠 관리 에이전트[/]\n"
            "[dim]브런치 ☕ | 블로그 📝 | 인스타그램 📸 | 링크드인 💼[/]",
            border_style="bright_yellow",
        )
    )


@app.command()
def chat(
    platform: Optional[str] = typer.Option(
        None,
        "--platform",
        "-p",
        help="플랫폼 지정 (brunch/blog/instagram/linkedin)",
    ),
):
    """에이전트와 대화형으로 콘텐츠를 작성합니다."""
    print_header()

    if platform and platform not in ["brunch", "blog", "instagram", "linkedin"]:
        console.print("[red]올바른 플랫폼을 선택해주세요: brunch, blog, instagram, linkedin[/]")
        raise typer.Exit(1)

    agent = get_agent()

    if platform:
        emoji = PLATFORM_EMOJIS.get(platform, "")
        color = PLATFORM_COLORS.get(platform, "white")
        console.print(f"\n[{color}]{emoji} {platform.upper()} 모드로 시작합니다.[/]\n")
    else:
        console.print("\n[dim]💡 팁: --platform 옵션으로 특정 플랫폼을 지정할 수 있습니다.[/]\n")

    console.print("[dim]'quit' 또는 'exit'를 입력하면 종료합니다. 'reset'으로 대화를 초기화합니다.[/]\n")

    while True:
        try:
            user_input = Prompt.ask("[bold green]나[/]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]종료합니다.[/]")
            break

        if user_input.lower() in ("quit", "exit", "종료"):
            console.print("[dim]종료합니다.[/]")
            break

        if user_input.lower() in ("reset", "초기화"):
            agent.reset()
            console.print("[yellow]대화 내역이 초기화되었습니다.[/]\n")
            continue

        if not user_input.strip():
            continue

        with console.status("[dim]생각 중...[/]", spinner="dots"):
            response = agent.chat(user_input, platform=platform)

        console.print()
        console.print(Panel(Markdown(response), title="[bold]에이전트[/]", border_style="bright_yellow"))
        console.print()


@app.command()
def generate(
    topic: str = typer.Argument(..., help="글의 주제"),
    platform: str = typer.Option(..., "--platform", "-p", help="플랫폼 (brunch/blog/instagram/linkedin)"),
    tone: str = typer.Option("자연스러운", "--tone", "-t", help="글의 톤앤매너"),
    keywords: Optional[str] = typer.Option(None, "--keywords", "-k", help="키워드 (쉼표로 구분)"),
    save: bool = typer.Option(False, "--save", "-s", help="초안으로 저장"),
):
    """특정 플랫폼용 콘텐츠를 바로 생성합니다."""
    if platform not in ["brunch", "blog", "instagram", "linkedin"]:
        console.print("[red]올바른 플랫폼을 선택해주세요: brunch, blog, instagram, linkedin[/]")
        raise typer.Exit(1)

    print_header()
    agent = get_agent()

    kw_list = [k.strip() for k in keywords.split(",")] if keywords else []
    emoji = PLATFORM_EMOJIS.get(platform, "")
    color = PLATFORM_COLORS.get(platform, "white")

    console.print(f"\n[{color}]{emoji} {platform.upper()}[/] 콘텐츠 생성 중...\n")
    console.print(f"  주제: [bold]{topic}[/]")
    if kw_list:
        console.print(f"  키워드: {', '.join(kw_list)}")
    console.print(f"  톤: {tone}\n")

    message = (
        f"다음 요청으로 콘텐츠를 생성해주세요.\n\n"
        f"- 플랫폼: {platform}\n"
        f"- 주제: {topic}\n"
        f"- 톤: {tone}\n"
        f"- 키워드: {', '.join(kw_list) if kw_list else '없음'}\n\n"
        f"generate_content 도구를 사용해서 완성된 콘텐츠를 작성하고, "
        f"결과물을 그대로 보여주세요."
    )

    if save:
        message += f"\n\n작성이 완료되면 save_draft 도구를 사용해 '{topic}'라는 제목으로 초안을 저장해주세요."

    with console.status("[dim]콘텐츠 생성 중...[/]", spinner="dots"):
        response = agent.chat(message, platform=platform)

    console.print(Panel(Markdown(response), title=f"[bold]{emoji} {platform.upper()} 콘텐츠[/]", border_style=color))


@app.command()
def repurpose(
    source: str = typer.Option(..., "--from", "-f", help="원본 플랫폼"),
    target: str = typer.Option(..., "--to", "-t", help="변환할 플랫폼"),
    content: Optional[str] = typer.Argument(None, help="변환할 콘텐츠 (없으면 stdin 또는 파일 입력)"),
    file: Optional[typer.FileText] = typer.Option(None, "--file", help="콘텐츠 파일 경로"),
):
    """기존 콘텐츠를 다른 플랫폼용으로 변환합니다."""
    for p in [source, target]:
        if p not in ["brunch", "blog", "instagram", "linkedin"]:
            console.print(f"[red]'{p}'는 올바른 플랫폼이 아닙니다.[/]")
            raise typer.Exit(1)

    if file:
        original_content = file.read()
    elif content:
        original_content = content
    else:
        console.print("[dim]변환할 콘텐츠를 입력하세요 (Ctrl+D로 완료):[/]")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        original_content = "\n".join(lines)

    if not original_content.strip():
        console.print("[red]콘텐츠가 비어있습니다.[/]")
        raise typer.Exit(1)

    print_header()
    agent = get_agent()

    src_emoji = PLATFORM_EMOJIS.get(source, "")
    tgt_emoji = PLATFORM_EMOJIS.get(target, "")
    tgt_color = PLATFORM_COLORS.get(target, "white")

    console.print(f"\n{src_emoji} {source.upper()} → {tgt_emoji} {target.upper()} 변환 중...\n")

    message = (
        f"repurpose_content 도구를 사용해서 다음 콘텐츠를 변환해주세요.\n\n"
        f"- 원본 플랫폼: {source}\n"
        f"- 변환 대상: {target}\n\n"
        f"원본 콘텐츠:\n{original_content}"
    )

    with console.status("[dim]변환 중...[/]", spinner="dots"):
        response = agent.chat(message, platform=target)

    console.print(
        Panel(Markdown(response), title=f"[bold]{tgt_emoji} {target.upper()} 버전[/]", border_style=tgt_color)
    )


@app.command()
def topics(
    niche: str = typer.Argument(..., help="관심 분야 (예: 자기계발, IT, 여행)"),
    platform: str = typer.Option("all", "--platform", "-p", help="플랫폼 (all/brunch/blog/instagram/linkedin)"),
    count: int = typer.Option(5, "--count", "-n", help="추천 주제 수"),
):
    """콘텐츠 주제를 추천받습니다."""
    print_header()
    agent = get_agent()

    console.print(f"\n[bold]{niche}[/] 분야의 콘텐츠 주제 {count}개를 추천받습니다...\n")

    message = (
        f"suggest_topics 도구를 사용해서 주제를 추천해주세요.\n"
        f"- 분야: {niche}\n"
        f"- 플랫폼: {platform}\n"
        f"- 개수: {count}\n\n"
        f"각 주제에 대해 제목, 핵심 포인트, 예상 반응을 포함해서 마크다운 형식으로 정리해주세요."
    )

    with console.status("[dim]주제 추천 중...[/]", spinner="dots"):
        response = agent.chat(message)

    console.print(Panel(Markdown(response), title="[bold]추천 주제[/]", border_style="bright_yellow"))


@app.command()
def drafts(
    platform: str = typer.Option("all", "--platform", "-p", help="플랫폼 필터"),
):
    """저장된 초안 목록을 확인합니다."""
    from agent.tools import _list_drafts
    import json

    result = json.loads(_list_drafts(platform))

    if result["status"] == "empty":
        console.print(Panel("[dim]저장된 초안이 없습니다.[/]", title="초안 목록"))
        return

    table = Table(title="저장된 초안 목록", box=box.ROUNDED)
    table.add_column("플랫폼", style="bold", min_width=12)
    table.add_column("파일명", min_width=30)
    table.add_column("크기", justify="right")
    table.add_column("수정일", min_width=16)

    for draft in result["drafts"]:
        emoji = PLATFORM_EMOJIS.get(draft["platform"], "")
        color = PLATFORM_COLORS.get(draft["platform"], "white")
        table.add_row(
            f"[{color}]{emoji} {draft['platform']}[/]",
            draft["filename"],
            f"{draft['size']:,}B",
            draft["modified"],
        )

    console.print(table)
    console.print(f"\n[dim]총 {result['count']}개의 초안[/]")


if __name__ == "__main__":
    app()

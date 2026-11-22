#!/usr/bin/env python3
"""
短剧 MCP Server（供支持 MCP 的 DeepSeek Bot / Grok Bot / Claude Code 直接调用）
启动方式：python tools/mcp_server.py
"""
import subprocess
from fastmcp import FastMCP
from providers import generate_image, generate_video

mcp = FastMCP("short-drama-tools")

@mcp.tool()
def tool_generate_image(prompt: str, output_path: str, ratio: str = "9:16", ref_image: str = None, provider: str = None) -> dict:
    """生成角色三视图、场景基准图或镜头首尾帧。支持 mock/jimeng/kling/bailian/local。"""
    return generate_image(prompt, output_path, ratio=ratio, ref_image=ref_image, provider=provider)

@mcp.tool()
def tool_generate_video(prompt: str, output_path: str, first_frame: str = None, duration: float = 2.0, provider: str = None) -> dict:
    """生成 1-3 秒单镜视频（无BGM）。支持 mock/jimeng/kling/bailian/local。"""
    return generate_video(prompt, output_path, first_frame=first_frame, duration=duration, provider=provider)

@mcp.tool()
def tool_render_cut(clips: list[str], output_path: str, voice: str = None, bgm: str = None, srt: str = None) -> dict:
    """使用 FFmpeg 将多个单镜视频按顺序拼接，并可选叠加独白、压低音量的 BGM 与 SRT 字幕。"""
    cmd = ["python", "tools/render_cut.py", "--clips", *clips, "--out", output_path]
    if voice:
        cmd.extend(["--voice", voice])
    if bgm:
        cmd.extend(["--bgm", bgm])
    if srt:
        cmd.extend(["--srt", srt])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {"status": "error", "stderr": res.stderr}
    return {"status": "ok", "output": output_path, "stdout": res.stdout}

if __name__ == "__main__":
    mcp.run()

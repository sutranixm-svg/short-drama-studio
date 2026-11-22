#!/usr/bin/env python3
"""粗剪合成：拼接单镜视频，混入独白 / BGM，可选烧字幕。

适配要点：
- 单镜视频可能没有音轨（即梦 / 可灵 / 百炼产出的 mp4 常见），此处用 ffprobe 探测后
  自动补一条等长静音底座，避免 amix 引用 [0:a] 直接失败。
- 字幕统一走 filter_complex，不与 -vf 混用，避免滤镜图冲突。
"""
import argparse
import json
import os
import subprocess
import tempfile


def run(cmd: list, what: str = "FFmpeg"):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"{what} 执行失败:\n{res.stderr}")
    return res


def probe(path: str, entries: str, select: str = None) -> str:
    cmd = ["ffprobe", "-v", "error"]
    if select:
        cmd += ["-select_streams", select]
    cmd += ["-show_entries", entries, "-of", "csv=p=0", path]
    return run(cmd, "ffprobe").stdout.strip()


def has_audio(path: str) -> bool:
    try:
        return bool(probe(path, "stream=index", "a"))
    except RuntimeError:
        return False


def media_duration(path: str) -> float:
    try:
        return float(probe(path, "format=duration").splitlines()[0])
    except Exception:
        return 0.0


def escape_filter_path(path: str) -> str:
    """把路径转成可在滤镜参数里安全使用的形式（Windows 反斜杠与盘符冒号）。"""
    return path.replace("\\", "/").replace(":", "\\:")


def video_size(path: str, default=(720, 1280)) -> tuple:
    try:
        out = probe(path, "stream=width,height", "v").splitlines()[0]
        w, h = out.split(",")[:2]
        return int(w), int(h)
    except Exception:
        return default


def normalize(src: str, dst: str, size: tuple, fps: int = 25) -> bool:
    """把单镜统一成同一规格：分辨率/帧率/sar 一致，且必定带一条音轨。

    concat -c copy 要求所有输入的流结构一致；混用「有音轨」与「无音轨」的片段时
    直接拼接会丢流或截断，所以先逐段规范化。返回是否额外补了静音。
    """
    w, h = size
    vf = (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}"
    )
    enc = ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-ar", "44100", "-ac", "2"]
    if has_audio(src):
        run(["ffmpeg", "-y", "-i", src, "-vf", vf, *enc, dst])
        return False
    run([
        "ffmpeg", "-y", "-i", src,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-vf", vf, "-shortest", *enc, dst,
    ])
    return True


def main():
    parser = argparse.ArgumentParser(
        description="短剧 - FFmpeg 自动粗剪合成工具（拼接多镜+叠加独白/BGM+字幕；自动适配无音轨片段）"
    )
    parser.add_argument("--clips", nargs="+", required=True, help="按顺序排列的单镜视频路径列表")
    parser.add_argument("--out", required=True, help="最终成片输出路径，如 workspace/ep01/final_cut.mp4")
    parser.add_argument("--voice", default=None, help="可选：独立连续独白/对白音轨路径")
    parser.add_argument("--bgm", default=None, help="可选：后期纯音乐 BGM 路径（自动压低音量防盖住人声）")
    parser.add_argument("--srt", default=None, help="可选：SRT 字幕文件路径")
    parser.add_argument("--keep-silent-track", action="store_true",
                        help="片段无音轨且未提供 voice/bgm 时，仍补一条静音音轨（默认已补）")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    for c in args.clips:
        if not os.path.exists(c):
            raise SystemExit(f"片段不存在: {c}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 先逐段规范化：统一分辨率/帧率，缺音轨的补静音（否则 concat -c copy 会丢流）
        notes = []
        target = video_size(args.clips[0])
        normalized = []
        for i, c in enumerate(args.clips):
            n = os.path.join(tmpdir, f"norm_{i}.mp4")
            padded = normalize(c, n, target)
            normalized.append(n)
            if padded:
                notes.append(f"片段 {i + 1} 无音轨，已补静音底座")

        concat_list = os.path.join(tmpdir, "list.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            for c in normalized:
                f.write(f"file '{os.path.abspath(c)}'\n")

        stitched = os.path.join(tmpdir, "stitched.mp4")
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", stitched])

        base_has_audio = has_audio(stitched)
        total = media_duration(stitched)

        cmd = ["ffmpeg", "-y", "-i", stitched]
        inputs_count = 1
        filter_parts = []
        audio_streams = []

        if base_has_audio:
            audio_streams.append("[0:a]")
        else:
            # 源片段无音轨：补等长静音底座，保证后续 amix / 交付规格一致
            silence = "anullsrc=channel_layout=stereo:sample_rate=44100"
            if total > 0:
                silence += f":d={total:.3f}"
            cmd.extend(["-f", "lavfi", "-i", silence])
            audio_streams.append(f"[{inputs_count}:a]")
            inputs_count += 1
            notes.append("片源无音轨，已自动补静音底座")

        if args.voice:
            cmd.extend(["-i", args.voice])
            audio_streams.append(f"[{inputs_count}:a]")
            inputs_count += 1

        if args.bgm:
            cmd.extend(["-i", args.bgm])
            filter_parts.append(f"[{inputs_count}:a]volume=0.25[bgm_low]")
            audio_streams.append("[bgm_low]")
            inputs_count += 1
            notes.append("BGM 已压至 0.25，保证人声优先")

        if len(audio_streams) > 1:
            mix_in = "".join(audio_streams)
            filter_parts.append(
                f"{mix_in}amix=inputs={len(audio_streams)}:duration=first:dropout_transition=2[aout]"
            )
            audio_label = "[aout]"
        else:
            # 单条音频流：直接映射输入流索引，不能带方括号（方括号是 filtergraph 输出标签语法）
            audio_label = audio_streams[0].strip("[]")

        if args.srt:
            if not os.path.exists(args.srt):
                raise SystemExit(f"字幕文件不存在: {args.srt}")
            filter_parts.append(f"[0:v]subtitles='{escape_filter_path(args.srt)}'[vout]")
            video_label = "[vout]"
        else:
            video_label = "0:v"

        if filter_parts:
            cmd.extend(["-filter_complex", ";".join(filter_parts)])

        cmd.extend(["-map", video_label, "-map", audio_label])
        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", args.out])
        run(cmd)

    print(json.dumps({
        "status": "ok",
        "clips_count": len(args.clips),
        "base_has_audio": base_has_audio,
        "duration": round(media_duration(args.out), 3),
        "notes": notes,
        "output": args.out,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

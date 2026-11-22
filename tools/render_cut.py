#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import tempfile

def run_ffmpeg(cmd: list):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg 渲染失败:\n{res.stderr}")

def main():
    parser = argparse.ArgumentParser(description="短剧 - FFmpeg 自动粗剪合成工具（拼接多镜+叠加独白/BGM+字幕）")
    parser.add_argument("--clips", nargs="+", required=True, help="按顺序排列的单镜视频路径列表")
    parser.add_argument("--out", required=True, help="最终成片输出路径，如 workspace/ep01/final_cut.mp4")
    parser.add_argument("--voice", default=None, help="可选：独立连续独白/对白音轨路径")
    parser.add_argument("--bgm", default=None, help="可选：后期纯音乐 BGM 路径（自动压低音量防盖住人声）")
    parser.add_argument("--srt", default=None, help="可选：SRT 字幕文件路径")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        concat_list = os.path.join(tmpdir, "list.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            for c in args.clips:
                f.write(f"file '{os.path.abspath(c)}'\n")

        stitched = os.path.join(tmpdir, "stitched.mp4")
        run_ffmpeg(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", stitched])

        cmd = ["ffmpeg", "-y", "-i", stitched]
        inputs_count = 1
        filter_parts = []
        audio_streams = ["[0:a]"]

        if args.voice:
            cmd.extend(["-i", args.voice])
            audio_streams.append(f"[{inputs_count}:a]")
            inputs_count += 1

        if args.bgm:
            cmd.extend(["-i", args.bgm])
            # BGM 自动压低至 0.25 音量，保证人声优先
            filter_parts.append(f"[{inputs_count}:a]volume=0.25[bgm_low]")
            audio_streams.append("[bgm_low]")
            inputs_count += 1

        if len(audio_streams) > 1:
            mix_in = "".join(audio_streams)
            filter_parts.append(f"{mix_in}amix=inputs={len(audio_streams)}:duration=first:dropout_transition=2[aout]")

        vf = f"subtitles={args.srt}" if args.srt else None
        if filter_parts:
            cmd.extend(["-filter_complex", ";".join(filter_parts)])
            cmd.extend(["-map", "0:v", "-map", "[aout]"])
        if vf:
            cmd.extend(["-vf", vf])

        cmd.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", args.out])
        run_ffmpeg(cmd)

    print(json.dumps({"status": "ok", "clips_count": len(args.clips), "output": args.out}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import json
from providers import generate_video

def main():
    parser = argparse.ArgumentParser(description="短剧 - 统一图生视频工具（单镜 1-3 秒，无BGM）")
    parser.add_argument("--prompt", required=True, help="单镜运动与运镜提示词")
    parser.add_argument("--out", required=True, help="输出视频路径，如 workspace/ep01/shot_01.mp4")
    parser.add_argument("--first-frame", default=None, help="首帧图片路径或URL")
    parser.add_argument("--duration", type=float, default=2.0, help="成片目标时长（1.0-3.0秒）")
    parser.add_argument("--provider", default=None, help="覆盖 .env 中的 VIDEO_PROVIDER（mock/jimeng/kling/bailian/local）")
    args = parser.parse_args()

    res = generate_video(args.prompt, args.out, first_frame=args.first_frame, duration=args.duration, provider=args.provider)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

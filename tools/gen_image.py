#!/usr/bin/env python3
import argparse
import json
from providers import generate_image

def main():
    parser = argparse.ArgumentParser(description="短剧 - 统一生图工具（支持即梦/可灵/百炼/本地/mock）")
    parser.add_argument("--prompt", required=True, help="图片生成提示词")
    parser.add_argument("--out", required=True, help="输出图片路径，如 workspace/ep01/shot_01.png")
    parser.add_argument("--ratio", default="9:16", help="画幅比例，默认 9:16")
    parser.add_argument("--ref", default=None, help="参考图路径或URL")
    parser.add_argument("--provider", default=None, help="覆盖 .env 中的 IMAGE_PROVIDER（mock/jimeng/kling/bailian/local）")
    args = parser.parse_args()

    res = generate_image(args.prompt, args.out, ratio=args.ratio, ref_image=args.ref, provider=args.provider)
    print(json.dumps(res, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

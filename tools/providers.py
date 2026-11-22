import os
import time
import subprocess
import requests

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # 未安装 python-dotenv 时回退到系统环境变量，mock 模式仍可用
    pass


def _run_ffmpeg(cmd: list):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg 执行失败:\n{res.stderr}")


def generate_image(prompt: str, output_path: str, ratio: str = "9:16", ref_image: str = None, provider: str = None):
    """统一生图入口：支持 mock / bailian / kling / jimeng / local"""
    provider = (provider or os.getenv("IMAGE_PROVIDER", "mock")).lower()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    if provider == "mock":
        size = "720x1280" if ratio == "9:16" else "1280x720"
        _run_ffmpeg([
            "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x1e293b:s={size}",
            "-frames:v", "1", output_path
        ])
        return {"status": "ok", "provider": "mock", "output": output_path, "note": "干跑占位图已生成"}

    elif provider == "bailian":
        api_key = os.getenv("BAILIAN_API_KEY")
        model = os.getenv("BAILIAN_IMAGE_MODEL", "wanx2.1-t2i-turbo")
        if not api_key:
            raise ValueError("缺少 BAILIAN_API_KEY，请在 .env 中配置")
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        headers = {"Authorization": f"Bearer {api_key}", "X-DashScope-Async": "enable", "Content-Type": "application/json"}
        size = "720*1280" if ratio == "9:16" else "1280*720"
        payload = {"model": model, "input": {"prompt": prompt}, "parameters": {"size": size, "n": 1}}
        resp = requests.post(url, headers=headers, json=payload, timeout=30).json()
        task_id = resp.get("output", {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"百炼生图提交失败: {resp}")
        # 轮询结果
        poll_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        for _ in range(60):
            time.sleep(3)
            r = requests.get(poll_url, headers={"Authorization": f"Bearer {api_key}"}, timeout=15).json()
            status = r.get("output", {}).get("task_status")
            if status == "SUCCEEDED":
                img_url = r["output"]["results"][0]["url"]
                with open(output_path, "wb") as f:
                    f.write(requests.get(img_url, timeout=30).content)
                return {"status": "ok", "provider": "bailian", "output": output_path}
            elif status in ("FAILED", "CANCELED"):
                raise RuntimeError(f"百炼生图失败: {r}")
        raise TimeoutError("百炼生图轮询超时")

    elif provider == "kling":
        ak = os.getenv("KLING_ACCESS_KEY")
        base = os.getenv("KLING_API_BASE", "https://api.klingai.com")
        if not ak:
            raise ValueError("缺少 KLING_ACCESS_KEY，请在 .env 中配置")
        # 标准可灵接口占位（不同代理/官方JWT鉴权可在此微调）
        headers = {"Authorization": f"Bearer {ak}", "Content-Type": "application/json"}
        payload = {"prompt": prompt, "aspect_ratio": ratio}
        if ref_image:
            payload["image"] = ref_image
        r = requests.post(f"{base}/v1/images/generations", headers=headers, json=payload, timeout=60).json()
        return {"status": "submitted", "provider": "kling", "raw_response": r, "output": output_path}

    elif provider == "jimeng":
        api_key = os.getenv("JIMENG_API_KEY")
        base = os.getenv("JIMENG_API_BASE", "https://visual.volcengineapi.com")
        model = os.getenv("JIMENG_IMAGE_MODEL", "jimeng_high_aes_general_v21")
        if not api_key:
            raise ValueError("缺少 JIMENG_API_KEY，请在 .env 中配置")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "prompt": prompt, "aspect_ratio": ratio}
        r = requests.post(f"{base}/v1/images/generations", headers=headers, json=payload, timeout=60).json()
        return {"status": "submitted", "provider": "jimeng", "raw_response": r, "output": output_path}

    elif provider == "local":
        endpoint = os.getenv("LOCAL_IMAGE_ENDPOINT", "http://127.0.0.1:8188/api/generate_image")
        token = os.getenv("LOCAL_API_TOKEN", "")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        payload = {"prompt": prompt, "ratio": ratio, "ref_image": ref_image}
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=180)
        resp.raise_for_status()
        if resp.headers.get("Content-Type", "").startswith("image/"):
            with open(output_path, "wb") as f:
                f.write(resp.content)
            return {"status": "ok", "provider": "local", "output": output_path}
        return {"status": "ok", "provider": "local", "raw_response": resp.json(), "output": output_path}

    else:
        raise ValueError(f"不支持的 IMAGE_PROVIDER: {provider}")


def generate_video(prompt: str, output_path: str, first_frame: str = None, duration: float = 2.0, provider: str = None):
    """统一生视频入口：支持 mock / bailian / kling / jimeng / local（无BGM）"""
    provider = (provider or os.getenv("VIDEO_PROVIDER", "mock")).lower()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    duration = max(1.0, min(3.0, float(duration)))  # 硬约束：单镜 1-3 秒

    if provider == "mock":
        if first_frame and os.path.exists(first_frame):
            _run_ffmpeg([
                "ffmpeg", "-y", "-loop", "1", "-i", first_frame,
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-t", str(duration), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                output_path
            ])
        else:
            _run_ffmpeg([
                "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0x0f172a:s=720x1280:d={duration}",
                "-f", "lavfi", "-i", f"anullsrc=channel_layout=stereo:sample_rate=44100:d={duration}",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest",
                output_path
            ])
        return {"status": "ok", "provider": "mock", "duration": duration, "output": output_path, "note": "干跑占位视频已生成（无BGM）"}

    elif provider == "bailian":
        api_key = os.getenv("BAILIAN_API_KEY")
        model = os.getenv("BAILIAN_VIDEO_MODEL", "wanx2.1-i2v-turbo")
        if not api_key:
            raise ValueError("缺少 BAILIAN_API_KEY，请在 .env 中配置")
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
        headers = {"Authorization": f"Bearer {api_key}", "X-DashScope-Async": "enable", "Content-Type": "application/json"}
        payload = {"model": model, "input": {"prompt": prompt, "img_url": first_frame}}
        resp = requests.post(url, headers=headers, json=payload, timeout=30).json()
        return {"status": "submitted", "provider": "bailian", "raw_response": resp, "output": output_path}

    elif provider == "kling":
        ak = os.getenv("KLING_ACCESS_KEY")
        base = os.getenv("KLING_API_BASE", "https://api.klingai.com")
        if not ak:
            raise ValueError("缺少 KLING_ACCESS_KEY，请在 .env 中配置")
        headers = {"Authorization": f"Bearer {ak}", "Content-Type": "application/json"}
        payload = {"prompt": prompt, "image": first_frame, "duration": "5"}
        r = requests.post(f"{base}/v1/videos/image2video", headers=headers, json=payload, timeout=60).json()
        return {"status": "submitted", "provider": "kling", "raw_response": r, "output": output_path}

    elif provider == "jimeng":
        api_key = os.getenv("JIMENG_API_KEY")
        base = os.getenv("JIMENG_API_BASE", "https://visual.volcengineapi.com")
        model = os.getenv("JIMENG_VIDEO_MODEL", "jimeng_i2v_v1")
        if not api_key:
            raise ValueError("缺少 JIMENG_API_KEY，请在 .env 中配置")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "prompt": prompt, "image_url": first_frame}
        r = requests.post(f"{base}/v1/videos/generations", headers=headers, json=payload, timeout=60).json()
        return {"status": "submitted", "provider": "jimeng", "raw_response": r, "output": output_path}

    elif provider == "local":
        endpoint = os.getenv("LOCAL_VIDEO_ENDPOINT", "http://127.0.0.1:8188/api/generate_video")
        token = os.getenv("LOCAL_API_TOKEN", "")
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        payload = {"prompt": prompt, "first_frame": first_frame, "duration": duration}
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=300)
        resp.raise_for_status()
        if resp.headers.get("Content-Type", "").startswith("video/"):
            with open(output_path, "wb") as f:
                f.write(resp.content)
            return {"status": "ok", "provider": "local", "output": output_path}
        return {"status": "ok", "provider": "local", "raw_response": resp.json(), "output": output_path}

    else:
        raise ValueError(f"不支持的 VIDEO_PROVIDER: {provider}")

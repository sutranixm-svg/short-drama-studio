"""统一生成后端：mock / bailian / kling / jimeng / local。

异步后端（bailian / kling / jimeng）统一走「提交 → 轮询 → 下载产物」三段式，
失败时把平台原始响应带进异常信息，便于定位鉴权、参数还是配额问题。
"""
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


def _download(url: str, output_path: str) -> str:
    if not url:
        raise RuntimeError("平台未返回产物 URL")
    r = requests.get(url, timeout=180, stream=True)
    r.raise_for_status()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1 << 16):
            f.write(chunk)
    if os.path.getsize(output_path) == 0:
        raise RuntimeError(f"下载到空文件: {url}")
    return output_path


def _poll(fetch, done, fail, interval=3, max_tries=100, label="任务"):
    """异步任务轮询：每 interval 秒取一次快照，直到 done 为真或 fail 触发。"""
    last = None
    for _ in range(max_tries):
        time.sleep(interval)
        last = fetch()
        if fail(last):
            raise RuntimeError(f"{label}失败: {last}")
        if done(last):
            return last
    raise TimeoutError(f"{label}轮询超时（{max_tries * interval}s），最后响应: {last}")


def _kling_jwt(ak: str, sk: str, ttl: int = 1800) -> str:
    """可灵用 AK/SK 签 HS256 JWT 作 Bearer；直接把 AK 当 token 会被拒。"""
    import base64
    import hashlib
    import hmac
    import json as _json

    def b64(raw: bytes) -> bytes:
        return base64.urlsafe_b64encode(raw).rstrip(b"=")

    now = int(time.time())
    header = b64(_json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = b64(_json.dumps({"iss": ak, "exp": now + ttl, "nbf": now - 5}).encode())
    signing = header + b"." + payload
    sig = b64(hmac.new(sk.encode(), signing, hashlib.sha256).digest())
    return (signing + b"." + sig).decode()


def _volc_headers(ak: str, sk: str, action: str, version: str, body_bytes: bytes,
                  host: str, region: str = "cn-north-1", service: str = "cv") -> dict:
    """火山引擎视觉 API 的 HMAC-SHA256 签名头（该 API 不接受 Bearer token）。"""
    import hashlib
    import hmac

    xdate = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    short = xdate[:8]
    payload_hash = hashlib.sha256(body_bytes).hexdigest()
    query = f"Action={action}&Version={version}"
    signed = "content-type;host;x-content-sha256;x-date"
    canon_headers = (
        f"content-type:application/json\nhost:{host}\n"
        f"x-content-sha256:{payload_hash}\nx-date:{xdate}\n"
    )
    canon_req = f"POST\n/\n{query}\n{canon_headers}\n{signed}\n{payload_hash}"
    scope = f"{short}/{region}/{service}/request"
    sts = f"HMAC-SHA256\n{xdate}\n{scope}\n{hashlib.sha256(canon_req.encode()).hexdigest()}"
    k = hmac.new(sk.encode(), short.encode(), hashlib.sha256).digest()
    k = hmac.new(k, region.encode(), hashlib.sha256).digest()
    k = hmac.new(k, service.encode(), hashlib.sha256).digest()
    k = hmac.new(k, b"request", hashlib.sha256).digest()
    sig = hmac.new(k, sts.encode(), hashlib.sha256).hexdigest()
    return {
        "Content-Type": "application/json",
        "X-Date": xdate,
        "X-Content-Sha256": payload_hash,
        "Authorization": f"HMAC-SHA256 Credential={ak}/{scope}, SignedHeaders={signed}, Signature={sig}",
    }


def _bailian_base() -> str:
    return os.getenv("BAILIAN_API_BASE", "https://dashscope.aliyuncs.com/api/v1")


def _bailian_async(url: str, headers: dict, payload: dict, output_path: str,
                   provider: str, label: str, pick_url) -> dict:
    """百炼异步任务：提交拿 task_id，轮询 /tasks/{id} 到 SUCCEEDED，再下载产物。"""
    headers = dict(headers, **{"X-DashScope-Async": "enable"})
    submit = requests.post(url, headers=headers, json=payload, timeout=30).json()
    task_id = (submit.get("output") or {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"{label}提交失败: {submit}")
    poll = f"{_bailian_base()}/tasks/{task_id}"
    data = _poll(
        lambda: requests.get(poll, headers={"Authorization": headers["Authorization"]}, timeout=20).json(),
        done=lambda d: (d.get("output") or {}).get("task_status") == "SUCCEEDED",
        fail=lambda d: (d.get("output") or {}).get("task_status") in ("FAILED", "CANCELED", "UNKNOWN"),
        interval=3, max_tries=100, label=label,
    )
    url_out = pick_url(data)
    _download(url_out, output_path)
    return {"status": "ok", "provider": provider, "task_id": task_id,
            "remote_url": url_out, "output": output_path}


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
        size = "720*1280" if ratio == "9:16" else "1280*720"
        return _bailian_async(
            f"{_bailian_base()}/services/aigc/text2image/image-synthesis",
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            {"model": model, "input": {"prompt": prompt}, "parameters": {"size": size, "n": 1}},
            output_path, "bailian", "百炼生图",
            pick_url=lambda d: (d["output"].get("results") or [{}])[0].get("url")
            or d["output"].get("image_url"),
        )

    elif provider == "kling":
        ak, sk = os.getenv("KLING_ACCESS_KEY"), os.getenv("KLING_SECRET_KEY")
        base = os.getenv("KLING_API_BASE", "https://api.klingai.com")
        if not ak or not sk:
            raise ValueError("缺少 KLING_ACCESS_KEY / KLING_SECRET_KEY，请在 .env 中配置")
        headers = {"Authorization": f"Bearer {_kling_jwt(ak, sk)}", "Content-Type": "application/json"}
        body = {"model_name": os.getenv("KLING_IMAGE_MODEL", "kling-v1"),
                "prompt": prompt, "aspect_ratio": ratio, "n": 1}
        if ref_image:
            body["image"] = ref_image
        submit = requests.post(f"{base}/v1/images/generations", headers=headers, json=body, timeout=60).json()
        task_id = (submit.get("data") or {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"可灵生图提交失败: {submit}")
        fetch_url = f"{base}/v1/images/generations/{task_id}"
        data = _poll(lambda: requests.get(fetch_url, headers=headers, timeout=30).json(),
                     done=lambda d: (d.get("data") or {}).get("task_status") == "succeed",
                     fail=lambda d: (d.get("data") or {}).get("task_status") in ("failed",),
                     interval=5, max_tries=60, label="可灵生图")
        images = ((data.get("data") or {}).get("task_result") or {}).get("images") or []
        if not images:
            raise RuntimeError(f"可灵未返回图片: {data}")
        _download(images[0].get("url"), output_path)
        return {"status": "ok", "provider": "kling", "task_id": task_id, "output": output_path}

    elif provider == "jimeng":
        return _jimeng_call("image", prompt, output_path, ratio=ratio, first_frame=ref_image)

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
        if not first_frame:
            raise ValueError("百炼图生视频需要 --first-frame")
        return _bailian_async(
            f"{_bailian_base()}/services/aigc/video-generation/video-synthesis",
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            {"model": model, "input": {"prompt": prompt, "img_url": first_frame},
             "parameters": {"duration": int(round(duration))}},
            output_path, "bailian", "百炼生视频",
            pick_url=lambda d: d["output"].get("video_url")
            or (d["output"].get("results") or [{}])[0].get("url"),
        )

    elif provider == "kling":
        ak, sk = os.getenv("KLING_ACCESS_KEY"), os.getenv("KLING_SECRET_KEY")
        base = os.getenv("KLING_API_BASE", "https://api.klingai.com")
        if not ak or not sk:
            raise ValueError("缺少 KLING_ACCESS_KEY / KLING_SECRET_KEY，请在 .env 中配置")
        if not first_frame:
            raise ValueError("可灵图生视频需要 --first-frame")
        headers = {"Authorization": f"Bearer {_kling_jwt(ak, sk)}", "Content-Type": "application/json"}
        body = {"model_name": os.getenv("KLING_VIDEO_MODEL", "kling-v1"),
                "prompt": prompt, "image": first_frame,
                "duration": str(int(round(duration))), "mode": "std"}
        submit = requests.post(f"{base}/v1/videos/image2video", headers=headers, json=body, timeout=60).json()
        task_id = (submit.get("data") or {}).get("task_id")
        if not task_id:
            raise RuntimeError(f"可灵生视频提交失败: {submit}")
        fetch_url = f"{base}/v1/videos/image2video/{task_id}"
        data = _poll(lambda: requests.get(fetch_url, headers=headers, timeout=30).json(),
                     done=lambda d: (d.get("data") or {}).get("task_status") == "succeed",
                     fail=lambda d: (d.get("data") or {}).get("task_status") in ("failed",),
                     interval=5, max_tries=60, label="可灵生视频")
        videos = ((data.get("data") or {}).get("task_result") or {}).get("videos") or []
        if not videos:
            raise RuntimeError(f"可灵未返回视频: {data}")
        _download(videos[0].get("url"), output_path)
        return {"status": "ok", "provider": "kling", "task_id": task_id, "output": output_path}

    elif provider == "jimeng":
        if not first_frame:
            raise ValueError("即梦图生视频需要 --first-frame")
        return _jimeng_call("video", prompt, output_path, ratio=None,
                            first_frame=first_frame, duration=duration)

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


def _jimeng_call(kind: str, prompt: str, output_path: str, ratio: str = None,
                 first_frame: str = None, duration: float = None) -> dict:
    """火山引擎视觉 API：提交 → 轮询 → 下载。

    鉴权二选一：
    - JIMENG_ACCESS_KEY + JIMENG_SECRET_KEY → 官方 HMAC-SHA256 签名（推荐）
    - 仅 JIMENG_API_KEY → Bearer 直连，用于自建中转/代理

    req_key 与返回里的产物字段以官方文档为准，均可用环境变量覆盖；
    换模型或换版本时只改 .env，不必改代码。
    """
    import json as _json

    base = os.getenv("JIMENG_API_BASE", "https://visual.volcengineapi.com").rstrip("/")
    host = base.split("://", 1)[-1].split("/")[0]
    req_key = os.getenv("JIMENG_VIDEO_REQ_KEY" if kind == "video" else "JIMENG_IMAGE_REQ_KEY",
                        os.getenv("JIMENG_IMAGE_MODEL", "jimeng_high_aes_general_v21"))
    version = os.getenv("JIMENG_API_VERSION", "2022-08-31")
    ak, sk = os.getenv("JIMENG_ACCESS_KEY"), os.getenv("JIMENG_SECRET_KEY")
    api_key = os.getenv("JIMENG_API_KEY")

    body = {"req_key": req_key, "prompt": prompt}
    if kind == "image":
        if ratio:
            body["aspect_ratio"] = ratio
        if first_frame:
            body["image_urls"] = [first_frame]
    else:
        body["image_urls"] = [first_frame]
        body["frames"] = int(round((duration or 2.0) * 24))

    raw = _json.dumps(body, ensure_ascii=False).encode()
    if ak and sk:
        headers = _volc_headers(ak, sk, "CVSync2AsyncSubmitTask", version, raw, host)
    elif api_key:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    else:
        raise ValueError("缺少 JIMENG_ACCESS_KEY/JIMENG_SECRET_KEY 或 JIMENG_API_KEY")

    submit = requests.post(f"{base}/?Action=CVSync2AsyncSubmitTask&Version={version}",
                           headers=headers, data=raw, timeout=60).json()
    task_id = (submit.get("data") or {}).get("task_id")
    if not task_id:
        raise RuntimeError(f"即梦提交失败（检查 req_key 与签名）: {submit}")

    qbody = {"req_key": req_key, "task_id": task_id}
    qraw = _json.dumps(qbody, ensure_ascii=False).encode()
    qheaders = (_volc_headers(ak, sk, "CVSync2AsyncGetResult", version, qraw, host)
                if ak and sk else {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})

    def fetch():
        return requests.post(f"{base}/?Action=CVSync2AsyncGetResult&Version={version}",
                             headers=qheaders, data=qraw, timeout=30).json()

    def _status(d):
        return str((d.get("data") or {}).get("status", "")).lower()

    data = _poll(fetch,
                 done=lambda d: _status(d) in ("done", "succeeded", "success"),
                 fail=lambda d: _status(d) in ("failed", "error", "not_found"),
                 interval=5, max_tries=60, label="即梦生成")
    out = data.get("data") or {}
    url = out.get("video_url") or out.get("image_url")
    if not url:
        for key in ("image_urls", "video_urls"):
            if out.get(key):
                url = out[key][0]
                break
    if not url:
        import base64

        b64 = out.get("binary_data_base64")
        if b64:
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(b64[0] if isinstance(b64, list) else b64))
            return {"status": "ok", "provider": "jimeng", "task_id": task_id,
                    "output": output_path, "note": "产物来自 binary_data_base64"}
        raise RuntimeError(f"即梦未返回可用产物（检查返回字段名）: {out}")
    _download(url, output_path)
    return {"status": "ok", "provider": "jimeng", "task_id": task_id,
            "remote_url": url, "output": output_path}

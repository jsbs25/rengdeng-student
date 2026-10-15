# -*- coding: utf-8 -*-
"""AI 阿拉伯音乐生成（MusicGen-small 本地推理，MPS 加速）"""
import os, time, threading, wave
os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
import numpy as np

_MODEL = None
_PROC = None
_LOCK = threading.Lock()
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'music_out')
_MODEL_DIR = '/Users/mafucheng/Desktop/arabic-learning/models_musicgen'
if not os.path.isdir(_MODEL_DIR):
    _MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models_musicgen')
os.makedirs(OUT_DIR, exist_ok=True)
SR = 32000  # MusicGen 采样率

def _load():
    global _MODEL, _PROC
    if _MODEL is None:
        import torch
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
        _PROC = AutoProcessor.from_pretrained(_MODEL_DIR)
        _MODEL = MusicgenForConditionalGeneration.from_pretrained(_MODEL_DIR, low_cpu_mem_usage=True)
        if torch.backends.mps.is_available():
            _MODEL.to('mps')
            try:
                # 半精度：MPS 上 fp16 显著加速（约 2-3 倍）
                _MODEL = _MODEL.to(dtype=torch.float16)
            except Exception:
                pass
        print(f'[music] 模型就绪: {_MODEL.device}', flush=True)

def status():
    return _MODEL is not None

def _save_wav(path, audio):
    audio = (audio * 32767).clip(-32768, 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(audio.tobytes())

def gen(prompt, seconds=12):
    """生成音乐，返回 (文件名, 时长秒)"""
    t0 = time.time()
    _load()
    import torch
    with _LOCK:
        inputs = _PROC(text=[prompt], padding=True, return_tensors='pt')
        if torch.backends.mps.is_available():
            inputs = {k: v.to('mps') for k, v in inputs.items()}
            try:
                inputs = {k: v.to(dtype=torch.float16) if v.dtype == torch.float32 else v for k, v in inputs.items()}
            except Exception:
                pass
        max_new = int(seconds * 50)  # ~50 tokens/秒
        audio = _MODEL.generate(**inputs, max_new_tokens=max_new)
        wav = audio[0].cpu().numpy()
        if wav.ndim == 2:
            wav = wav[0]  # [1, T] -> [T]
    name = f'music_{int(time.time())}.wav'
    path = os.path.join(OUT_DIR, name)
    _save_wav(path, wav)
    dur = round(wav.shape[0] / SR, 1)
    print(f'[music] 生成完成: {name} 时长{dur}s 耗时{int(time.time()-t0)}s', flush=True)
    return name, dur

def gen_long(prompt, seconds=120, seg=30):
    """生成长音频（MusicGen 单次上限约30秒）：分段 generate_continuation 续写拼接"""
    import math, torch
    t0 = time.time()
    _load()
    with _LOCK:
        inputs = _PROC(text=[prompt], padding=True, return_tensors='pt')
        if torch.backends.mps.is_available():
            inputs = {k: v.to('mps') for k, v in inputs.items()}
        seg_tokens = int(seg * 50)
        n_seg = max(1, math.ceil(seconds / seg))
        audio = None
        for i in range(n_seg):
            if audio is None:
                audio = _MODEL.generate(**inputs, max_new_tokens=seg_tokens)
            else:
                # transformers 新版：generate(input_values=前段音频) 续写
                audio = _MODEL.generate(input_values=audio, **inputs, max_new_tokens=seg_tokens)
            print(f'[music] 段 {i+1}/{n_seg} 完成 ({int(time.time()-t0)}s)', flush=True)
        wav = audio[0].cpu().numpy()
        if wav.ndim == 2:
            wav = wav[0]
    name = f'song_{int(time.time())}.wav'
    path = os.path.join(OUT_DIR, name)
    _save_wav(path, wav)
    dur = round(wav.shape[0] / SR, 1)
    print(f'[music] 长曲完成: {name} {dur}s 总耗时{int(time.time()-t0)}s', flush=True)
    return name, dur

# ===== 完整歌曲：2 进程并行生成 + 交叉淡化拼接 =====
import multiprocessing as mp

def _song_worker(prompt, seconds, seed, out_path):
    """子进程：加载模型生成一段（continuation 续写保持连贯）"""
    import math as _m
    os.environ.setdefault('HF_HUB_OFFLINE', '1')
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    proc = AutoProcessor.from_pretrained(_MODEL_DIR)
    model = MusicgenForConditionalGeneration.from_pretrained(_MODEL_DIR, low_cpu_mem_usage=True)
    if torch.backends.mps.is_available():
        model = model.to('mps').to(dtype=torch.float16)
    torch.manual_seed(seed)
    inputs = proc(text=[prompt], padding=True, return_tensors='pt')
    if torch.backends.mps.is_available():
        inputs = {k: v.to('mps') for k, v in inputs.items()}
        inputs = {k: v.to(dtype=torch.float16) if v.dtype == torch.float32 else v for k, v in inputs.items()}
    seg = 30
    n_seg = max(1, _m.ceil(seconds / seg))
    audio = None
    for i in range(n_seg):
        if audio is None:
            audio = model.generate(**inputs, max_new_tokens=int(seg * 50))
        else:
            audio = model.generate(input_values=audio, **inputs, max_new_tokens=int(seg * 50))
    wav = audio[0].cpu().numpy()
    if wav.ndim == 2:
        wav = wav[0]
    np.save(out_path, wav)

def _crossfade(a, b, fade_sr=8000):
    """交叉淡化拼接两段音频"""
    if len(b) < fade_sr * 2:
        return np.concatenate([a, b])
    fade = np.minimum(np.arange(fade_sr), fade_sr - 1 - np.arange(fade_sr)).astype(np.float64) / (fade_sr - 1)
    tail = a[-fade_sr:].astype(np.float64) * (1 - fade)
    head = b[:fade_sr].astype(np.float64) * fade
    mid = np.concatenate([tail + head, b[fade_sr:].astype(np.float64)])
    return np.concatenate([a[:-fade_sr].astype(np.float64), mid])

def gen_song(prompt, seconds=120):
    """完整歌曲：2 进程并行生成，各唱一半，交叉淡化拼接"""
    import math
    t0 = time.time()
    half = math.ceil(seconds / 2)
    tmp1 = os.path.join(OUT_DIR, f'_seg_{int(time.time())}_a.npy')
    tmp2 = os.path.join(OUT_DIR, f'_seg_{int(time.time())}_b.npy')
    ctx = mp.get_context('spawn')
    ps = [
        ctx.Process(target=_song_worker, args=(prompt, half, 1000, tmp1)),
        ctx.Process(target=_song_worker, args=(prompt, seconds - half, 2000, tmp2)),
    ]
    for p in ps:
        p.start()
    for p in ps:
        p.join()
    a = np.load(tmp1)
    b = np.load(tmp2)
    os.remove(tmp1)
    os.remove(tmp2)
    wav = _crossfade(a, b)
    name = f'song_{int(time.time())}.wav'
    _save_wav(os.path.join(OUT_DIR, name), wav)
    dur = round(wav.shape[0] / SR, 1)
    print(f'[music] 完整歌曲完成: {name} {dur}s 总耗时{int(time.time()-t0)}s', flush=True)
    return name, dur

if __name__ == '__main__':
    n, d = gen('Traditional Arabic music, oud and nay flute, meditative maqam melody', 10)
    print('测试完成:', n, d, '秒')

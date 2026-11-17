#!/usr/bin/env python3
"""Assemble gameplay clips into a trailer or a vertical short.

Usage:
    python3 videos/montage.py videos/configs/trailer.json
    python3 videos/montage.py videos/configs/short_divine_hatch.json --out out.mp4
    python3 videos/montage.py videos/configs/trailer.json --check   # verify rushes only

Requires ffmpeg and ffprobe on the PATH. Standard library only.
Paths in a config (rushes, music, output) are relative to the config file.
See videos/README.md for the config format.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

FORMATS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
}

FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Black.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/ariblk.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(" ".join(cmd), file=sys.stderr)
        print(result.stderr[-3000:], file=sys.stderr)
        die("ffmpeg failed (see above)")


def probe(path: Path) -> tuple[float, bool]:
    """Return (duration in seconds, has_audio) for a media file."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
         "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        die(f"cannot read {path}: {out.stderr.strip()}")
    info = json.loads(out.stdout)
    duration = float(info.get("format", {}).get("duration", 0) or 0)
    has_audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    return duration, has_audio


def find_font(cfg_font: str | None, base: Path) -> str:
    if cfg_font:
        p = (base / cfg_font).resolve()
        if not p.exists():
            die(f"font not found: {p}")
        return str(p)
    for f in FONT_CANDIDATES:
        if os.path.exists(f):
            return f
    die('no bold font found; set "font" in the config to a .ttf/.otf file')
    return ""


def ff_escape(value: str) -> str:
    """Escape a path for use inside an ffmpeg filter option."""
    return value.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def atempo_chain(speed: float) -> str:
    """atempo only accepts 0.5..2.0 per instance, so chain as needed."""
    parts = []
    s = speed
    while s < 0.5:
        parts.append("atempo=0.5")
        s /= 0.5
    while s > 2.0:
        parts.append("atempo=2.0")
        s /= 2.0
    parts.append(f"atempo={s:.4f}")
    return ",".join(parts)


class Renderer:
    def __init__(self, cfg: dict, base: Path, tmp: Path):
        self.cfg = cfg
        self.base = base
        self.tmp = tmp
        fmt = cfg.get("format", "16:9")
        if fmt not in FORMATS:
            die(f"format must be one of {list(FORMATS)}")
        self.w, self.h = FORMATS[fmt]
        self.vertical = self.h > self.w
        self.fps = int(cfg.get("fps", 30))
        self.font = find_font(cfg.get("font"), base)
        self.fit = cfg.get("fit", "crop" if self.vertical else "crop")
        self.text_color = cfg.get("text_color", "white")
        self.accent = cfg.get("accent_color", "#FFD23F")
        self.game_volume = float(cfg.get("game_volume", 1.0))
        self.count = 0

    # ---------- text ----------
    def _textfile(self, text: str, max_chars: int) -> Path:
        lines = []
        for raw in text.split("\n"):
            lines.extend(textwrap.wrap(raw, max_chars) or [""])
        self.count += 1
        p = self.tmp / f"text_{self.count}.txt"
        p.write_text("\n".join(lines), encoding="utf-8")
        return p

    def _drawtext(self, text: str, size: int, y_expr: str, color: str, appear: float = 0.0) -> str:
        max_chars = 16 if self.vertical else 26
        if size < self.base_size():
            max_chars = int(max_chars * 1.5)
        tf = self._textfile(text, max_chars)
        border = max(4, size // 14)
        alpha = f"if(lt(t,{appear}),0,min(1,(t-{appear})/0.15))"
        return (
            f"drawtext=fontfile='{ff_escape(self.font)}':textfile='{ff_escape(str(tf))}'"
            f":fontsize={size}:fontcolor={color}:borderw={border}:bordercolor=black"
            f":shadowx=0:shadowy={border}:shadowcolor=black@0.6"
            f":line_spacing={size // 6}:text_align=center"
            f":x=(w-text_w)/2:y={y_expr}:alpha='{alpha}'"
        )

    def base_size(self) -> int:
        return int(min(self.w, self.h) * (0.095 if self.vertical else 0.09))

    def _text_filters(self, seg: dict) -> list[str]:
        filters = []
        size = self.base_size()
        # Vertical: keep text in the upper area, away from TikTok/Shorts buttons.
        # Horizontal: lower third.
        y_main = "h*0.17" if self.vertical else "h*0.70-text_h/2"
        y_sub = "h*0.17+%d" % int(size * 2.6) if self.vertical else "h*0.70+text_h/2+%d" % int(size * 0.9)
        if seg.get("text"):
            filters.append(self._drawtext(seg["text"], size, y_main, self.text_color, seg.get("text_at", 0.0)))
        if seg.get("subtext"):
            filters.append(self._drawtext(seg["subtext"], int(size * 0.6), y_sub, self.accent,
                                          seg.get("text_at", 0.0) + 0.2))
        return filters

    # ---------- segments ----------
    def _fit_filter(self, mode: str) -> str:
        w, h = self.w, self.h
        if mode == "blur":
            return (
                f"split=2[bg][fg];"
                f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=30:2[bg2];"
                f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fg2];"
                f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2"
            )
        # crop: fill the frame, centred unless crop_x is given (0 = left, 1 = right)
        return f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}:(iw-{w})*CROPX:(ih-{h})/2"

    def render_clip(self, seg: dict, index: int) -> Path:
        src = (self.base / seg["file"]).resolve()
        if not src.exists():
            die(f"segment {index}: rush not found: {src}")
        start = float(seg.get("start", 0))
        duration = float(seg["duration"])
        speed = float(seg.get("speed", 1.0))
        src_len = duration * speed
        src_dur, has_audio = probe(src)
        if start + src_len > src_dur + 0.05:
            die(f"segment {index}: {src.name} is {src_dur:.2f}s long, "
                f"but needs {start:.2f}s + {src_len:.2f}s")

        fit = self._fit_filter(seg.get("fit", self.fit)).replace("CROPX", str(float(seg.get("crop_x", 0.5))))
        vf = [f"setpts=(PTS-STARTPTS)/{speed}", fit]
        zoom = float(seg.get("zoom", 1.0))
        if zoom > 1.0:
            # slow push-in from 1.0 to `zoom` across the segment
            vf.append(
                f"scale=w='iw*(1+({zoom}-1)*t/{duration})':h='ih*(1+({zoom}-1)*t/{duration})':eval=frame,"
                f"crop={self.w}:{self.h}"
            )
        vf.append(f"fps={self.fps}")
        vf += self._text_filters(seg)
        vf += self._fades(seg, duration)
        vf.append("format=yuv420p")

        out = self.tmp / f"seg_{index:03d}.mp4"
        cmd = ["ffmpeg", "-y", "-ss", f"{start}", "-t", f"{src_len}", "-i", str(src)]
        keep_audio = has_audio and seg.get("audio", True)
        if not keep_audio:
            cmd += ["-f", "lavfi", "-t", f"{duration}", "-i", "anullsrc=r=48000:cl=stereo"]
        af = f"{atempo_chain(speed)},volume={self.game_volume * float(seg.get('volume', 1.0))}" if keep_audio else "anull"
        af += f",aformat=sample_rates=48000:channel_layouts=stereo,apad,atrim=0:{duration}"
        filt = f"[0:v]{','.join(vf)}[v];[{0 if keep_audio else 1}:a]{af}[a]"
        cmd += ["-filter_complex", filt, "-map", "[v]", "-map", "[a]", "-t", f"{duration}"]
        cmd += self._encode_args()
        cmd.append(str(out))
        run(cmd)
        return out

    def render_card(self, seg: dict, index: int) -> Path:
        duration = float(seg.get("duration", 3))
        color = seg.get("color", "#120A2E")
        vf = [f"fps={self.fps}"]
        size = int(self.base_size() * 1.15)
        if seg.get("text"):
            vf.append(self._drawtext(seg["text"], size, "h*0.42-text_h", self.text_color, seg.get("text_at", 0.0)))
        if seg.get("subtext"):
            vf.append(self._drawtext(seg["subtext"], int(size * 0.62), "h*0.42+%d" % int(size * 0.6),
                                     self.accent, seg.get("text_at", 0.0) + 0.35))
        vf += self._fades(seg, duration, default_in=0.3)
        vf.append("format=yuv420p")
        out = self.tmp / f"seg_{index:03d}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c={color}:s={self.w}x{self.h}:d={duration}:r={self.fps}",
            "-f", "lavfi", "-t", f"{duration}", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex", f"[0:v]{','.join(vf)}[v]", "-map", "[v]", "-map", "1:a",
            "-t", f"{duration}",
        ]
        cmd += self._encode_args()
        cmd.append(str(out))
        run(cmd)
        return out

    def _fades(self, seg: dict, duration: float, default_in: float = 0.0) -> list[str]:
        f = []
        if seg.get("flash"):
            f.append("fade=t=in:st=0:d=0.25:color=white")
        elif float(seg.get("fade_in", default_in)) > 0:
            f.append(f"fade=t=in:st=0:d={float(seg.get('fade_in', default_in))}")
        fo = float(seg.get("fade_out", 0))
        if fo > 0:
            f.append(f"fade=t=out:st={duration - fo}:d={fo}")
        return f

    def _encode_args(self) -> list[str]:
        return ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(self.fps),
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]

    # ---------- assembly ----------
    def render(self, out_path: Path) -> None:
        segments = self.cfg.get("segments", [])
        if not segments:
            die("config has no segments")
        parts = []
        for i, seg in enumerate(segments):
            kind = seg.get("type", "clip")
            label = seg.get("text") or seg.get("file") or kind
            print(f"  [{i + 1}/{len(segments)}] {kind}: {label}")
            parts.append(self.render_card(seg, i) if kind == "card" else self.render_clip(seg, i))

        listing = self.tmp / "concat.txt"
        listing.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts), encoding="utf-8")
        joined = self.tmp / "joined.mp4"
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(joined)])

        total, _ = probe(joined)
        music = self.cfg.get("music")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if music:
            mpath = (self.base / music).resolve()
            if not mpath.exists():
                die(f"music not found: {mpath}")
            mvol = float(self.cfg.get("music_volume", 0.6))
            mstart = float(self.cfg.get("music_start", 0))
            fade = min(1.5, total / 4)
            filt = (
                f"[1:a]atrim=start={mstart},asetpts=PTS-STARTPTS,volume={mvol},"
                f"afade=t=in:d=0.3,afade=t=out:st={total - fade}:d={fade},"
                f"aformat=sample_rates=48000:channel_layouts=stereo[m];"
                f"[0:a][m]amix=inputs=2:duration=first:normalize=0[a]"
            )
            run(["ffmpeg", "-y", "-i", str(joined), "-stream_loop", "-1", "-i", str(mpath),
                 "-filter_complex", filt, "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                 "-c:a", "aac", "-b:a", "192k", "-t", f"{total}", "-movflags", "+faststart", str(out_path)])
        else:
            run(["ffmpeg", "-y", "-i", str(joined), "-c", "copy", "-movflags", "+faststart", str(out_path)])
        print(f"done: {out_path} ({total:.1f}s, {self.w}x{self.h})")


def check(cfg: dict, base: Path) -> bool:
    ok = True
    total = 0.0
    for i, seg in enumerate(cfg.get("segments", []), 1):
        dur = float(seg.get("duration", 3))
        total += dur
        if seg.get("type", "clip") == "card":
            print(f"  {i:2d}. card   {dur:4.1f}s  {seg.get('text', '')}")
            continue
        src = (base / seg["file"]).resolve()
        if not src.exists():
            print(f"  {i:2d}. MISSING     {seg['file']}")
            ok = False
            continue
        length, _ = probe(src)
        need = float(seg.get("start", 0)) + dur * float(seg.get("speed", 1))
        status = "ok" if need <= length + 0.05 else f"TOO SHORT ({length:.1f}s, needs {need:.1f}s)"
        if status != "ok":
            ok = False
        print(f"  {i:2d}. clip   {dur:4.1f}s  {seg['file']}  {status}")
    print(f"  total: {total:.1f}s")
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config", type=Path)
    ap.add_argument("--out", type=Path, help="output file (default: the config's \"output\")")
    ap.add_argument("--check", action="store_true", help="only verify that the rushes exist and are long enough")
    args = ap.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        die("ffmpeg and ffprobe must be installed and on the PATH")
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    base = args.config.resolve().parent

    print(f"{args.config.name}: {cfg.get('title', '')}")
    if args.check:
        sys.exit(0 if check(cfg, base) else 1)

    out = args.out.resolve() if args.out else (base / cfg.get("output", "../out/video.mp4")).resolve()
    with tempfile.TemporaryDirectory(prefix="montage_") as tmp:
        Renderer(cfg, base, Path(tmp)).render(out)


if __name__ == "__main__":
    main()

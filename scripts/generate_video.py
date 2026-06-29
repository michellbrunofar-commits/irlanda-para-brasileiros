#!/usr/bin/env python3
"""
Pipeline automático: relatório → vídeo → YouTube.

Requer:
  UNSPLASH_ACCESS_KEY         — unsplash.com/developers (gratuito)
  YOUTUBE_CLIENT_SECRETS_FILE — caminho para o JSON do Google Cloud Console

Instalar:
  pip3 install gtts requests google-api-python-client google-auth-oauthlib
  brew install ffmpeg   (ou baixar em ffmpeg.org)
"""

import json
import os
import pickle
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ── Dependências ──────────────────────────────────────────────────────────────

def require(pkg, install):
    try:
        return __import__(pkg)
    except ImportError:
        print(f"Instale: pip3 install {install}")
        sys.exit(1)

requests = require("requests", "requests")
gTTS     = require("gtts", "gtts").gTTS

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request as GRequest
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False

# ── Config ────────────────────────────────────────────────────────────────────

UNSPLASH_KEY     = os.environ.get("UNSPLASH_ACCESS_KEY", "")
YOUTUBE_SECRETS  = os.environ.get("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
POSTS_DIR        = Path(__file__).parent.parent / "posts"
OUTPUT_DIR       = Path(__file__).parent.parent / "videos"
W, H             = 1920, 1080

SECTION_QUERIES = {
    "intro":     "Dublin Ireland skyline green",
    "mercado":   "Dublin office technology workers",
    "habitacao": "Dublin housing apartments city",
    "imigracao": "Ireland passport visa document",
    "mundial":   "European economy finance Frankfurt",
    "tldr":      "Ireland nature green landscape",
}

MONTHS_PT = {
    "January":"Janeiro", "February":"Fevereiro", "March":"Março",
    "April":"Abril", "May":"Maio", "June":"Junho", "July":"Julho",
    "August":"Agosto", "September":"Setembro", "October":"Outubro",
    "November":"Novembro", "December":"Dezembro",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def pt_date(slug: str) -> str:
    d = datetime.strptime(slug, "%Y-%m-%d").strftime("%d de %B de %Y")
    for en, pt in MONTHS_PT.items():
        d = d.replace(en, pt)
    return d


def clean_text(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*",     r"\1", text)
    text = re.sub(r"^[-*]\s+",      "",    text, flags=re.MULTILINE)
    text = re.sub(r"^#+\s+",        "",    text, flags=re.MULTILINE)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    text = re.sub(r"\n{3,}",        "\n\n", text)
    return text.strip()


def get_latest_post() -> tuple[str, Path]:
    posts = sorted(POSTS_DIR.glob("*.md"), reverse=True)
    if not posts:
        print("Nenhum relatório encontrado em posts/", file=sys.stderr)
        sys.exit(1)
    return posts[0].stem, posts[0]


def parse_report(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    if content.startswith("---"):
        content = content.split("---", 2)[2].strip()

    title_m = re.search(r"^# (.+)$", content, re.MULTILINE)
    title   = title_m.group(1) if title_m else "Análise Econômica"

    patterns = [
        ("mercado",   r"### Mercado de Trabalho\n(.*?)(?=\n###|\n---)",   "Mercado de Trabalho"),
        ("habitacao", r"### Habita.*?\n(.*?)(?=\n###|\n---)",             "Habitação e Custo de Vida"),
        ("imigracao", r"### Imigra.*?\n(.*?)(?=\n###|\n---|\Z)",          "Imigração e Vistos"),
        ("mundial",   r"### Destaques Globais\n(.*?)(?=\n###|\n---)",     "Panorama Mundial"),
        ("tldr",      r"### Resumo Executivo.*?\n(.*?)(?=\n---|\Z)",      "Resumo do Dia"),
    ]

    sections = []
    for key, pat, label in patterns:
        m = re.search(pat, content, re.DOTALL)
        if m:
            text = clean_text(m.group(1))
            if len(text) > 50:
                sections.append((key, label, text))

    return {"title": title, "sections": sections}

# ── Imagem ────────────────────────────────────────────────────────────────────

def fetch_image(query: str, dest: Path):
    if UNSPLASH_KEY:
        try:
            url  = f"https://api.unsplash.com/photos/random?query={query}&orientation=landscape"
            resp = requests.get(url, headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"}, timeout=10)
            if resp.status_code == 200:
                img_url = resp.json()["urls"]["regular"]
                img = requests.get(img_url, timeout=30)
                dest.write_bytes(img.content)
                return
        except Exception as e:
            print(f"Unsplash erro: {e} — usando cor sólida", file=sys.stderr)

    # Fallback: fundo verde Irlanda
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x169B62:size={W}x{H}:rate=1",
        "-frames:v", "1", str(dest)
    ], capture_output=True)

# ── Áudio ─────────────────────────────────────────────────────────────────────

def make_tts(text: str, dest: Path):
    gTTS(text=text[:900], lang="pt", slow=False).save(str(dest))


def audio_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 6.0

# ── Segmentos de vídeo ────────────────────────────────────────────────────────

def make_intro(date_str: str, dest: Path):
    line1 = "Irlanda para Brasileiros"
    line2 = f"Analise Economica — {date_str}"
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=0x0f7a4d:size={W}x{H}:rate=25",
        "-vf",
        f"drawtext=text='{line1}':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=h/2-80,"
        f"drawtext=text='{line2}':fontsize=44:fontcolor=white@0.85:x=(w-text_w)/2:y=h/2+20",
        "-t", "4", "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p", str(dest)
    ], capture_output=True)


def make_segment(img: Path, audio: Path, title: str, dest: Path):
    dur  = audio_duration(audio) + 0.5
    safe = title.replace("'", "").replace(":", " -").replace(",", "")
    vf   = (
        f"scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},"
        f"drawtext=text='{safe}':"
        f"fontsize=52:fontcolor=white:x=(w-text_w)/2:y=h-140:"
        f"box=1:boxcolor=black@0.55:boxborderw=18"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img),
        "-i", str(audio),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-t", str(dur), "-pix_fmt", "yuv420p",
        str(dest)
    ], capture_output=True)


def concat_segments(segs: list[Path], dest: Path):
    lst = dest.parent / "list.txt"
    lst.write_text("\n".join(f"file '{s.absolute()}'" for s in segs))
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(lst), "-c", "copy", str(dest)
    ], capture_output=True)
    lst.unlink(missing_ok=True)

# ── YouTube ───────────────────────────────────────────────────────────────────

def upload_youtube(video: Path, title: str, date_str: str):
    if not YOUTUBE_AVAILABLE:
        print("google-api-python-client não instalado — pulando upload.", file=sys.stderr)
        return
    if not os.path.exists(YOUTUBE_SECRETS):
        print(f"Arquivo não encontrado: {YOUTUBE_SECRETS} — pulando upload.", file=sys.stderr)
        return

    scopes    = ["https://www.googleapis.com/auth/youtube.upload"]
    token_f   = Path("youtube_token.pickle")
    creds     = None

    if token_f.exists():
        creds = pickle.loads(token_f.read_bytes())

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GRequest())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(YOUTUBE_SECRETS, scopes)
            creds = flow.run_local_server(port=0)
        token_f.write_bytes(pickle.dumps(creds))

    yt   = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title":           f"{title} | Irlanda para Brasileiros",
            "description":     f"Análise econômica da Irlanda — {date_str}\n\nMercado de trabalho, habitação, imigração e economia mundial para brasileiros na Irlanda.\n\n🌐 Site: https://irlandaparabrasileiros.vercel.app",
            "tags":            ["Irlanda", "Brasil", "imigrantes", "economia", "Dublin", "emprego", "moradia", "visto"],
            "categoryId":      "25",
            "defaultLanguage": "pt",
        },
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }

    media  = MediaFileUpload(str(video), chunksize=-1, resumable=True, mimetype="video/mp4")
    req    = yt.videos().insert(part=",".join(body.keys()), body=body, media_body=media)
    resp   = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  Upload: {int(status.progress() * 100)}%", file=sys.stderr)

    vid_id = resp["id"]
    print(f"✓ Publicado: https://youtube.com/watch?v={vid_id}", file=sys.stderr)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    for dep in ["ffmpeg", "ffprobe"]:
        if subprocess.run(["which", dep], capture_output=True).returncode != 0:
            print(f"Erro: '{dep}' não encontrado.\nInstale: brew install ffmpeg")
            sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)

    slug, post_path = get_latest_post()
    print(f"Gerando vídeo: {slug}", file=sys.stderr)

    report   = parse_report(post_path)
    date_str = pt_date(slug)
    segments = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        # Intro
        print("→ Intro", file=sys.stderr)
        intro = tmp / "seg_00.mp4"
        make_intro(date_str, intro)
        segments.append(intro)

        # Seções
        for i, (key, label, text) in enumerate(report["sections"], 1):
            print(f"→ {label}", file=sys.stderr)
            img   = tmp / f"img_{i:02d}.jpg"
            audio = tmp / f"audio_{i:02d}.mp3"
            seg   = tmp / f"seg_{i:02d}.mp4"

            fetch_image(SECTION_QUERIES.get(key, "Ireland economy"), img)
            make_tts(text, audio)
            make_segment(img, audio, label, seg)
            segments.append(seg)

        # Montar vídeo final
        print("→ Montando vídeo final...", file=sys.stderr)
        output = OUTPUT_DIR / f"{slug}.mp4"
        concat_segments(segments, output)

    print(f"✓ Vídeo salvo: {output}", file=sys.stderr)

    upload_youtube(output, report["title"], date_str)


if __name__ == "__main__":
    main()

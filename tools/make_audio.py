"""data.js의 질문·답변으로 audio/{id}-q.mp3, audio/{id}-a.mp3를 생성합니다.

사용법:  pip install edge-tts  →  python tools/make_audio.py
텍스트가 바뀐 항목만 다시 만듭니다(audio/manifest.json에 해시 저장).
"""
import asyncio, hashlib, json, pathlib, re

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "audio"
VOICES = {"q": "en-US-AvaNeural", "a": "en-US-AndrewNeural"}  # 질문: 진행자 Ava, 답변: 응시자 Harry


def load_questions():
    src = (ROOT / "data.js").read_text(encoding="utf-8")
    return json.loads(re.search(r"const QUESTIONS = (\[.*\]);", src, re.S).group(1))


async def main():
    OUT.mkdir(exist_ok=True)
    manifest_path = OUT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    jobs = []
    for item in load_questions():
        for kind, text in (("q", item["q"]), ("a", item["a"])):
            name = f"{item['id']}-{kind}.mp3"
            digest = hashlib.sha1((VOICES[kind] + text).encode()).hexdigest()
            if manifest.get(name) != digest or not (OUT / name).exists():
                jobs.append((name, kind, text, digest))
    sem = asyncio.Semaphore(4)

    async def make(name, kind, text, digest):
        async with sem:
            await edge_tts.Communicate(text, VOICES[kind]).save(str(OUT / name))
            manifest[name] = digest
            print("made", name)

    await asyncio.gather(*(make(*j) for j in jobs))
    manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True), encoding="utf-8")
    print(f"{len(jobs)} generated, {len(manifest)} total")


if __name__ == "__main__":
    asyncio.run(main())

// 미리 생성한 신경망 음성(audio/{id}-q|a.mp3)을 재생합니다. 파일을 못 불러오면 브라우저 TTS로 대체합니다.
const OpicVoice = (() => {
  let audio = null;
  function stop() {
    if (audio) { audio.pause(); audio = null; }
    if ('speechSynthesis' in window) speechSynthesis.cancel();
  }
  function fallback(text, rate, onend) {
    if (!('speechSynthesis' in window)) { onend?.(); return; }
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'en-US'; u.rate = rate; u.onend = () => onend?.();
    speechSynthesis.speak(u);
  }
  function play(id, kind, { rate = 1, onend } = {}) {
    stop();
    const a = new Audio(`audio/${id}-${kind}.mp3`);
    audio = a;
    a.playbackRate = rate;
    a.onended = () => { if (audio === a) { audio = null; onend?.(); } };
    a.play().catch(err => {
      if (audio !== a) return;
      audio = null;
      if (err.name === 'NotAllowedError') { onend?.(); return; }
      const item = QUESTIONS.find(x => x.id === id);
      fallback(kind === 'q' ? item.q : item.a, rate, onend);
    });
  }
  return { play, stop };
})();

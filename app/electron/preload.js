// Electron 预加载：暴露原生语音识别给页面
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // 原生语音识别（macOS SFSpeechRecognizer）
  startVoice: () => ipcRenderer.send('voice-start'),
  stopVoice: () => ipcRenderer.send('voice-stop'),
  // 每句识别结果
  onSpeech: (cb) => {
    ipcRenderer.on('voice-text', (e, text) => cb(text));
  },
  // 识别器状态
  onVoiceState: (cb) => {
    ipcRenderer.on('voice-state', (e, state) => cb(state));
  },
  isDesktop: true,
});

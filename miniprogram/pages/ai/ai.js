const api = require('../../utils/api');

Page({
  data: {
    messages: [
      { role: 'bot', text: 'مرحبا！你好，我是 AI 老师 نور（努尔）。\n用中文或阿拉伯语提问，我来帮你学阿语、读书、查资料。' }
    ],
    input: '',
    sending: false,
    scrollInto: ''
  },
  onInput(e) {
    this.setData({ input: e.detail.value });
  },
  send() {
    const msg = (this.data.input || '').trim();
    if (!msg || this.data.sending) return;
    const messages = this.data.messages.concat({ role: 'user', text: msg });
    this.setData({ input: '', messages, sending: true, scrollInto: 'm' + (messages.length - 1) });

    api.chat(msg).then((d) => {
      const reply = d.arabic || d.reply || '（没有回复）';
      const arr = this.data.messages.concat({ role: 'bot', text: reply });
      this.setData({ messages: arr, sending: false, scrollInto: 'm' + (arr.length - 1) });
    }).catch(() => {
      const arr = this.data.messages.concat({ role: 'bot', text: '⚠️ 请求失败，请检查网络或稍后重试。' });
      this.setData({ messages: arr, sending: false });
    });
  }
});

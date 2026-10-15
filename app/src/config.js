// 全局配置：API 地址（iOS / Android / Web 通用）
// Web 用 localhost；真机请把 LAN_IP 改成电脑的局域网 IP（与 server.py 同网段）
import { Platform } from 'react-native';

export const LAN_IP = '192.168.1.6'; // ← 真机调试时改成你电脑的局域网 IP
export const PORT = 8080;

export const API_BASE =
  Platform.OS === 'web'
    ? `http://localhost:${PORT}`
    : `http://${LAN_IP}:${PORT}`;

export const AI_NAME = 'رفيق العربية'; // 老师名字（阿拉伯语）

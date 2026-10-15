// 礼拜时间计算（本地天文算法，离线可用）—— 标准 praytimes.org 算法
// 标准：MWL（Fajr 18° / Isha 17°），Asr 影子倍数 1（沙斐仪派），日出日落 0.833°

export const CITIES = [
  { name: '西宁', lat: 36.6171, lon: 101.7782 },
  { name: '格尔木', lat: 36.4027, lon: 94.9029 },
  { name: '海东', lat: 36.5005, lon: 102.1045 },
  { name: '德令哈', lat: 37.3738, lon: 97.3609 },
  { name: '共和', lat: 36.2845, lon: 100.6201 },
  { name: '玉树', lat: 33.0047, lon: 97.0061 },
  { name: '玛沁', lat: 34.4739, lon: 100.2417 },
  { name: '同仁', lat: 35.5197, lon: 102.0166 },
  { name: '北京', lat: 39.9042, lon: 116.4074 },
  { name: '上海', lat: 31.2304, lon: 121.4737 },
  { name: '广州', lat: 23.1291, lon: 113.2644 },
  { name: '深圳', lat: 22.5431, lon: 114.0579 },
  { name: '乌鲁木齐', lat: 43.8256, lon: 87.6168 },
  { name: '兰州', lat: 36.0611, lon: 103.8343 },
  { name: '银川', lat: 38.4872, lon: 106.2309 },
  { name: '西安', lat: 34.3416, lon: 108.9398 },
  { name: '西宁', lat: 36.6171, lon: 101.7782 },
  { name: '昆明', lat: 25.0389, lon: 102.7183 },
  { name: '郑州', lat: 34.7466, lon: 113.6254 },
  { name: '呼和浩特', lat: 40.8424, lon: 111.749 },
  { name: '沈阳', lat: 41.8057, lon: 123.4315 },
  { name: '成都', lat: 30.5728, lon: 104.0668 },
];

const D2R = Math.PI / 180;
const R2D = 180 / Math.PI;

function fixAngle(a) { return a - 360 * Math.floor(a / 360); }
function fixHour(a) { return a - 24 * Math.floor(a / 24); }

// 太阳位置：返回赤纬（弧度）与均时差（小时）
function sunPosition(jd) {
  const D = jd - 2451545.0;
  const g = fixAngle(357.529 + 0.98560028 * D);
  const q = fixAngle(280.459 + 0.98564736 * D);
  const L = fixAngle(q + 1.915 * Math.sin(g * D2R) + 0.02 * Math.sin(2 * g * D2R));
  const e = 23.439 - 0.00000036 * D;
  const RA = R2D * Math.atan2(Math.cos(e * D2R) * Math.sin(L * D2R), Math.cos(L * D2R)) / 15;
  const eqt = q / 15 - fixHour(RA);
  const decl = Math.asin(Math.sin(e * D2R) * Math.sin(L * D2R));
  return { decl, eqt };
}

export function prayerTimes(date, lat, lon, tzOffsetMin) {
  const tz = tzOffsetMin / 60;
  const jd = date.getTime() / 86400000 + 2440587.5;
  const { decl, eqt } = sunPosition(jd);
  const dhuhr = fixHour(12 + tz - lon / 15 - eqt);

  function hourAngle(angle) {
    const cosH = (Math.sin(angle * D2R) - Math.sin(decl) * Math.sin(lat * D2R)) / (Math.cos(decl) * Math.cos(lat * D2R));
    return R2D * Math.acos(Math.min(1, Math.max(-1, cosH))) / 15;
  }

  const sunrise = dhuhr - hourAngle(-0.833);
  const maghrib = dhuhr + hourAngle(-0.833);
  const fajr = dhuhr - hourAngle(-18);
  const isha = dhuhr + hourAngle(-17);
  // 晡礼：影子倍数 1（沙斐仪派）
  const alt = Math.atan(1 / (Math.tan(Math.abs(lat * D2R - decl)) + 1));
  const asr = dhuhr + R2D * Math.acos(Math.min(1, Math.max(-1, (Math.sin(alt) - Math.sin(decl) * Math.sin(lat * D2R)) / (Math.cos(decl) * Math.cos(lat * D2R))))) / 15;

  return {
    fajr: fixHour(fajr), sunrise: fixHour(sunrise), dhuhr: fixHour(dhuhr),
    asr: fixHour(asr), maghrib: fixHour(maghrib), isha: fixHour(isha),
  };
}

export function fmt(hours) {
  const total = Math.round(hours * 60);
  const h = Math.floor(total / 60) % 24;
  const mm = total % 60;
  return String(h).padStart(2, '0') + ':' + String(mm).padStart(2, '0');
}

export const ATHAN_AR = 'الله أكبر الله أكبر، أشهد أن لا إله إلا الله، أشهد أن محمدا رسول الله، حي على الصلاة، حي على الفلاح، الله أكبر الله أكبر، لا إله إلا الله';
export const ATHAN_CN = '真主至大，真主至大；我作证：除真主外绝无应受崇拜的；我作证：穆罕默德是真主的使者；快来礼拜吧；快来成功吧；真主至大，真主至大；除真主外绝无应受崇拜的';

export const PRAYER_NAMES = [
  { key: 'fajr', cn: '晨礼', en: 'Fajr' },
  { key: 'sunrise', cn: '日出', en: 'Sunrise' },
  { key: 'dhuhr', cn: '晌礼', en: 'Dhuhr' },
  { key: 'asr', cn: '晡礼', en: 'Asr' },
  { key: 'maghrib', cn: '昏礼', en: 'Maghrib' },
  { key: 'isha', cn: '宵礼', en: 'Isha' },
];

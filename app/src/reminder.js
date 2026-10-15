// 每日学习提醒（本地通知）
import * as Notifications from 'expo-notifications';
import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = 'nur_remind_time';
const CHANNEL = 'daily-reminder';

Notifications.setNotificationHandler({
  handleNotification: async () => ({ shouldShowAlert: true, shouldPlaySound: false, shouldSetBadge: false }),
});

export const Reminder = {
  async getTime() {
    try { return (await AsyncStorage.getItem(KEY)) || ''; } catch { return ''; }
  },
  // hhmm 形如 '20:00'；传空串 = 关闭
  async setTime(hhmm) {
    await AsyncStorage.setItem(KEY, hhmm || '');
    try { await Notifications.cancelAllScheduledNotificationsAsync(); } catch (e) {}
    if (!hhmm) return;
    const [h, m] = hhmm.split(':').map(Number);
    try {
      await Notifications.requestPermissionsAsync();
      try {
        await Notifications.setNotificationChannelAsync(CHANNEL, {
          name: '每日学习提醒',
          importance: Notifications.AndroidImportance.HIGH,
        });
      } catch (e) {}
      await Notifications.scheduleNotificationAsync({
        content: {
          title: '🕌 燃灯者 · 该学习啦',
          body: '今天的句子、卡片和对话等着你，打开 App 继续阿拉伯语之旅吧！',
        },
        trigger: { type: Notifications.SchedulableTriggerInputTypes.DAILY, hour: h, minute: m },
      });
    } catch (e) {}
  },
  async cancel() {
    try { await Notifications.cancelAllScheduledNotificationsAsync(); } catch (e) {}
  },
};

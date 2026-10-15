// 我的 ProfileScreen：用户 + 会员 + 统计
import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert, Modal, TextInput } from 'react-native';
import { Colors, Radius } from '../theme';
import { View as V } from 'react-native';
import { ArchHeader, GlassCard } from '../components';
import { Store } from '../store';
import { setServerIp, getApiBase } from '../api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { Reminder } from '../reminder';
import { SRS } from '../srs';
import WordBookModal from '../WordBookModal';
import QuranModal from '../QuranModal';
import HadithModal from '../HadithModal';
import AdminModal from '../AdminModal';
import VipModal from '../VipModal';
import NodeModal from '../NodeModal';

export default function ProfileScreen() {
  const [stats, setStats] = useState(null);
  const [favCount, setFavCount] = useState(0);
  const [learnCount, setLearnCount] = useState(0);
  const [serverIp, setServerIpState] = useState('');
  const [ipModal, setIpModal] = useState(false);
  const [ipInput, setIpInput] = useState('');
  const [goal, setGoal] = useState(20);
  const GOALS = [10, 20, 30, 50, 100];
  const [serverOn, setServerOn] = useState(null); // null=检测中 true/false
  const [remindTime, setRemindTime] = useState('');
  const [srsInfo, setSrsInfo] = useState({ due: 0, total: 0 });
  const [wbOpen, setWbOpen] = useState(false);
  const [quranOpen, setQuranOpen] = useState(false);
  const [hadithOpen, setHadithOpen] = useState(false);
  const [adminOpen, setAdminOpen] = useState(false);
  const [vipOpen, setVipOpen] = useState(false);
  const [nodeOpen, setNodeOpen] = useState(false);
  const REMIND_OPTS = ['', '18:00', '20:00', '21:00', '22:00'];

  useEffect(() => {
    Reminder.getTime().then(setRemindTime);
    SRS.counts().then(setSrsInfo);
  }, []);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${await getApiBase()}/api/sentences`, { cache: 'no-store' });
        setServerOn(res.ok);
      } catch { setServerOn(false); }
    })();
  }, [serverIp]);

  useEffect(() => {
    (async () => {
      setStats(await Store.getStats());
      setGoal((await Store.getStats()).goalWords || 20);
      setFavCount((await Store.getFavorites()).length);
      setLearnCount((await Store.getLearned()).length);
      const ip = await AsyncStorage.getItem('nur_server_ip');
      setServerIpState(ip || '');
    })();
  }, []);

  // 服务器设置（局域网 IP）
  const openServerSetting = () => {
    setIpInput(serverIp);
    setIpModal(true);
  };

  const saveServerIp = () => {
    const val = (ipInput || '').trim();
    AsyncStorage.setItem('nur_server_ip', val).catch(() => {});
    setServerIp(val);
    setServerIpState(val);
    setIpModal(false);
    Alert.alert('已保存', val ? '服务器已切换为 ' + val : '已恢复默认服务器');
  };

  // 导出学习数据备份（JSON 文件，可通过微信/文件保存）
  const exportData = async () => {
    try {
      const keys = ['nur_favorites', 'nur_learned', 'nur_review', 'nur_stats', 'nur_srs_v1', 'nur_wordbook_v1', 'nur_server_ip'];
      const data = {};
      for (const k of keys) {
        const v = await AsyncStorage.getItem(k);
        if (v) data[k] = v;
      }
      data._exported = new Date().toISOString();
      const path = (FileSystem.cacheDirectory || '') + 'nur-backup-' + Date.now() + '.json';
      await FileSystem.writeAsStringAsync(path, JSON.stringify(data, null, 2));
      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(path, { mimeType: 'application/json', dialogTitle: '导出学习数据备份' });
      } else {
        Alert.alert('导出完成', '备份文件已保存：' + path);
      }
    } catch (e) {
      Alert.alert('导出失败', String(e));
    }
  };

  const plan = 'free'; // 预留会员系统

  return (
    <ScrollView style={styles.root} contentContainerStyle={{ paddingBottom: 40 }}>
      <ArchHeader title="👤 我的" subtitle="" zh="学习档案 · 会员" />

      <View style={styles.section}>
        <GlassCard style={styles.userCard}>
          <View style={styles.avatar}><Text style={styles.avatarTxt}>🧕</Text></View>
          <View style={{ flex: 1, marginLeft: 14 }}>
            <Text style={styles.userName}>阿拉伯语学习者</Text>
            <Text style={styles.userDesc}>{plan === 'free' ? '免费用户' : '高级会员'} · 学习之路</Text>
          </View>
          <TouchableOpacity style={styles.loginBtn} onPress={() => Alert.alert('登录', '支持 Apple / Google / 手机号登录（开发中）')}>
            <Text style={styles.loginTxt}>{plan === 'free' ? '登录' : '会员'}</Text>
          </TouchableOpacity>
        </GlassCard>
      </View>

      <View style={styles.section}>
        <Text style={styles.secTitle}>🔔 每日提醒</Text>
        <GlassCard style={styles.goalCard}>
          <Text style={styles.goalDesc}>到点提醒你学习（本地通知，无需联网）</Text>
          <View style={styles.goalRow}>
            {REMIND_OPTS.map((t) => (
              <TouchableOpacity
                key={t || 'off'}
                style={[styles.goalChip, remindTime === t && styles.goalChipOn]}
                onPress={async () => {
                  setRemindTime(t);
                  await Reminder.setTime(t);
                  Alert.alert(t ? '已设置提醒' : '已关闭提醒', t ? `每天 ${t} 提醒你学习` : '不再发送提醒');
                }}
              >
                <Text style={[styles.goalTxt, remindTime === t && styles.goalTxtOn]}>{t ? t : '关闭'}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </GlassCard>
      </View>

      <View style={styles.section}>
        <Text style={styles.secTitle}>🎯 每日目标</Text>
        <GlassCard style={styles.goalCard}>
          <Text style={styles.goalDesc}>每天学习多少个单词？首页进度环按此计算</Text>
          <View style={styles.goalRow}>
            {GOALS.map((g) => (
              <TouchableOpacity
                key={g}
                style={[styles.goalChip, goal === g && styles.goalChipOn]}
                onPress={async () => {
                  setGoal(g);
                  const s = await Store.getStats();
                  s.goalWords = g;
                  await Store.saveStats(s);
                  setStats(s);
                }}
              >
                <Text style={[styles.goalTxt, goal === g && styles.goalTxtOn]}>{g}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </GlassCard>
      </View>

      {/* 7 天学习曲线 */}
      <View style={styles.section}>
        <Text style={styles.secTitle}>📈 近 7 天学习</Text>
        <View style={styles.chartCard}>
          {(() => {
            const hist = (stats && stats.historyMinutes) || {};
            const days = [];
            for (let i = 6; i >= 0; i--) {
              const d = new Date();
              d.setDate(d.getDate() - i);
              const key = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
              days.push({ key, min: hist[key] || 0, wd: '日一二三四五六'[d.getDay()] });
            }
            const max = Math.max(10, ...days.map((x) => x.min));
            return (
              <View style={{ flexDirection: 'row', alignItems: 'flex-end', height: 110, gap: 6 }}>
                {days.map((x, i) => (
                  <View key={i} style={{ flex: 1, alignItems: 'center' }}>
                    <Text style={{ fontSize: 8.5, color: Colors.muted, marginBottom: 3 }}>{x.min > 0 ? x.min + '分' : ''}</Text>
                    <View style={{ width: '70%', height: Math.max(3, (x.min / max) * 70), borderRadius: 4, backgroundColor: x.min > 0 ? Colors.gold : 'rgba(201,168,76,0.15)' }} />
                    <Text style={{ fontSize: 9, color: Colors.muted, marginTop: 4 }}>{x.wd}</Text>
                  </View>
                ))}
              </View>
            );
          })()}
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.secTitle}>💎 会员</Text>
        <GlassCard style={styles.memberCard}>
          <Text style={styles.memberTitle}>高级会员</Text>
          <Text style={styles.memberDesc}>解锁 AI 无限对话 · 高级课程 · 专项训练</Text>
          <TouchableOpacity style={styles.upgradeBtn} onPress={() => Alert.alert('会员', '高级会员功能预留，即将上线')}>
            <Text style={styles.upgradeTxt}>升级 →</Text>
          </TouchableOpacity>
        </GlassCard>
      </View>

      <View style={styles.section}>
        <Text style={styles.secTitle}>ℹ️ 关于</Text>
        <View style={styles.menuList}>
          <Text style={styles.secTitle}>🎒 我的功能</Text>
          <MenuRow icon="👑" label="开通 VIP 会员（无限 AI · 音乐生成）" onPress={() => setVipOpen(true)} />
          <MenuRow icon="📕" label="我的生词本" onPress={() => setWbOpen(true)} />
          <MenuRow icon="🕌" label="古兰经 · 最近阅读与书签" onPress={() => setQuranOpen(true)} />
          <MenuRow icon="📜" label="圣训 · 收藏与今日一训" onPress={() => setHadithOpen(true)} />
          <MenuRow icon="🕌" label="حامل المصباح · 燃灯者，无声却引人归途" />
          <MenuRow icon="📊" label={`数据：2524句 · 30场景对话 · 5本书 · 古兰经114章`} />
          <MenuRow icon="💾" label="导出学习数据备份" onPress={exportData} />
          <MenuRow icon="🖥" label={`服务器：${serverIp || '默认(自动)'} ${serverOn === true ? '· 🟢 在线' : serverOn === false ? '· 🔴 离线' : '· 检测中...'}`} onPress={openServerSetting} />
          <MenuRow icon="⚡" label="高速节点（免费聚合 · 自动测速）" onPress={() => setNodeOpen(true)} />
          <MenuRow icon="⚙️" label="🖥 管理控制台（系统/内容/AI 设置）" onPress={() => setAdminOpen(true)} />
          <MenuRow icon="📦" label="版本 1.3.0（燃灯者）" />
          <MenuRow icon="🌐" label="支持 iOS / Android" />
        </View>
      </View>

      {/* 服务器设置弹窗 */}
      <Modal visible={ipModal} transparent animationType="fade" onRequestClose={() => setIpModal(false)}>
        <View style={styles.ipMask}>
          <View style={styles.ipCard}>
            <Text style={styles.ipTitle}>🖥 服务器设置</Text>
            <Text style={styles.ipDesc}>输入电脑的局域网 IP（如 192.168.1.9），AI / 文章 / 书籍将从该服务器加载。留空则恢复默认。</Text>
            <TextInput
              style={styles.ipInput}
              value={ipInput}
              onChangeText={setIpInput}
              placeholder="192.168.1.9"
              placeholderTextColor={Colors.muted}
              autoCapitalize="none"
              keyboardType="numeric"
            />
            <View style={styles.ipBtns}>
              <TouchableOpacity style={[styles.ipBtn, styles.ipBtnCancel]} onPress={() => setIpModal(false)}>
                <Text style={styles.ipBtnTxt}>取消</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.ipBtn, styles.ipBtnOk]} onPress={saveServerIp}>
                <Text style={[styles.ipBtnTxt, { color: '#fff' }]}>保存</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

function MiniStat({ icon, label, value }) {
  return (
    <View style={styles.miniStat}>
      <Text style={{ fontSize: 18 }}>{icon}</Text>
      <Text style={styles.miniNum}>{value}</Text>
      <Text style={styles.miniLabel}>{label}</Text>
          <WordBookModal visible={wbOpen} onClose={() => setWbOpen(false)} />
      <QuranModal visible={quranOpen} onClose={() => setQuranOpen(false)} />
      <HadithModal visible={hadithOpen} onClose={() => setHadithOpen(false)} />
      <AdminModal visible={adminOpen} onClose={() => setAdminOpen(false)} />
      <VipModal visible={vipOpen} onClose={() => setVipOpen(false)} />
      <NodeModal visible={nodeOpen} onClose={() => setNodeOpen(false)} />

    </View>
  );
}

function MenuRow({ icon, label, onPress }) {
  if (onPress) {
    return (
      <TouchableOpacity style={styles.menuRow} onPress={onPress}>
        <Text style={{ fontSize: 14 }}>{icon}</Text>
        <Text style={styles.menuTxt}>{label}</Text>
        <Text style={{ fontSize: 14, color: Colors.gold, marginLeft: 'auto' }}>›</Text>
      </TouchableOpacity>
    );
  }
  return (
    <TouchableOpacity style={styles.menuRow} activeOpacity={0.7} onPress={onPress}>
      <Text style={{ fontSize: 14 }}>{icon}</Text>
      <Text style={styles.menuTxt}>{label}</Text>
      {onPress ? <Text style={{ color: '#c9a84c', fontSize: 13 }}>›</Text> : null}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  userCard: { backgroundColor: '#fff', borderRadius: 16, borderWidth: 1, borderColor: 'rgba(201,168,76,.25)', padding: 16, marginBottom: 14 },
  userName: { fontSize: 15, fontWeight: '800', color: '#0f3d31' },
  userVip: { fontSize: 11.5, fontWeight: '700', marginTop: 5 },
  userBtns: { flexDirection: 'row', gap: 8, marginTop: 10 },
  userBtn: { backgroundColor: 'rgba(201,168,76,.15)', borderWidth: 1, borderColor: 'rgba(201,168,76,.35)', borderRadius: 10, paddingHorizontal: 14, paddingVertical: 8 },
  userBtnTxt: { fontSize: 12, fontWeight: '800', color: '#0f3d31' },
  root: { flex: 1, backgroundColor: Colors.cream },
  section: { paddingHorizontal: 16, marginTop: 16 },
  secTitle: { fontSize: 15, fontWeight: '700', color: Colors.greenDark, marginBottom: 10 },
  userCard: { flexDirection: 'row', alignItems: 'center', padding: 16 },
  avatar: {
    width: 54, height: 54, borderRadius: 27, backgroundColor: 'rgba(201,168,76,0.12)',
    alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,0.25)',
  },
  avatarTxt: { fontSize: 26 },
  userName: { fontSize: 15, fontWeight: '700', color: Colors.ink },
  userDesc: { fontSize: 10.5, color: Colors.muted, marginTop: 2 },
  loginBtn: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: 16, backgroundColor: Colors.gold },
  loginTxt: { fontSize: 11, fontWeight: '700', color: '#fff' },
  statGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  chartCard: {
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 14,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)',
  },
  goalCard: { padding: 16 },
  goalDesc: { fontSize: 10.5, color: Colors.muted, marginBottom: 10 },
  goalRow: { flexDirection: 'row', gap: 10 },
  goalChip: {
    flex: 1, paddingVertical: 10, borderRadius: Radius.md, alignItems: 'center',
    backgroundColor: Colors.white, borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  goalChipOn: { backgroundColor: Colors.greenDark, borderColor: 'rgba(201,168,76,0.5)' },
  goalTxt: { fontSize: 13, fontWeight: '800', color: Colors.greenDark },
  goalTxtOn: { color: Colors.goldLight },
  miniStat: {
    width: '48%', backgroundColor: Colors.white, borderRadius: Radius.md, padding: 14,
    alignItems: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)',
  },
  miniNum: { fontSize: 20, fontWeight: '800', color: Colors.greenDark, marginTop: 3 },
  miniLabel: { fontSize: 9.5, color: Colors.muted, marginTop: 1 },
  memberCard: { padding: 18, backgroundColor: 'rgba(15,61,49,0.03)' },
  memberTitle: { fontSize: 16, fontWeight: '800', color: Colors.goldDark },
  memberDesc: { fontSize: 11, color: Colors.muted, marginTop: 4 },
  upgradeBtn: {
    marginTop: 12, alignSelf: 'flex-start', paddingHorizontal: 16, paddingVertical: 8,
    borderRadius: Radius.md, backgroundColor: Colors.greenDark,
  },
  upgradeTxt: { fontSize: 12, color: Colors.goldLight, fontWeight: '700' },
  menuList: { backgroundColor: Colors.white, borderRadius: Radius.md, overflow: 'hidden', borderWidth: 1, borderColor: 'rgba(201,168,76,0.12)' },
  menuRow: { flexDirection: 'row', alignItems: 'center', padding: 14, borderBottomWidth: 1, borderBottomColor: '#f0eeea' },
  menuTxt: { fontSize: 12, color: Colors.ink, marginLeft: 10 },
  ipMask: { flex: 1, backgroundColor: 'rgba(15,61,49,0.5)', justifyContent: 'center', padding: 24 },
  ipCard: { backgroundColor: Colors.cream, borderRadius: Radius.lg, padding: 20 },
  ipTitle: { fontSize: 16, fontWeight: '800', color: Colors.greenDark },
  ipDesc: { fontSize: 11.5, color: Colors.muted, marginTop: 6, lineHeight: 18 },
  ipInput: {
    backgroundColor: Colors.white, borderRadius: Radius.md, marginTop: 12,
    paddingHorizontal: 14, paddingVertical: 10, fontSize: 14, color: Colors.ink,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.3)',
  },
  ipBtns: { flexDirection: 'row', gap: 10, marginTop: 14, justifyContent: 'flex-end' },
  ipBtn: { paddingHorizontal: 18, paddingVertical: 8, borderRadius: Radius.md },
  ipBtnCancel: { backgroundColor: 'rgba(0,0,0,0.06)' },
  ipBtnOk: { backgroundColor: Colors.greenDark },
  ipBtnTxt: { fontSize: 12, fontWeight: '700', color: Colors.ink },
});

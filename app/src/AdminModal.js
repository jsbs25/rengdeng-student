// 管理控制台（App 内置）：系统状态 + 内容管理 + AI 设置 + 系统控制
import React, { useState, useEffect } from 'react';
import {
  View, Text, Modal, ScrollView, TouchableOpacity, StyleSheet, TextInput, ActivityIndicator, Alert,
} from 'react-native';
import { Colors, Radius } from './theme';
import { ArchHeader } from './components';
import { getApiBase } from './api';

const KINDS = [
  ['sentences', '💬 句子'],
  ['hadith', '📜 圣训'],
  ['history', '📜 历史'],
  ['dialogues', '💬 对话'],
];

export default function AdminModal({ visible, onClose }) {
  const [tab, setTab] = useState('dash');
  const [status, setStatus] = useState(null);
  const [kind, setKind] = useState('sentences');
  const [q, setQ] = useState('');
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [sys, setSys] = useState('');
  const [aiSystem, setAiSystem] = useState('');
  const [aiTokens, setAiTokens] = useState('2000');
  const [busy, setBusy] = useState(false);
  const [users, setUsers] = useState([]);
  const [codes, setCodes] = useState([]);

  useEffect(() => {
    if (visible) { loadStatus(); loadAI(); }
  }, [visible]);

  const loadStatus = async () => {
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/status`, { cache: 'no-store' });
      setStatus(await r.json());
    } catch (e) { setStatus(null); }
  };

  const loadUsers = async () => {
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/users`, { cache: 'no-store' });
      const d = await r.json();
      setUsers(d.users || []);
    } catch (e) { setUsers([]); }
  };

  const setVip = async (username) => {
    Alert.prompt ? null : null;
    if (Alert.prompt) {
      Alert.prompt('设置会员', `${username}：开通多少天？（0 取消）`, [
        { text: '取消', style: 'cancel' },
        { text: '确定', onPress: async (days) => { await doSetVip(username, days); } },
      ], 'plain-text', '30');
    } else {
      // Android 无 prompt——用简单方案：30天/90天/取消
      Alert.alert('设置会员', `${username} 开通会员？`, [
        { text: '取消', style: 'cancel' },
        { text: '30 天', onPress: () => doSetVip(username, 30) },
        { text: '90 天', onPress: () => doSetVip(username, 90) },
        { text: '365 天', onPress: () => doSetVip(username, 365) },
      ]);
    }
  };

  const doSetVip = async (username, days) => {
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/set_vip`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, days: parseInt(days) || 0 }),
      });
      const d = await r.json();
      Alert.alert(d.ok ? '✅' : '⚠️', d.msg || '操作完成');
      loadUsers();
    } catch (e) { Alert.alert('⚠️', '操作失败'); }
  };

  const loadCodes = async () => {
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/codes`, { cache: 'no-store' });
      const d = await r.json();
      setCodes(d.codes || []);
    } catch (e) { setCodes([]); }
  };

  const genCodes = async (days) => {
    setBusy(true);
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/gen_code`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ days, batch: 5 }),
      });
      const d = await r.json();
      Alert.alert(d.ok ? '✅ 已生成' : '⚠️', d.msg || (d.codes || []).join('\n'));
      loadCodes();
    } catch (e) { Alert.alert('⚠️', '操作失败'); }
    setBusy(false);
  };

  const loadAI = async () => {
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/ai`, { cache: 'no-store' });
      const d = await r.json();
      setAiSystem(d.system || '');
      setAiTokens(d.max_tokens || '2000');
    } catch (e) {}
  };

  const loadData = async (k) => {
    setKind(k); setBusy(true);
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/data?kind=${k}&page=0&size=30&q=${encodeURIComponent(q)}`, { cache: 'no-store' });
      const d = await r.json();
      setItems(d.items || []);
      setTotal(d.total || 0);
    } catch (e) { setItems([]); setTotal(0); }
    setBusy(false);
  };

  const saveAI = async () => {
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/ai`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ system: aiSystem, max_tokens: parseInt(aiTokens) || 2000 }),
      });
      const d = await r.json();
      Alert.alert(d.ok ? '✅ 已保存' : '⚠️ 保存失败', d.ok ? 'AI 设置已保存，重启服务器后生效' : '请重试');
    } catch (e) { Alert.alert('⚠️', '无法连接服务器，请确认手机与电脑在同一 WiFi'); }
  };

  const doAction = async (action, label) => {
    setBusy(true); setSys(`⏳ ${label} 执行中...（可能需要几分钟）`);
    try {
      const r = await fetch(`${await getApiBase()}/api/admin/${action}`, { method: 'POST' });
      const d = await r.json();
      setSys((d.ok ? '✅ 完成\n' : '❌ 失败\n') + (d.out || ''));
    } catch (e) { setSys('⚠️ 请求失败，请确认服务器已启动'); }
    setBusy(false);
    loadStatus();
  };

  const Stat = ({ icon, label, value, ok }) => (
    <View style={styles.stat}>
      <Text style={{ fontSize: 20 }}>{icon}</Text>
      <Text style={styles.statN}>{value}</Text>
      <Text style={styles.statL}>{label}</Text>
      {ok !== undefined ? <Text style={[styles.statOk, ok ? { color: '#1a8a5c' } : { color: '#c0392b' }]}>{ok ? '✅ 就绪' : '❌ 缺失'}</Text> : null}
    </View>
  );

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={onClose}>
      <View style={styles.root}>
        <ArchHeader title="🖥 管理控制台" subtitle="ADMIN" zh="系统 · 内容 · AI · 控制" />
        <View style={styles.tabs}>
          {[['dash', '📊 仪表盘'], ['data', '📚 内容'], ['ai', '🤖 AI'], ['users', '👥 用户'], ['codes', '🔑 激活码'], ['sys', '⚙️ 系统']].map(([k, l]) => (
            <TouchableOpacity key={k} style={[styles.tab, tab === k && styles.tabOn]} onPress={() => setTab(k)}>
              <Text style={[styles.tabTxt, tab === k && styles.tabTxtOn]}>{l}</Text>
            </TouchableOpacity>
          ))}
        </View>
        <ScrollView style={styles.body} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
          {tab === 'dash' ? (
            <View style={styles.grid}>
              {status ? (
                <>
                  <Stat icon="🕐" label="当前时间" value={status.time} />
                  <Stat icon="💾" label="磁盘可用" value={(status.disk_free_gb || '?') + ' GB'} />
                  <Stat icon="💬" label="句子" value={status.categorized} />
                  <Stat icon="📜" label="圣训" value={status.hadith_all} />
                  <Stat icon="📜" label="历史文章" value={status.history} />
                  <Stat icon="💬" label="对话场景" value={status.dialogues} />
                  <Stat icon="🗣" label="语音识别" value={status.asr_model ? '✅' : '❌'} ok={status.asr_model} />
                  <Stat icon="🎵" label="音乐生成" value={status.music_model ? '✅' : '❌'} ok={status.music_model} />
                </>
              ) : <Text style={styles.err}>⚠️ 无法连接服务器（请确认电脑 App/服务器运行中，且手机与电脑同一 WiFi）</Text>}
            </View>
          ) : null}

          {tab === 'data' ? (
            <View>
              <View style={styles.kindRow}>
                {KINDS.map(([k, l]) => (
                  <TouchableOpacity key={k} style={[styles.kindBtn, kind === k && styles.kindBtnOn]} onPress={() => loadData(k)}>
                    <Text style={[styles.kindTxt, kind === k && styles.kindTxtOn]}>{l}</Text>
                  </TouchableOpacity>
                ))}
              </View>
              <View style={styles.searchRow}>
                <TextInput style={styles.search} placeholder="🔍 搜索..." value={q} onChangeText={setQ} placeholderTextColor="#9aa88f" />
                <TouchableOpacity style={styles.searchBtn} onPress={() => loadData(kind)}>
                  <Text style={styles.searchBtnTxt}>搜索</Text>
                </TouchableOpacity>
              </View>
              <Text style={styles.total}>共 {total} 条</Text>
              {busy ? <ActivityIndicator style={{ marginTop: 20 }} color={Colors.goldDark} /> : null}
              {items.map((it, i) => (
                <View key={i} style={styles.item}>
                  <Text style={styles.itemAr} numberOfLines={1}>{it.ar || ''}</Text>
                  <Text style={styles.itemZh} numberOfLines={1}>{it.zh || ''}</Text>
                </View>
              ))}
            </View>
          ) : null}

          {tab === 'ai' ? (
            <View>
              <Text style={styles.label}>🤖 AI 系统提示词（决定 AI 角色与行为）</Text>
              <TextInput style={styles.aiInput} multiline value={aiSystem} onChangeText={setAiSystem} placeholderTextColor="#9aa88f" />
              <View style={styles.aiRow}>
                <Text style={styles.label}>最大回答（词元）：</Text>
                <TextInput style={styles.tokenInput} value={aiTokens} onChangeText={setAiTokens} keyboardType="numeric" />
              </View>
              <TouchableOpacity style={styles.saveBtn} onPress={saveAI}>
                <Text style={styles.saveTxt}>💾 保存 AI 设置</Text>
              </TouchableOpacity>
              <Text style={styles.hint}>⚠️ 修改后需重启服务器（桌面 App 重启）生效</Text>
            </View>
          ) : null}

          {tab === 'users' ? (
            <View>
              <Text style={styles.label}>👥 用户管理（点击用户设置会员）</Text>
              <TouchableOpacity style={styles.refreshBtn} onPress={loadUsers}>
                <Text style={styles.refreshTxt}>🔄 刷新用户列表</Text>
              </TouchableOpacity>
              {users.length === 0 ? <Text style={styles.err}>暂无用户</Text> : null}
              {users.map((u, i) => (
                <TouchableOpacity key={i} style={styles.userRow} onPress={() => setVip(u.username)}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.userName}>👤 {u.username}</Text>
                    <Text style={styles.userMeta}>
                      {u.vip ? `👑 会员 · 至 ${u.vip_until}` : '普通用户'} · 注册于 {u.created}
                    </Text>
                  </View>
                  <Text style={styles.userGo}>{u.vip ? '👑' : '💎'} 设置</Text>
                </TouchableOpacity>
              ))}
              <Text style={styles.hint}>💡 点击用户 → 选择开通天数（30/90/365 天）或取消会员</Text>
            </View>
          ) : null}

          {tab === 'codes' ? (
            <View>
              <Text style={styles.label}>🔑 激活码管理（生成后发给付费用户）</Text>
              <View style={styles.kindRow}>
                <TouchableOpacity style={styles.kindBtn} onPress={() => genCodes(30)}>
                  <Text style={styles.kindTxt}>生成 30 天 × 5</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.kindBtn} onPress={() => genCodes(90)}>
                  <Text style={styles.kindTxt}>生成 90 天 × 5</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.kindBtn} onPress={() => genCodes(365)}>
                  <Text style={styles.kindTxt}>生成 365 天 × 5</Text>
                </TouchableOpacity>
              </View>
              <TouchableOpacity style={styles.refreshBtn} onPress={loadCodes}>
                <Text style={styles.refreshTxt}>🔄 刷新码列表</Text>
              </TouchableOpacity>
              {codes.length === 0 ? <Text style={styles.err}>暂无激活码</Text> : null}
              {codes.map((c, i) => (
                <View key={i} style={[styles.userRow, { flexDirection: 'row', alignItems: 'center' }]}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.userName}>{c.code}</Text>
                    <Text style={styles.userMeta}>
                      {c.days} 天 · {c.used ? `已用（${c.used_by} ${c.used_at}）` : '✅ 未使用'}
                    </Text>
                  </View>
                  <Text style={[styles.userGo, { color: c.used ? '#c0392b' : '#1a8a5c' }]}>{c.used ? '已用' : '可用'}</Text>
                </View>
              ))}
              <Text style={styles.hint}>💡 收款后把激活码发给用户，用户 App 内「我的 → 开通 VIP」输入兑换</Text>
            </View>
          ) : null}

          {tab === 'sys' ? (
            <View>
              <TouchableOpacity style={[styles.sysBtn, busy && { opacity: 0.5 }]} onPress={() => doAction('rebuild', '重建数据')} disabled={busy}>
                <Text style={styles.sysTxt}>🔄 重建全部数据（句子/圣训/网页）</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.sysBtn, styles.sysBtnGold, busy && { opacity: 0.5 }]} onPress={() => doAction('scraper', '爬虫')} disabled={busy}>
                <Text style={styles.sysTxtGold}>🕷 立即运行内容爬虫</Text>
              </TouchableOpacity>
              <View style={styles.out}>
                <Text style={styles.outTxt}>{sys || '点击按钮执行操作，输出显示在这里'}</Text>
              </View>
            </View>
          ) : null}
        </ScrollView>
        <View style={styles.footer}>
          <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
            <Text style={styles.closeTxt}>✕ 关闭</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.bg },
  tabs: { flexDirection: 'row', gap: 6, paddingHorizontal: 16, paddingTop: 10, flexWrap: 'wrap' },
  tab: { backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 7 },
  tabOn: { backgroundColor: Colors.greenDark, borderColor: Colors.greenDark },
  tabTxt: { fontSize: 11.5, fontWeight: '800', color: Colors.greenDark },
  tabTxtOn: { color: Colors.gold },
  body: { flex: 1 },
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8 },
  stat: { width: '48%', backgroundColor: '#fff', borderRadius: 12, padding: 12, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,.22)' },
  statN: { fontSize: 19, fontWeight: '800', color: Colors.greenDark, marginTop: 3 },
  statL: { fontSize: 10, color: Colors.muted, marginTop: 2 },
  statOk: { fontSize: 10.5, fontWeight: '700', marginTop: 2 },
  err: { fontSize: 12, color: '#c0392b', lineHeight: 19 },
  kindRow: { flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginBottom: 10 },
  kindBtn: { backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 8, paddingHorizontal: 10, paddingVertical: 6 },
  kindBtnOn: { backgroundColor: Colors.greenDark },
  kindTxt: { fontSize: 11, fontWeight: '700', color: Colors.greenDark },
  kindTxtOn: { color: Colors.gold },
  searchRow: { flexDirection: 'row', gap: 8, marginBottom: 8 },
  search: { flex: 1, backgroundColor: '#fff', borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8, fontSize: 12.5, borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', color: Colors.ink },
  searchBtn: { backgroundColor: Colors.gold, borderRadius: 10, paddingHorizontal: 16, justifyContent: 'center' },
  searchBtnTxt: { fontSize: 12, fontWeight: '800', color: Colors.greenDark },
  total: { fontSize: 11, color: Colors.muted, marginBottom: 6 },
  item: { flexDirection: 'row', gap: 10, paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: 'rgba(201,168,76,.12)' },
  itemAr: { flex: 1, fontFamily: 'serif', fontWeight: '700', color: Colors.greenDark, fontSize: 12 },
  itemZh: { flex: 1, color: '#666', fontSize: 11.5 },
  label: { fontSize: 12.5, fontWeight: '800', color: Colors.greenDark, marginTop: 12, marginBottom: 6 },
  aiInput: { backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', padding: 12, fontSize: 12, color: Colors.ink, minHeight: 180, textAlignVertical: 'top', lineHeight: 19 },
  aiRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  tokenInput: { backgroundColor: '#fff', borderRadius: 10, borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', paddingHorizontal: 12, paddingVertical: 8, fontSize: 13, width: 90, color: Colors.ink },
  saveBtn: { backgroundColor: Colors.gold, borderRadius: 12, paddingVertical: 12, alignItems: 'center', marginTop: 16 },
  saveTxt: { fontSize: 13.5, fontWeight: '800', color: Colors.greenDark },
  hint: { fontSize: 10, color: '#999', marginTop: 8, lineHeight: 15 },
  sysBtn: { backgroundColor: Colors.greenDark, borderRadius: 12, paddingVertical: 13, alignItems: 'center', marginBottom: 10 },
  sysBtnGold: { backgroundColor: Colors.gold },
  sysTxt: { fontSize: 13, fontWeight: '800', color: Colors.gold },
  sysTxtGold: { fontSize: 13, fontWeight: '800', color: Colors.greenDark },
  out: { backgroundColor: '#0e3529', borderRadius: 12, padding: 12, minHeight: 120 },
  outTxt: { color: '#a8e0b5', fontSize: 10.5, fontFamily: 'monospace', lineHeight: 16 },
  refreshBtn: { backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 10, paddingVertical: 8, alignItems: 'center', marginBottom: 10 },
  refreshTxt: { fontSize: 12, fontWeight: '800', color: Colors.greenDark },
  userRow: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 12, padding: 12, marginBottom: 8, borderWidth: 1, borderColor: 'rgba(201,168,76,.2)' },
  userName: { fontSize: 13.5, fontWeight: '800', color: Colors.greenDark },
  userMeta: { fontSize: 10.5, color: Colors.muted, marginTop: 3 },
  userGo: { fontSize: 12, fontWeight: '800', color: '#a8892e' },
  footer: { padding: 14, borderTopWidth: 1, borderTopColor: 'rgba(201,168,76,.2)' },
  closeBtn: { backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 12, paddingVertical: 11, alignItems: 'center' },
  closeTxt: { fontSize: 13, fontWeight: '700', color: Colors.greenDark },
});

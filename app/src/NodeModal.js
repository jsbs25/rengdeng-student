// ⚡ 高速节点：免费聚合 + 自动测速（多源节点，挑最快的给你）
import React, { useState, useEffect } from 'react';
import {
  View, Text, Modal, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Alert, Clipboard,
} from 'react-native';
import { Colors } from './theme';
import { ArchHeader } from './components';
import { getApiBase } from './api';

export default function NodeModal({ visible, onClose }) {
  const [nodes, setNodes] = useState([]);
  const [count, setCount] = useState(0);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState('');
  const [subUrl, setSubUrl] = useState('');

  const load = async () => {
    setBusy(true); setErr('');
    try {
      const base = await getApiBase();
      const r = await fetch(`${base}/api/nodes`, { cache: 'no-store' });
      const d = await r.json();
      if (d.nodes && d.nodes.length) {
        setNodes(d.nodes);
        setCount(d.count || d.nodes.length);
        setSubUrl(d.sub || '');
      } else {
        setErr(d.error || '暂无节点，请稍后重试');
      }
    } catch (e) { setErr('无法连接服务器，请确认手机与电脑同一 WiFi'); }
    setBusy(false);
  };

  useEffect(() => {
    if (visible) load();
  }, [visible]);

  const copySub = () => {
    if (!subUrl) return;
    Clipboard.setString(subUrl);
    Alert.alert('✅ 已复制', `订阅链接：${subUrl}\n\n粘贴到 Clash Verge / Clash 的「订阅」里即可使用`);
  };

  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <View style={styles.mask}>
        <View style={styles.card}>
          <ArchHeader title="⚡ 高速节点" subtitle="FREE" zh="多源聚合 · 自动测速 · 最快优先" />
          <View style={{ flexDirection: 'row', gap: 8, paddingHorizontal: 16, paddingTop: 6 }}>
            <TouchableOpacity style={styles.btn} onPress={load} disabled={busy}>
              <Text style={styles.btnTxt}>{busy ? '⏳ 刷新中...' : '🔄 重新测速'}</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.btn, styles.btnGold]} onPress={copySub}>
              <Text style={styles.btnTxtGold}>📋 复制订阅链接</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={{ flex: 1, paddingHorizontal: 16, marginTop: 10 }}>
            {busy && nodes.length === 0 ? (
              <View style={{ alignItems: 'center', paddingVertical: 40 }}>
                <ActivityIndicator color="#a8892e" />
                <Text style={styles.hint}>正在聚合免费节点并测速（约 10 秒）...</Text>
              </View>
            ) : null}
            {err ? <Text style={styles.err}>{err}</Text> : null}
            {count > 0 ? (
              <Text style={styles.count}>已聚合 {count} 个免费节点 · 以下是最快的 {nodes.length} 个</Text>
            ) : null}
            {nodes.map((n, i) => (
              <View key={i} style={styles.row}>
                <Text style={styles.rank}>{i + 1}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.name} numberOfLines={1}>{n.name}</Text>
                  <Text style={styles.meta}>{n.server}:{n.port}</Text>
                </View>
                <Text style={styles.fast}>{i < 5 ? '⚡ 快' : ''}</Text>
              </View>
            ))}
            <View style={{ marginTop: 14, paddingBottom: 20 }}>
              <Text style={styles.note}>
                💡 使用方法：复制订阅链接 → 在 Clash Verge（电脑）或 Clash（手机）的「订阅」里粘贴导入 → 选最快节点。
              </Text>
              <Text style={styles.note}>
                ⚠️ 免费节点为公共资源：速度有限、时效几天、勿登录重要账号。
              </Text>
              <Text style={styles.note}>
                🚀 想要真正的高速稳定：有一台云服务器（Vultr/甲骨文免费）就能「一键生成专属节点」。
              </Text>
              <TouchableOpacity
                style={{ backgroundColor: '#0f3d31', borderRadius: 12, paddingVertical: 13, alignItems: 'center', marginTop: 6 }}
                onPress={() => {
                  Alert.alert('🚀 一键生成专属高速节点', '步骤：\n\n1. 购买一台国外服务器（推荐 Vultr 东京，约 ¥43/月；或甲骨文永久免费）\n2. 把电脑桌面「燃灯者一键节点部署.sh」上传到服务器\n3. 执行 bash deploy_node.sh\n4. 完成！复制输出的 vless 链接，粘贴到 Clash 即可使用（高速专属）\n\n需要我帮你买服务器或远程部署？直接跟我说！');
                }}
              >
                <Text style={{ color: '#e8d48b', fontSize: 13, fontWeight: '800' }}>🚀 一键生成专属高速节点（操作说明）</Text>
              </TouchableOpacity>
            </View>
          </ScrollView>

          <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
            <Text style={styles.closeTxt}>✕ 关闭</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  mask: { flex: 1, backgroundColor: 'rgba(6,25,19,.85)', justifyContent: 'center' },
  card: { backgroundColor: '#f7f3ec', margin: 20, borderRadius: 20, height: '82%', overflow: 'hidden' },
  btn: { flex: 1, backgroundColor: '#fff', borderRadius: 11, paddingVertical: 11, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,.35)' },
  btnTxt: { fontSize: 12.5, fontWeight: '800', color: '#0f3d31' },
  btnGold: { backgroundColor: '#a8892e' },
  btnTxtGold: { fontSize: 12.5, fontWeight: '800', color: '#fff' },
  count: { fontSize: 11, color: '#a8892e', marginBottom: 8 },
  row: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderRadius: 11, padding: 10, marginBottom: 6, borderWidth: 1, borderColor: 'rgba(201,168,76,.2)' },
  rank: { width: 24, height: 24, borderRadius: 12, backgroundColor: '#0f3d31', color: '#e8d48b', textAlign: 'center', lineHeight: 24, fontSize: 11, fontWeight: '800', marginRight: 10 },
  name: { fontSize: 12.5, fontWeight: '700', color: '#1c2b26' },
  meta: { fontSize: 10.5, color: '#8a8f8c', marginTop: 2 },
  fast: { fontSize: 11, fontWeight: '800', color: '#1a8a5c' },
  err: { color: '#c0392b', fontSize: 12, textAlign: 'center', paddingVertical: 20 },
  hint: { color: '#8a8f8c', fontSize: 11, marginTop: 10 },
  note: { fontSize: 10.5, color: '#8a8f8c', lineHeight: 17, marginBottom: 6 },
  closeBtn: { backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 12, paddingVertical: 11, alignItems: 'center', margin: 16, marginTop: 0 },
  closeTxt: { fontSize: 13, fontWeight: '800', color: '#0f3d31' },
});

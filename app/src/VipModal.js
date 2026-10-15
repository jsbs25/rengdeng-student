// VIP 开通页面：微信收款码 + 激活码兑换
import React, { useState, useEffect } from 'react';
import {
  View, Text, Modal, ScrollView, TouchableOpacity, StyleSheet, TextInput, Alert, Image,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors } from './theme';
import { ArchHeader } from './components';
import { getApiBase } from './api';

export default function VipModal({ visible, onClose, onActivated, activateOnly }) {
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);
  const [deviceId, setDeviceId] = useState('');
  const [qrUrl, setQrUrl] = useState('');
  const [vip, setVip] = useState(false);
  const [vipUntil, setVipUntil] = useState('');

  useEffect(() => {
    if (!visible) return;
    AsyncStorage.getItem('nur_device_id').then((d) => {
      let id = d;
      if (!id) {
        id = 'd' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
        AsyncStorage.setItem('nur_device_id', id).catch(() => {});
      }
      setDeviceId(id);
    }).catch(() => {});
    AsyncStorage.multiGet(['nur_vip', 'nur_vip_until']).then((pairs) => {
      pairs.forEach(([k, v]) => {
        if (k === 'nur_vip') setVip(v === '1');
        if (k === 'nur_vip_until') setVipUntil(v || '');
      });
    }).catch(() => {});
    getApiBase().then((b) => setQrUrl(b + '/pay_qr.png')).catch(() => {});
  }, [visible]);

  const activate = async () => {
    const c = code.trim().toUpperCase();
    if (!c) { Alert.alert('提示', '请输入激活码'); return; }
    setBusy(true);
    try {
      const r = await fetch(`${await getApiBase()}/api/vip/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: c, device_id: deviceId, token: (await AsyncStorage.getItem('nur_token')) || '' }),
      });
      const d = await r.json();
      if (d.ok) {
        await AsyncStorage.multiSet([['nur_vip', '1'], ['nur_vip_until', (d.msg.match(/至\s*(\S+)/) || ['', ''])[1]]]);
        setVip(true);
        Alert.alert('🎉 开通成功', d.msg);
        if (onActivated) onActivated();
      } else {
        Alert.alert('兑换失败', d.msg || '请检查激活码');
      }
    } catch (e) {
      Alert.alert('⚠️', '无法连接服务器，请确认手机与电脑同一 WiFi');
    }
    setBusy(false);
  };

  return (
    <Modal visible={visible} animationType={activateOnly ? "fade" : "slide"} onRequestClose={() => { if (!activateOnly) onClose(); }}>
      <View style={styles.root}>
        <ArchHeader title={activateOnly ? "🔑 激活账号" : "👑 开通会员"} subtitle="VIP" zh={activateOnly ? "输入激活码解锁全部功能" : "无限 AI · 音乐生成 · 全部功能"} />
        <ScrollView style={styles.body} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
          {/* 当前状态 */}
          <View style={[styles.statusCard, vip && styles.statusCardVip]}>
            <Text style={styles.statusTitle}>{vip ? '👑 尊贵会员' : '当前：普通用户'}</Text>
            <Text style={styles.statusDesc}>
              {vip ? `会员有效期至 ${vipUntil}` : '开通会员解锁全部功能'}
            </Text>
          </View>

          {/* 权益 */}
          <Text style={styles.label}>✨ 会员专属权益</Text>
          <View style={styles.benefitCard}>
            {[
              ['🧞', 'AI 对话无限次（普通用户每日 20 次）'],
              ['🎵', 'AI 阿拉伯音乐生成（会员专属）'],
              ['📜', '全部历史/圣训/经注深度内容'],
              ['⚡', '优先体验新功能'],
            ].map(([ic, txt], i) => (
              <View key={i} style={styles.benefitRow}>
                <Text style={{ fontSize: 16 }}>{ic}</Text>
                <Text style={styles.benefitTxt}>{txt}</Text>
              </View>
            ))}
          </View>

          {/* 微信收款码 */}
          <Text style={styles.label}>💳 微信扫码支付</Text>
          <View style={styles.qrCard}>
            {qrUrl ? (
              <Image source={{ uri: qrUrl }} style={styles.qrImg} resizeMode="contain" />
            ) : (
              <Text style={styles.qrPlaceholder}>🖼 收款码加载中...</Text>
            )}
            <Text style={styles.qrHint}>扫一扫上方二维码付款（如：30 元/月）</Text>
            <Text style={styles.qrHint2}>付款后联系管理员获取激活码，在下方输入开通</Text>
          </View>

          {/* 激活码 */}
          <Text style={styles.label}>🔑 输入激活码开通</Text>
          <TextInput
            style={styles.codeInput}
            placeholder="例如：ABCD-EFGH-JKLM"
            placeholderTextColor="#9aa88f"
            value={code}
            onChangeText={(t) => setCode(t.toUpperCase())}
            autoCapitalize="characters"
          />
          <TouchableOpacity style={[styles.activateBtn, busy && { opacity: 0.6 }]} onPress={activate} disabled={busy}>
            <Text style={styles.activateTxt}>{busy ? '⏳ 兑换中...' : '👑 立即开通会员'}</Text>
          </TouchableOpacity>
          <Text style={styles.hint}>💡 激活码从管理员处获取（付款后发放），每个码限用一次，绑定账号{activateOnly ? "，激活后全部功能解锁" : ""}</Text>
        </ScrollView>
        <View style={styles.footer}>
          {!activateOnly && (
            <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
              <Text style={styles.closeTxt}>✕ 关闭</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.bg },
  body: { flex: 1 },
  statusCard: { backgroundColor: '#fff', borderRadius: 16, borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', padding: 16, alignItems: 'center', marginBottom: 14 },
  statusCardVip: { backgroundColor: 'rgba(201,168,76,.12)', borderColor: '#a8892e' },
  statusTitle: { fontSize: 17, fontWeight: '800', color: '#0f3d31' },
  statusDesc: { fontSize: 12, color: '#8a9c8f', marginTop: 5 },
  label: { fontSize: 13, fontWeight: '800', color: '#0f3d31', marginTop: 14, marginBottom: 8 },
  benefitCard: { backgroundColor: '#fff', borderRadius: 14, borderWidth: 1, borderColor: 'rgba(201,168,76,.2)', padding: 14 },
  benefitRow: { flexDirection: 'row', alignItems: 'center', gap: 10, paddingVertical: 7 },
  benefitTxt: { fontSize: 12.5, color: '#333', flex: 1, lineHeight: 18 },
  qrCard: { backgroundColor: '#fff', borderRadius: 14, borderWidth: 1, borderColor: 'rgba(201,168,76,.2)', padding: 16, alignItems: 'center' },
  qrImg: { width: 200, height: 200, borderRadius: 8, backgroundColor: '#faf7f0' },
  qrPlaceholder: { width: 200, height: 200, textAlign: 'center', textAlignVertical: 'center', color: '#999', fontSize: 12 },
  qrHint: { fontSize: 12, fontWeight: '700', color: '#0f3d31', marginTop: 10 },
  qrHint2: { fontSize: 10.5, color: '#8a9c8f', marginTop: 5 },
  codeInput: {
    backgroundColor: '#fff', borderRadius: 12, borderWidth: 1, borderColor: 'rgba(201,168,76,.35)',
    paddingHorizontal: 14, paddingVertical: 12, fontSize: 15, letterSpacing: 1.5, color: '#0f3d31', fontWeight: '700',
  },
  activateBtn: { backgroundColor: '#a8892e', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 12 },
  activateTxt: { fontSize: 15, fontWeight: '800', color: '#fff' },
  hint: { fontSize: 10.5, color: '#999', marginTop: 12, lineHeight: 16 },
  footer: { padding: 14, borderTopWidth: 1, borderTopColor: 'rgba(201,168,76,.2)' },
  closeBtn: { backgroundColor: '#fff', borderWidth: 1, borderColor: 'rgba(201,168,76,.3)', borderRadius: 12, paddingVertical: 11, alignItems: 'center' },
  closeTxt: { fontSize: 13, fontWeight: '700', color: '#0f3d31' },
});

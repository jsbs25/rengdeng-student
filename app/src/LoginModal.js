// 登录 / 注册界面
import React, { useState } from 'react';
import {
  View, Text, Modal, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform, ActivityIndicator, Alert,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Colors } from './theme';
import { getApiBase } from './api';

export default function LoginModal({ visible, onClose, onLogin }) {
  const [mode, setMode] = useState('login'); // login | register
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (!username.trim() || password.length < 4) {
      Alert.alert('提示', '用户名至少 2 个字符，密码至少 4 位');
      return;
    }
    setBusy(true);
    try {
      const r = await fetch(`${await getApiBase()}/api/auth/${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: username.trim(), password }),
      });
      const d = await r.json();
      if (d.ok) {
        await AsyncStorage.multiSet([
          ['nur_token', d.token],
          ['nur_username', d.username],
          ['nur_vip', d.vip ? '1' : '0'],
          ['nur_vip_until', d.vip_until || ''],
        ]);
        if (onLogin) onLogin(d);
        if (onClose) onClose();
      } else {
        Alert.alert(mode === 'login' ? '登录失败' : '注册失败', d.msg || '请重试');
      }
    } catch (e) {
      Alert.alert('⚠️', '无法连接服务器：请确认手机与电脑在同一 WiFi，且服务器已启动');
    }
    setBusy(false);
  };

  return (
    <Modal visible={visible} animationType="fade" transparent onRequestClose={() => {}}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.mask}>
        <View style={styles.card}>
          <Text style={styles.logo}>🕌</Text>
          <Text style={styles.title}>燃灯者 · حامل المصباح</Text>
          <Text style={styles.sub}>登录后使用全部功能</Text>

          <View style={styles.modeRow}>
            <TouchableOpacity style={[styles.modeBtn, mode === 'login' && styles.modeBtnOn]} onPress={() => setMode('login')}>
              <Text style={[styles.modeTxt, mode === 'login' && styles.modeTxtOn]}>登录</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.modeBtn, mode === 'register' && styles.modeBtnOn]} onPress={() => setMode('register')}>
              <Text style={[styles.modeTxt, mode === 'register' && styles.modeTxtOn]}>注册</Text>
            </TouchableOpacity>
          </View>

          <TextInput
            style={styles.input}
            placeholder="用户名"
            placeholderTextColor="#9aa88f"
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
          />
          <TextInput
            style={styles.input}
            placeholder="密码（至少 4 位）"
            placeholderTextColor="#9aa88f"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />

          <TouchableOpacity style={[styles.submitBtn, busy && { opacity: 0.6 }]} onPress={submit} disabled={busy}>
            {busy ? <ActivityIndicator color="#fff" /> : (
              <Text style={styles.submitTxt}>{mode === 'login' ? '🔑 登 录' : '✨ 注 册'}</Text>
            )}
          </TouchableOpacity>

          <Text style={styles.hint}>
            {mode === 'login' ? '还没有账号？点上方「注册」创建' : '注册后即可使用（普通用户每日 AI 20 次）'}
          </Text>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  mask: { flex: 1, backgroundColor: 'rgba(10,30,22,0.7)', alignItems: 'center', justifyContent: 'center', padding: 24 },
  card: {
    width: '100%', maxWidth: 360, backgroundColor: '#fdf9ee', borderRadius: 22,
    padding: 24, alignItems: 'center', borderWidth: 1, borderColor: 'rgba(201,168,76,.4)',
  },
  logo: { fontSize: 46 },
  title: { fontSize: 17, fontWeight: '800', color: Colors.greenDark, marginTop: 8 },
  sub: { fontSize: 11.5, color: Colors.muted, marginTop: 4, marginBottom: 16 },
  modeRow: { flexDirection: 'row', gap: 8, marginBottom: 14, width: '100%' },
  modeBtn: { flex: 1, paddingVertical: 9, borderRadius: 10, backgroundColor: '#f0ead8', alignItems: 'center' },
  modeBtnOn: { backgroundColor: Colors.greenDark },
  modeTxt: { fontSize: 13, fontWeight: '800', color: Colors.greenDark },
  modeTxtOn: { color: Colors.gold },
  input: {
    width: '100%', backgroundColor: '#fff', borderRadius: 12, borderWidth: 1,
    borderColor: 'rgba(201,168,76,.35)', paddingHorizontal: 14, paddingVertical: 11,
    fontSize: 14, color: Colors.ink, marginBottom: 10,
  },
  submitBtn: {
    width: '100%', backgroundColor: 'linear-gradient' ? Colors.greenDark : Colors.greenDark,
    backgroundColor: Colors.greenDark, borderRadius: 12, paddingVertical: 13, alignItems: 'center', marginTop: 6,
  },
  submitTxt: { fontSize: 15, fontWeight: '800', color: Colors.gold },
  hint: { fontSize: 10.5, color: '#8a9c8f', marginTop: 14, textAlign: 'center', lineHeight: 16 },
});

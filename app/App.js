// 燃灯者 · 手机壳（WebView 壳：直接加载电脑上的新版界面，界面与网页/桌面版完全一致）
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { View, Text, ActivityIndicator, TouchableOpacity, StatusBar, StyleSheet, BackHandler, Platform } from 'react-native';
import { WebView } from 'react-native-webview';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Network from 'expo-network';

const PORT = 8080;
const FALLBACK_IPS = ['192.168.1.116'];
const KEY = 'nur_server_ip';

export default function App() {
  const [base, setBase] = useState(null);
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(true);
  const ref = useRef(null);

  const probe = async (ip, ms) => {
    try {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), ms);
      const r = await fetch('http://' + ip + ':' + PORT + '/', { signal: ctrl.signal });
      clearTimeout(t);
      return !!r && (r.ok || r.status === 200);
    } catch (e) { return false; }
  };

  const discover = useCallback(async () => {
    setBusy(true); setErr('');
    let saved = null;
    try { saved = await AsyncStorage.getItem(KEY); } catch (e) {}

    const ordered = [];
    if (saved) ordered.push(saved);
    FALLBACK_IPS.forEach((ip) => { if (ordered.indexOf(ip) < 0) ordered.push(ip); });

    for (const ip of ordered) {
      if (await probe(ip, 1500)) {
        try { await AsyncStorage.setItem(KEY, ip); } catch (e) {}
        setBase('http://' + ip + ':' + PORT + '/'); setBusy(false); return;
      }
    }

    // 局域网扫描（并发）
    try {
      const info = await Network.getIpAddressAsync();
      const myIp = info && info.indexOf('.') > 0 ? info : null;
      const seg = myIp ? myIp.split('.').slice(0, 3).join('.') : '192.168.1';
      const ips = [];
      for (let i = 1; i <= 80; i++) ips.push(seg + '.' + i);
      for (let s = 0; s < ips.length; s += 20) {
        const batch = ips.slice(s, s + 20);
        const res = await Promise.all(batch.map((ip) => probe(ip, 900).then((ok) => (ok ? ip : null))));
        const hit = res.find((x) => x);
        if (hit) {
          try { await AsyncStorage.setItem(KEY, hit); } catch (e) {}
          setBase('http://' + hit + ':' + PORT + '/'); setBusy(false); return;
        }
      }
    } catch (e) {}

    setBusy(false);
    setErr('没找到电脑上的服务。\n请确认：① 电脑上「燃灯者」在运行；② 手机和电脑连的是同一个 WiFi。\n然后点下面重试。');
  }, []);

  useEffect(() => { discover(); }, [discover]);

  useEffect(() => {
    const sub = BackHandler.addEventListener('hardwareBackPress', () => {
      if (ref.current) { ref.current.goBack(); return true; }
      return false;
    });
    return () => sub.remove();
  }, []);

  if (base) {
    return (
      <View style={styles.fill}>
        <StatusBar barStyle="light-content" backgroundColor="#0f0f0f" />
        <WebView
          ref={ref}
          source={{ uri: base }}
          style={styles.fill}
          originWhitelist={['*']}
          javaScriptEnabled
          domStorageEnabled
          allowsBackForwardNavigationGestures
          pullToRefreshEnabled
          startInLoadingState
          renderLoading={() => (
            <View style={styles.center}><ActivityIndicator size="large" color="#3ea6ff" /></View>
          )}
          onError={() => { setBase(null); setErr('连接中断，请重试。'); }}
        />
      </View>
    );
  }

  return (
    <View style={styles.center}>
      <StatusBar barStyle="light-content" backgroundColor="#0f0f0f" />
      <Text style={styles.logo}>حامل المصباح</Text>
      <Text style={styles.sub}>燃灯者 · 无声却引人归途</Text>
      {busy ? (
        <View style={{ alignItems: 'center', marginTop: 28 }}>
          <ActivityIndicator size="large" color="#3ea6ff" />
          <Text style={styles.hint}>正在查找电脑上的服务…</Text>
        </View>
      ) : (
        <View style={{ alignItems: 'center', marginTop: 20, paddingHorizontal: 28 }}>
          <Text style={styles.err}>{err}</Text>
          <TouchableOpacity style={styles.btn} onPress={discover}>
            <Text style={styles.btnTx}>重试</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  fill: { flex: 1, backgroundColor: '#0f0f0f' },
  center: { flex: 1, backgroundColor: '#0f0f0f', alignItems: 'center', justifyContent: 'center' },
  logo: { color: '#f1f1f1', fontSize: 30, fontWeight: '800', fontFamily: Platform.OS === 'ios' ? 'Geeza Pro' : 'serif' },
  sub: { color: '#aaaaaa', fontSize: 12, marginTop: 6, letterSpacing: 1 },
  hint: { color: '#aaaaaa', marginTop: 12, fontSize: 12 },
  err: { color: '#cccccc', fontSize: 13, lineHeight: 22, textAlign: 'center' },
  btn: { marginTop: 22, backgroundColor: '#3ea6ff', paddingHorizontal: 26, paddingVertical: 11, borderRadius: 999 },
  btnTx: { color: '#0f0f0f', fontWeight: '700', fontSize: 14 },
});

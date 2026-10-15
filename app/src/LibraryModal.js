// 图书馆组件：文章 + 书籍（整本阅读）+ AI 生成文章
// 优先拉取服务器数据，离线自动降级到内置
import React, { useState, useEffect } from 'react';
import {
  View, Text, Modal, FlatList, TouchableOpacity, StyleSheet, ScrollView, ActivityIndicator, Alert,
} from 'react-native';
import * as Speech from 'expo-speech';
import * as Sharing from 'expo-sharing';
import { Asset } from 'expo-asset';
import { speak as ttsSpeak } from './tts';
import { Colors, Radius } from './theme';
import { loadArticles, loadBooks, chatMessage } from './api';
import { useStudyTimer } from './useStudyTimer';

const AI_TOPICS = ['القهوة', 'رمضان', 'السفر', 'الأسرة', 'القدس', 'النيل', 'العلم', 'الربيع'];

export default function LibraryModal({ visible, onClose }) {
  useStudyTimer(visible);
  const [tab, setTab] = useState('articles'); // articles | books
  const [articles, setArticles] = useState([]);
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [aiBusy, setAiBusy] = useState(false);
  const [reading, setReading] = useState(null);
  const [page, setPage] = useState(1);
  const PAGE_LEN = 2500;
  const bodyLen = reading && reading.body ? reading.body.length : 0;
  const pageTotal = Math.max(1, Math.ceil(bodyLen / PAGE_LEN));
  const readingPageBody = reading && reading.body ? reading.body.slice((page - 1) * PAGE_LEN, page * PAGE_LEN) : '';
  const readingPageCn = reading && reading.cn ? reading.cn.slice((page - 1) * PAGE_LEN, page * PAGE_LEN) : ''; // 文章/章节阅读 {title, body, cn}
  const [curBook, setCurBook] = useState(null); // 当前书籍（章节列表）

  useEffect(() => {
    if (visible && articles.length === 0) {
      setLoading(true);
      loadArticles().then(setArticles).finally(() => setLoading(false));
    }
    if (visible && books.length === 0) {
      loadBooks().then(setBooks);
    }
  }, [visible, articles.length, books.length]);

  const speak = async (text) => {
    if (!text) return;
    Speech.stop();
    await ttsSpeak(text.replace(/[\n\r]+/g, ' '), { lang: 'ar-SA', rate: 0.65, onError: () => Alert.alert('朗读失败', 'TTS 语音包不可用，请检查系统文字转语音设置') });
  };

  // AI 生成文章
  const aiWrite = async (topic) => {
    setAiBusy(true);
    try {
      const reply = await chatMessage(`اكتب مقالا قصيرا عن ${topic} بالعربية الفصحى مع الترجمة الصينية في النهاية.`, 'article_' + Date.now());
      const lines = reply.split('\n').filter((l) => l.trim());
      const title = lines[0] && lines[0].length < 40 ? lines[0].replace(/^[#*\s]+/, '') : '✨ ' + topic;
      const body = lines[0] && lines[0].length < 40 ? lines.slice(1).join('\n') : reply;
      const art = { title: '✨ ' + title, body: body || reply, cn: '', ai: true };
      setArticles((a) => [art, ...a]);
      setReading(art);
    } catch (e) {
      Alert.alert('AI 未连接', '请确认 server.py 已运行，AI 才能写文章。');
    }
    setAiBusy(false);
  };

  // 打开内置 PDF 原书（系统阅读器）
  const openPdfBook = async () => {
    try {
      const asset = Asset.fromModule(require('../../assets/books/weipuzhidao.pdf'));
      await asset.downloadAsync();
      const uri = asset.localUri || asset.uri;
      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(uri, {
          mimeType: 'application/pdf',
          dialogTitle: '《为仆之道》',
          UTI: 'com.adobe.pdf',
        });
      } else {
        Alert.alert('无法打开', '当前设备不支持打开 PDF');
      }
    } catch (e) {
      Alert.alert('打开失败', String(e));
    }
  };

  const openBook = (b) => setCurBook(b);
  const openChapter = (b, c, i) => setReading({ title: `${b.title} · ${i + 1}. ${c.t}`, body: c.body, cn: '' });

  const closeAll = () => { setReading(null); setCurBook(null); onClose(); };

  return (
    <Modal visible={visible} animationType="slide" onRequestClose={closeAll}>
      <View style={styles.root}>
        <View style={styles.head}>
          <Text style={styles.headTitle}>📚 图书馆</Text>
          <View style={styles.headTabs}>
            <TouchableOpacity style={[styles.headTab, tab === 'articles' && styles.headTabOn]} onPress={() => { setTab('articles'); setCurBook(null); setReading(null); }}>
              <Text style={[styles.headTabTxt, tab === 'articles' && styles.headTabTxtOn]}>📰 文章</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.headTab, tab === 'books' && styles.headTabOn]} onPress={() => { setTab('books'); setCurBook(null); setReading(null); }}>
              <Text style={[styles.headTabTxt, tab === 'books' && styles.headTabTxtOn]}>📕 书籍 ({books.length})</Text>
            </TouchableOpacity>
          </View>
          <TouchableOpacity onPress={closeAll} style={styles.closeBtn}>
            <Text style={styles.closeTxt}>✕</Text>
          </TouchableOpacity>
        </View>

        {/* 阅读视图（长文分页，每页 2500 字） */}
        {reading ? (
          <View style={styles.body}>
            <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 20 }}>
              <Text style={styles.readTitle}>{reading.title}</Text>
              <View style={styles.articleCard}>
                <Text style={styles.articleAr}>{readingPageBody}</Text>
              </View>
              {reading.cn ? (
                <View style={styles.transCard}>
                  <Text style={styles.transLabel}>🇨🇳 中文翻译</Text>
                  <Text style={styles.transText}>{readingPageCn}</Text>
                </View>
              ) : null}
            </ScrollView>
            <View style={styles.pageBar}>
              <TouchableOpacity style={[styles.pageBtn, page === 1 && styles.pageBtnOff]} disabled={page === 1} onPress={() => setPage(page - 1)}>
                <Text style={styles.pageTxt}>‹ 上一页</Text>
              </TouchableOpacity>
              <Text style={styles.pageInfo}>{page} / {pageTotal}{reading.body && reading.body.length > 2500 ? '' : ''}</Text>
              <TouchableOpacity style={[styles.pageBtn, page >= pageTotal && styles.pageBtnOff]} disabled={page >= pageTotal} onPress={() => setPage(page + 1)}>
                <Text style={styles.pageTxt}>下一页 ›</Text>
              </TouchableOpacity>
            </View>
            <View style={styles.pageTools}>
              <TouchableOpacity style={styles.listenBtn} onPress={() => speak(readingPageBody)}>
                <Text style={styles.listenTxt}>🔊 朗读本页</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.backBtn} onPress={() => setReading(null)}>
                <Text style={styles.backTxt}>← 返回{curBook ? '目录' : '列表'}</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : tab === 'books' && curBook ? (
          // 书籍目录
          <ScrollView style={styles.body} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
            <TouchableOpacity style={styles.backBtn} onPress={() => setCurBook(null)}>
              <Text style={styles.backTxt}>← 返回书籍列表</Text>
            </TouchableOpacity>
            <Text style={styles.bookTitle}>📕 {curBook.title}</Text>
            <Text style={styles.bookAuthor}>👤 {curBook.author}</Text>
            <View style={styles.introCard}><Text style={styles.introTxt}>{curBook.intro_cn}</Text></View>
            <Text style={styles.chapterLabel}>📑 目录（{curBook.chapters.length} 章）</Text>
            {curBook.chapters.map((c, i) => (
              <TouchableOpacity key={i} style={styles.chItem} onPress={() => openChapter(curBook, c, i)}>
                <Text style={styles.chNum}>{i + 1}</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.chTitle}>{c.t}</Text>
                  <Text style={styles.chPreview}>{(c.body || '').slice(0, 50)}...</Text>
                </View>
                <Text style={styles.chGo}>›</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        ) : tab === 'books' ? (
          // 书籍列表 + PDF 原书
          <FlatList
            data={books}
            keyExtractor={(item, i) => String(i)}
            contentContainerStyle={{ padding: 16 }}
            ListHeaderComponent={
              <TouchableOpacity style={styles.pdfCard} onPress={openPdfBook}>
                <Text style={styles.pdfIcon}>📄</Text>
                <View style={{ flex: 1 }}>
                  <Text style={styles.pdfTitle}>《为仆之道》· PDF 原书</Text>
                  <Text style={styles.pdfDesc}>扫描版 219 页 · 点击用系统阅读器打开（保留原版式）</Text>
                </View>
                <Text style={styles.chGo}>›</Text>
              </TouchableOpacity>
            }
            ListEmptyComponent={loading ? <ActivityIndicator style={{ marginTop: 40 }} color={Colors.gold} /> : <Text style={styles.empty}>暂无书籍</Text>}
            renderItem={({ item }) => (
              <TouchableOpacity style={styles.artItem} onPress={() => openBook(item)}>
                <Text style={styles.artTitle}>📕 {item.title}</Text>
                <Text style={styles.artPreview}>👤 {item.author} · {item.chapters.length} 章</Text>
                <Text style={styles.artPreview}>{(item.intro_cn || '').slice(0, 60)}...</Text>
              </TouchableOpacity>
            )}
          />
        ) : (
          // 文章列表 + AI 写文章
          <>
            <View style={styles.aiWrap}>
              <Text style={styles.aiLabel}>✨ AI 写文章</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.aiRow}>
                {AI_TOPICS.map((t, i) => (
                  <TouchableOpacity key={i} style={styles.aiChip} onPress={() => aiWrite(t)} disabled={aiBusy}>
                    <Text style={styles.aiChipTxt}>{aiBusy ? '⏳' : '🧞'} {t}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>

            <FlatList
              data={articles}
              keyExtractor={(item, i) => String(i)}
              contentContainerStyle={{ padding: 16 }}
              ListEmptyComponent={loading ? <ActivityIndicator style={{ marginTop: 40 }} color={Colors.gold} /> : <Text style={styles.empty}>暂无文章</Text>}
              renderItem={({ item }) => (
                <TouchableOpacity style={styles.artItem} onPress={() => setReading(item)}>
                  <Text style={styles.artTitle}>📖 {item.title}</Text>
                  <Text style={styles.artPreview}>{(item.body || '').slice(0, 60)}...</Text>
                  {item.ai ? <Text style={styles.aiTag}>✨ AI 生成</Text> : null}
                </TouchableOpacity>
              )}
            />
          </>
        )}
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: Colors.cream },
  head: {
    backgroundColor: Colors.greenDark, padding: 16, paddingTop: 52,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
  },
  headTitle: { fontSize: 15, fontWeight: '700', color: Colors.goldLight },
  headTabs: { flexDirection: 'row', gap: 6, marginLeft: 10, flex: 1 },
  headTab: { paddingHorizontal: 10, paddingVertical: 5, borderRadius: 12, backgroundColor: 'rgba(255,255,255,0.08)' },
  headTabOn: { backgroundColor: Colors.gold },
  headTabTxt: { fontSize: 10, color: 'rgba(255,255,255,0.7)', fontWeight: '600' },
  headTabTxtOn: { color: '#fff' },
  closeBtn: { width: 34, height: 34, borderRadius: 17, backgroundColor: 'rgba(255,255,255,0.1)', alignItems: 'center', justifyContent: 'center' },
  closeTxt: { fontSize: 15, color: '#fff' },
  body: { flex: 1 },
  aiWrap: { paddingHorizontal: 16, paddingTop: 12 },
  aiLabel: { fontSize: 11, color: Colors.muted, marginBottom: 6, fontWeight: '600' },
  aiRow: { gap: 6, paddingBottom: 4 },
  aiChip: {
    paddingHorizontal: 12, paddingVertical: 7, borderRadius: 15,
    backgroundColor: 'rgba(201,168,76,0.12)', borderWidth: 1, borderColor: 'rgba(201,168,76,0.4)',
  },
  aiChipTxt: { fontSize: 10.5, fontWeight: '700', color: Colors.goldDark },
  artItem: {
    backgroundColor: Colors.white, borderRadius: Radius.md, padding: 14, marginBottom: 8,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)',
  },
  artTitle: { fontSize: 14, fontWeight: '700', color: Colors.greenDark },
  artPreview: { fontSize: 10.5, color: Colors.muted, marginTop: 4 },
  aiTag: { fontSize: 9, color: Colors.goldDark, marginTop: 4, fontWeight: '700' },
  bookTitle: { fontSize: 18, fontWeight: '800', color: Colors.greenDark, marginTop: 8, textAlign: 'center' },
  bookAuthor: { fontSize: 11, color: Colors.muted, textAlign: 'center', marginTop: 4 },
  introCard: { backgroundColor: Colors.white, borderRadius: Radius.md, padding: 12, marginTop: 12, borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)' },
  introTxt: { fontSize: 12, color: Colors.ink, lineHeight: 20 },
  chapterLabel: { fontSize: 11, color: Colors.muted, marginTop: 14, marginBottom: 8, fontWeight: '600' },
  chItem: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: Colors.white,
    borderRadius: Radius.md, padding: 12, marginBottom: 6,
    borderWidth: 1, borderColor: 'rgba(201,168,76,0.12)',
  },
  chNum: { fontSize: 12, fontWeight: '800', color: Colors.goldDark, width: 28, textAlign: 'center' },
  chTitle: { fontSize: 12.5, fontWeight: '600', color: Colors.greenDark },
  chPreview: { fontSize: 9.5, color: Colors.muted, marginTop: 2 },
  chGo: { fontSize: 18, color: Colors.gold, marginLeft: 6 },
  readTitle: { fontSize: 16, fontWeight: '800', color: Colors.greenDark, marginBottom: 10, textAlign: 'center' },
  articleCard: { backgroundColor: Colors.greenDark, borderRadius: Radius.lg, padding: 20, marginBottom: 12 },
  articleAr: {
    fontFamily: 'serif', fontSize: 17, fontWeight: '700', color: Colors.goldLight,
    textAlign: 'center', lineHeight: 30, writingDirection: 'rtl',
  },
  transCard: { backgroundColor: Colors.white, borderRadius: Radius.md, padding: 16, borderWidth: 1, borderColor: 'rgba(201,168,76,0.14)' },
  transLabel: { fontSize: 11, color: Colors.muted, marginBottom: 6 },
  transText: { fontSize: 13, color: Colors.ink, lineHeight: 22 },
  pageBar: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 8, gap: 10 },
  pageBtn: { paddingHorizontal: 14, paddingVertical: 7, borderRadius: 14, backgroundColor: Colors.greenDark },
  pageBtnOff: { opacity: 0.35 },
  pageTxt: { fontSize: 11, fontWeight: '700', color: Colors.goldLight },
  pageInfo: { flex: 1, textAlign: 'center', fontSize: 11, color: Colors.muted },
  pageTools: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingBottom: 14 },
  listenBtn: {
    marginTop: 12, paddingVertical: 12, borderRadius: Radius.md,
    backgroundColor: Colors.gold, alignItems: 'center',
  },
  listenTxt: { fontSize: 13, fontWeight: '700', color: '#fff' },
  backBtn: { marginTop: 4, alignItems: 'center', padding: 8 },
  backTxt: { fontSize: 12, color: Colors.green },
  empty: { textAlign: 'center', color: Colors.muted, marginTop: 40 },
  pdfCard: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: 'rgba(15,61,49,0.05)',
    borderRadius: Radius.md, padding: 14, marginBottom: 12,
    borderWidth: 1.5, borderColor: 'rgba(201,168,76,0.4)', borderStyle: 'dashed',
  },
  pdfIcon: { fontSize: 26, marginRight: 12 },
  pdfTitle: { fontSize: 13.5, fontWeight: '800', color: Colors.greenDark },
  pdfDesc: { fontSize: 10, color: Colors.muted, marginTop: 3 },
});

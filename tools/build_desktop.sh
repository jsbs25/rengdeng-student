#!/bin/bash
# 一键重建「燃灯者」桌面版（Electron）
# 用法: bash tools/build_desktop.sh [输出目录，默认 ~/Desktop]
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$ROOT/app"
ELECTRON_DIR="$APP_DIR/electron"
OUT_DIR="${1:-$HOME/Desktop}"
APP_NAME="燃灯者 - حامل المصباح"
TARGET="$OUT_DIR/${APP_NAME}.app"

echo "▶ 1/5 生成最新网页 → electron/dist/index.html"
python3 "$ROOT/tools/sync_version.py" 2>/dev/null || true
python3 "$ROOT/build_home.py" "$ROOT/arabic_learning.html" >/dev/null
cp "$ROOT/arabic_learning.html" "$ELECTRON_DIR/dist/index.html"
cp -f "$ROOT/manifest.webmanifest" "$ELECTRON_DIR/dist/manifest.webmanifest" 2>/dev/null || true
cp -f "$ROOT/icon-192.png" "$ROOT/icon-512.png" "$ELECTRON_DIR/dist/" 2>/dev/null || true
mkdir -p "$ELECTRON_DIR/dist/data" && cp -f "$ROOT/data/islamic_catalog.json" "$ELECTRON_DIR/dist/data/" 2>/dev/null || true
mkdir -p "$ELECTRON_DIR/dist/assets/imgs" && cp -f "$ROOT/assets/imgs/"*.jpg "$ELECTRON_DIR/dist/assets/imgs/" 2>/dev/null || true
mkdir -p "$ELECTRON_DIR/dist/data/hadith" && cp -f "$ROOT/data/hadith/"*.json "$ELECTRON_DIR/dist/data/hadith/" 2>/dev/null || true
mkdir -p "$ELECTRON_DIR/dist/data" && cp -f "$ROOT/data/tafsir.json" "$ELECTRON_DIR/dist/data/" 2>/dev/null || true
cp -f "$ROOT/data/civ.json" "$ELECTRON_DIR/dist/data/" 2>/dev/null || true
cp -f "$ROOT/data/civ_rulers.json" "$ELECTRON_DIR/dist/data/" 2>/dev/null || true
cp -f "$ROOT/data/islamic_catalog.json" "$ELECTRON_DIR/dist/data/" 2>/dev/null || true
mkdir -p "$ELECTRON_DIR/dist/data/cn_books/t" && cp -f "$ROOT/data/cn_books/index.json" "$ELECTRON_DIR/dist/data/cn_books/" 2>/dev/null || true
echo "   $(du -h "$ELECTRON_DIR/dist/index.html" | cut -f1)"

echo "▶ 2/5 组装 app 资源"
STAGE="$(mktemp -d)/app"
mkdir -p "$STAGE/electron"
cp -R "$ELECTRON_DIR/." "$STAGE/electron/"
VER=$(python3 -c "import re;print(re.search(r\"APP_VERSION = '([^']+)'\", open(r'$ROOT/build_home.py',encoding='utf-8').read()).group(1))")
cat > "$STAGE/package.json" <<JSON
{
  "name": "nur-al-arabiyya-desktop",
  "productName": "حامل المصباح · 燃灯者",
  "version": "$VER",
  "main": "electron/main.js",
  "private": true
}
JSON

echo "▶ 3/5 复制 Electron 运行时（295MB，稍等）"
rm -rf "$TARGET"
mkdir -p "$OUT_DIR"
cp -R "$APP_DIR/node_modules/electron/dist/Electron.app" "$TARGET"
rm -rf "$TARGET/Contents/Resources/default_app.asar"
cp -R "$STAGE" "$TARGET/Contents/Resources/app"

echo "▶ 4/5 写入 Info.plist / 图标"
PLIST="$TARGET/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleName ${APP_NAME}" "$PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName ${APP_NAME}" "$PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier com.nurarabiyya.desktop" "$PLIST" 2>/dev/null || true
/usr/libexec/PlistBuddy -c "Add :NSMicrophoneUsageDescription string 需要麦克风权限，用于阿拉伯语口语陪练（语音识别）" "$PLIST" 2>/dev/null || /usr/libexec/PlistBuddy -c "Set :NSMicrophoneUsageDescription 需要麦克风权限，用于阿拉伯语口语陪练（语音识别）" "$PLIST" 2>/dev/null || true
if [ -d "$APP_DIR/icon.iconset" ]; then
  iconutil -c icns "$APP_DIR/icon.iconset" -o /tmp/nur_icon.icns 2>/dev/null && \
    cp /tmp/nur_icon.icns "$TARGET/Contents/Resources/app.icns" && \
    /usr/libexec/PlistBuddy -c "Set :CFBundleIconFile app.icns" "$PLIST" 2>/dev/null || true
fi

echo "▶ 5/5 ad-hoc 签名"
codesign --force --deep --sign - "$TARGET" >/dev/null 2>&1 || echo "   ⚠️ 签名失败（不影响本地运行）"

echo "✅ 完成: $TARGET"
du -sh "$TARGET"

#!/bin/bash
# 打「燃灯者」iOS 安装包（IPA）
# 依赖：Xcode（完整版，App Store 安装，约 10GB）+ CocoaPods
# 用法：bash tools/build_ipa.sh
# 产出：~/Desktop/燃灯者_ios_未签名.ipa （未签名，用 Sideloadly/AltStore 侧载安装）
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/app"

if ! xcodebuild -version >/dev/null 2>&1; then
  echo "❌ 未检测到完整版 Xcode。请先到 App Store 安装 Xcode，然后运行："
  echo "   sudo xcode-select -s /Applications/Xcode.app/Contents/Developer"
  exit 1
fi

echo "▶ 1/4 生成 iOS 工程（Expo prebuild）"
cd "$APP"
npx expo prebuild -p ios --clean

echo "▶ 2/4 安装 Pods"
cd "$APP/ios" && pod install

echo "▶ 3/4 编译（Release，不签名）"
cd "$APP/ios"
xcodebuild -workspace *.xcworkspace -scheme "$(ls *.xcworkspace | sed 's/.xcworkspace//')" \
  -configuration Release -sdk iphoneos -derivedDataPath build \
  CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY="" \
  build

echo "▶ 4/4 打包 IPA"
APP_PATH=$(find "$APP/ios/build/Build/Products/Release-iphoneos" -maxdepth 1 -name "*.app" | head -1)
if [ -z "$APP_PATH" ]; then echo "❌ 没找到 .app"; exit 1; fi
WORK=$(mktemp -d)
mkdir -p "$WORK/Payload"
cp -R "$APP_PATH" "$WORK/Payload/"
OUT="$HOME/Desktop/燃灯者_ios_未签名.ipa"
rm -f "$OUT"
(cd "$WORK" && zip -qry "$OUT" Payload)
echo "✅ 完成：$OUT"
echo "   安装方式：用 Sideloadly / AltStore / TrollStore 侧载到 iPhone（需要你的 Apple ID 免费签名，7 天有效）"

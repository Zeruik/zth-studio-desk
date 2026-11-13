#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${ZTH_ANDROID_PLATFORM:?Set ZTH_ANDROID_PLATFORM to a directory containing android.jar}"
: "${ZTH_ANDROID_BUILD_TOOLS:?Set ZTH_ANDROID_BUILD_TOOLS to Android build-tools 35.0.0}"
mkdir -p android/out/classes android/out/dex release
"$ZTH_ANDROID_BUILD_TOOLS/aapt2" compile --dir android/res -o android/out/resources.zip
"$ZTH_ANDROID_BUILD_TOOLS/aapt2" link -o android/out/base.apk -I "$ZTH_ANDROID_PLATFORM/android.jar" --manifest android/AndroidManifest.xml -A app android/out/resources.zip
if command -v javac >/dev/null; then
 javac -source 8 -target 8 -classpath "$ZTH_ANDROID_PLATFORM/android.jar" -d android/out/classes android/src/studio/zerotohand/design/MainActivity.java
else
 : "${ZTH_ECJ_JAR:?Set ZTH_ECJ_JAR to the Eclipse ECJ compiler JAR}"
 java -jar "$ZTH_ECJ_JAR" -8 -classpath "$ZTH_ANDROID_PLATFORM/android.jar" -d android/out/classes android/src/studio/zerotohand/design/MainActivity.java
fi
(cd android/out/classes && zip -q -r ../classes.jar .)
"$ZTH_ANDROID_BUILD_TOOLS/d8" --lib "$ZTH_ANDROID_PLATFORM/android.jar" --min-api 28 --output android/out/dex android/out/classes.jar
cp android/out/base.apk android/out/unsigned.apk
(cd android/out/dex && zip -q -u ../unsigned.apk classes.dex)
"$ZTH_ANDROID_BUILD_TOOLS/zipalign" -f -p 4 android/out/unsigned.apk android/out/aligned.apk
# Development APK only. Production upgrades must use the same privately held release key.
if [ ! -f android/out/debug.keystore ]; then
 keytool -genkeypair -keystore android/out/debug.keystore -storepass android -keypass android -alias androiddebugkey -dname 'CN=ZTH Development,O=ZeroToHand Studio,C=CN' -keyalg RSA -keysize 2048 -validity 10000
fi
"$ZTH_ANDROID_BUILD_TOOLS/apksigner" sign --ks android/out/debug.keystore --ks-pass pass:android --out release/ZTH-Design-Studio-1.0.0-Android-preview.apk android/out/aligned.apk
"$ZTH_ANDROID_BUILD_TOOLS/apksigner" verify --verbose release/ZTH-Design-Studio-1.0.0-Android-preview.apk

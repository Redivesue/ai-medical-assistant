#!/bin/bash
# Android SDK 路径配置脚本

echo "正在查找 Android SDK..."

# 检查常见位置
SDK_PATH=""

if [ -d "$HOME/Library/Android/sdk" ]; then
    SDK_PATH="$HOME/Library/Android/sdk"
    echo "✅ 找到 SDK: $SDK_PATH"
elif [ -d "$HOME/Android/Sdk" ]; then
    SDK_PATH="$HOME/Android/Sdk"
    echo "✅ 找到 SDK: $SDK_PATH"
else
    echo "❌ 未找到 Android SDK"
    echo ""
    echo "请选择："
    echo "1. 如果已安装 Android Studio，请打开 Android Studio -> Preferences -> Android SDK，查看 SDK Location"
    echo "2. 如果未安装，请先安装 Android Studio: https://developer.android.com/studio"
    echo ""
    read -p "请输入你的 Android SDK 路径（或按 Enter 跳过）: " SDK_PATH
fi

if [ -n "$SDK_PATH" ] && [ -d "$SDK_PATH" ]; then
    # 创建 local.properties
    echo "sdk.dir=$SDK_PATH" > local.properties
    echo "✅ 已创建 local.properties"
    echo "SDK 路径: $SDK_PATH"
    echo ""
    echo "现在可以运行: ./gradlew assembleRelease"
else
    echo "⚠️  未配置 SDK 路径"
    echo "请手动编辑 local.properties 文件，设置正确的 sdk.dir 路径"
fi

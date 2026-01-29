# Android SDK 配置指南

## 问题
构建时出现错误：`SDK location not found`

## 解决方案

### 方法 1：使用 Android Studio（推荐，最简单）

1. **下载并安装 Android Studio**
   - 访问：https://developer.android.com/studio
   - 下载 macOS 版本并安装

2. **打开项目**
   - 打开 Android Studio
   - 选择 `File` -> `Open`
   - 选择 `andriod_app` 目录
   - Android Studio 会自动创建 `local.properties` 并配置 SDK 路径

3. **在 Android Studio 中构建**
   - 点击 `Build` -> `Build Bundle(s) / APK(s)` -> `Build APK(s)`
   - 或使用菜单：`Build` -> `Generate Signed Bundle / APK`

### 方法 2：手动配置 SDK 路径

如果你已经安装了 Android SDK（通过 Android Studio 或其他方式）：

1. **找到 SDK 路径**
   ```bash
   # 常见位置：
   ~/Library/Android/sdk          # macOS Android Studio 默认
   ~/Android/Sdk                  # 其他安装方式
   ```

2. **创建 local.properties 文件**
   ```bash
   cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/andriod_app
   
   # 编辑 local.properties，设置正确的路径
   echo "sdk.dir=/Users/hanwu/Library/Android/sdk" > local.properties
   ```
   
   **注意**：将 `/Users/hanwu/Library/Android/sdk` 替换为你的实际 SDK 路径

3. **验证配置**
   ```bash
   ./gradlew assembleRelease
   ```

### 方法 3：只安装命令行工具（不安装完整 Android Studio）

如果你只需要构建 APK，不想安装完整的 Android Studio：

1. **下载命令行工具**
   ```bash
   # 访问：https://developer.android.com/studio#command-tools
   # 下载 "Command line tools only" (macOS)
   ```

2. **解压并设置**
   ```bash
   # 解压到某个目录，例如：
   mkdir -p ~/android-sdk
   unzip commandlinetools-mac-*.zip -d ~/android-sdk
   
   # 创建 local.properties
   echo "sdk.dir=$HOME/android-sdk" > local.properties
   ```

3. **安装必要的 SDK 组件**
   ```bash
   # 需要安装 SDK Platform 和 Build Tools
   # 可以通过 Android Studio 的 SDK Manager 安装
   ```

## 快速检查

检查 SDK 是否已安装：

```bash
# 检查常见位置
ls -d ~/Library/Android/sdk 2>/dev/null && echo "✅ Found SDK" || echo "❌ SDK not found"

# 如果找到，创建 local.properties
if [ -d "$HOME/Library/Android/sdk" ]; then
    echo "sdk.dir=$HOME/Library/Android/sdk" > local.properties
    echo "✅ Created local.properties"
fi
```

## 推荐方案

**最简单的方式**：安装 Android Studio，然后用它打开项目。Android Studio 会自动处理所有配置。

## 构建 APK

配置好 SDK 后，运行：

```bash
cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/andriod_app
./gradlew assembleRelease
```

APK 文件将生成在：
```
app/build/outputs/apk/release/app-release.apk
```

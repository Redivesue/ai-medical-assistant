# 红蜘蛛AI医疗助手 - Android App

## 项目结构

```
android_app/
├── app/
│   ├── src/main/
│   │   ├── java/com/yourname/medbot/
│   │   │   ├── MainActivity.kt      # 主聊天界面
│   │   │   ├── ApiClient.kt        # 调用后端 HTTP
│   │   │   ├── ChatAdapter.kt      # 消息列表适配器
│   │   │   └── model/              # 请求/响应数据类
│   │   │       ├── ChatRequest.kt
│   │   │       ├── ChatResponse.kt
│   │   │       └── ChatMessage.kt
│   │   └── res/                    # 布局、图标、颜色
│   │       ├── layout/
│   │       ├── drawable/
│   │       └── values/
│   └── build.gradle
├── build.gradle
├── settings.gradle
└── gradle.properties
```

## 环境要求

- Android Studio Hedgehog (2023.1.1) 或更高版本
- JDK 8 或更高版本
- Android SDK API 24+ (Android 7.0+)
- Gradle 8.2+

## 快速开始

### 1. 在 Android Studio 中打开项目

1. 打开 Android Studio
2. 选择 `File` -> `Open`
3. 选择 `android_app` 目录
4. 等待 Gradle 同步完成

### 2. 配置后端 API 地址

编辑 `app/src/main/java/com/yourname/medbot/ApiClient.kt`：

```kotlin
companion object {
    // 本地开发（模拟器）: "http://10.0.2.2:8000"
    // 本地开发（真机）: "http://192.168.x.x:8000" (替换为你的电脑IP)
    // 生产环境: "https://your-render-app.onrender.com"
    private const val BASE_URL = "https://your-render-app.onrender.com"
}
```

**本地测试配置：**
- **Android 模拟器**：使用 `http://10.0.2.2:8000`（10.0.2.2 是模拟器访问宿主机 localhost 的特殊地址）
- **真机测试**：
  1. 确保手机和电脑在同一 WiFi 网络
  2. 在电脑上运行后端：`cd backend && ./run_local.sh`
  3. 查看电脑的 IP 地址（macOS: `ifconfig | grep "inet "`，Windows: `ipconfig`）
  4. 将 `BASE_URL` 设置为 `http://你的电脑IP:8000`

### 3. 修改包名（可选）

如果需要修改包名 `com.yourname.medbot`：

1. 在 Android Studio 中右键点击 `com.yourname.medbot` 包
2. 选择 `Refactor` -> `Rename`
3. 输入新的包名
4. 同步更新 `AndroidManifest.xml` 和 `build.gradle` 中的包名

### 4. 运行应用

1. 连接 Android 设备或启动模拟器
2. 点击 `Run` 按钮（绿色三角形）或按 `Shift+F10`
3. 等待应用安装并启动

## 功能说明

### 已实现功能

- ✅ 聊天界面（用户消息和 AI 回复）
- ✅ 发送问题到后端 API
- ✅ 显示加载状态（"红蜘蛛正在思考中..."）
- ✅ 错误处理（网络错误、API 错误）
- ✅ 紧急症状检测（高危症状会显示特殊样式和提示）
- ✅ 消息列表自动滚动

### 消息类型

- **用户消息**：右侧显示，橙色背景
- **AI 消息**：左侧显示，灰色背景
- **加载消息**：左侧显示，灰色背景，斜体
- **错误消息**：左侧显示，红色背景
- **紧急提示**：左侧显示，橙红色背景，加粗

## 依赖库

- **Retrofit 2.9.0** - HTTP 客户端
- **Gson** - JSON 序列化/反序列化
- **Kotlin Coroutines** - 异步处理
- **Material Design Components** - UI 组件

## 构建和打包

### Debug 版本

```bash
./gradlew assembleDebug
```

生成的 APK 位置：`app/build/outputs/apk/debug/app-debug.apk`

### Release 版本

1. 生成签名密钥（首次需要）：
```bash
keytool -genkey -v -keystore medbot-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias medbot
```

2. 在 `app/build.gradle` 中配置签名信息

3. 构建 Release APK：
```bash
./gradlew assembleRelease
```

## 常见问题

### 1. 网络请求失败

- 检查后端服务是否运行
- 检查 `BASE_URL` 配置是否正确
- 检查手机/模拟器网络连接
- 真机测试时确保手机和电脑在同一网络

### 2. 编译错误

- 确保 Gradle 同步完成
- 检查 Android SDK 版本是否正确
- 清理并重新构建：`./gradlew clean build`

### 3. 应用崩溃

- 查看 Logcat 日志：`View` -> `Tool Windows` -> `Logcat`
- 检查网络权限是否已添加（已在 AndroidManifest.xml 中配置）

## 后续开发建议

1. **添加更多 UI 优化**：
   - 消息发送时间显示
   - 消息复制功能
   - 语音输入（可选）
   - 快捷症状按钮

2. **添加功能**：
   - 历史对话记录
   - 离线缓存
   - 推送通知（可选）

3. **性能优化**：
   - 图片加载优化（如果后续添加图片）
   - 列表滚动优化
   - 网络请求缓存

## 联系与支持

如有问题，请查看后端 API 文档或联系开发团队。

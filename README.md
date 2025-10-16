<!-- markdownlint-disable MD033 MD041 -->
<p align="center">
  <img alt="LOGO" src="https://cdn.jsdelivr.net/gh/MaaAssistantArknights/design@main/logo/maa-logo_512x512.png" width="256" height="256" />
</p>

<div align="center">

# Maa-CIYUANJI

</div>

次元姬小说助手 - 基于MaaFramework + PySide6实现次元姬小说app签到及小说内容识别保存到本地

本项目是基于 [MaaFramework](https://github.com/MaaXYZ/MaaFramework) 开发的次元姬小说助手，可以实现次元姬小说app的自动签到以及小说内容的识别和保存。

> **MaaFramework** 是基于图像识别技术、运用 [MAA](https://github.com/MaaAssistantArknights/MaaAssistantArknights) 开发经验去芜存菁、完全重写的新一代自动化黑盒测试框架。
> 低代码的同时仍拥有高扩展性，旨在打造一款丰富、领先、且实用的开源库，助力开发者轻松编写出更好的黑盒测试程序，并推广普及。

## 功能特性

- 自动签到获取代币
- 小说内容自动识别与保存
- 多设备协同识别，避免重复处理
- 章节内容一键导出为TXT文件
- 友好的PySide6图形界面
- 完整的日志记录和日志文件
- MAA框架设备检测与管理

## 即刻开始

- [📄 快速开始](https://github.com/MaaXYZ/MaaFramework/blob/main/docs/zh_cn/1.1-%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B.md)
- [🎞️ 视频教程](https://www.bilibili.com/video/BV1yr421E7MW)

## 环境配置

1. 确保已安装conda，并创建了名为`Maa-WJDR`的虚拟环境

2. 克隆本项目及子项目：

    ```bash
    git clone https://github.com/MaaXYZ/MaaPracticeBoilerplate.git
    ```

3. 下载 MaaFramework 的 [Release 包](https://github.com/MaaXYZ/MaaFramework/releases)，解压到 `deps` 文件夹中。

4. 下载通用资源子模块（MaaCommonAssets）

    ```bash
    git submodule update --init --recursive
    ```

    请注意，子模块仓库体积较大，请确认您已经成功下载，否则后续 OCR（文字识别）将报错并无识别结果。  
    若 git 命令始终无法成功下载，也可尝试前往 [Mirror酱](https://mirrorchyan.com/zh/projects?rid=MaaCommonAssets&source=ghtempl-readme) 手动下载后解压到 `assets/MaaCommonAssets` 文件夹中，目录结构为 `assets/MaaCommonAssets/OCR`。

5. 配置资源文件：

    ```bash
    python ./configure.py
    ```

    若报错 `File Not Found: XXXXXX`，则说明上一步 MaaCommonAssets 未正常下载，请再次检查！

6. 安装PySide6：

    ```bash
    conda activate Maa-WJDR
    pip install PySide6
    ```

## 如何使用

1. 运行主程序：

    ```bash
    conda activate Maa-WJDR
    python main.py
    ```

2. 在界面中设置目标小说及章节范围

3. 点击"签到"获取代币

4. 点击"识别小说"开始处理小说内容

5. 处理完成后可点击"导出小说"将内容保存为TXT文件

## 项目结构

```
Maa-CIYUANJI/
├── agent/                  # MaaFramework代理模块
│   ├── main.py             # 代理主程序
│   ├── my_action.py        # 自定义动作
│   └── my_reco.py          # 自定义识别
├── assets/                 # 资源文件
├── logs/                   # 日志文件目录
├── novels/                 # 小说内容保存目录
├── config_manager.py       # 配置管理模块
├── device_manager.py       # 设备管理模块
├── logger.py               # 日志管理模块
├── novel_processor.py      # 小说处理模块
├── main_ui.py              # 主界面模块
├── main.py                 # 稨序入口
├── config.json             # 用户配置文件
├── stats.json              # 运行状态文件
├── devices.json            # 设备配置文件
└── README.md               # 说明文档
```

## 代币机制

- 代币有三个属性：数量、过期时间、余额
- 每天签到可获得代币，有效期为7天
- 使用代币购买付费章节时，优先扣除距离过期时间最短的代币

## 多设备协同

- 支持多个设备同时识别同一本小说
- 每个设备只处理未被其他设备处理过的章节
- 通过状态文件记录每个章节由哪个设备处理

## 生态共建

MAA 正计划建设为一类项目，而非舟的单一软件。

若您的项目依赖于 MaaFramework，我们欢迎您将它命名为 MaaXXX, MXA, MAX 等等。当然，这是许可而不是限制，您也可以自由选择其他与 MAA 无关的名字，完全取决于您自己的想法！

同时，我们也非常欢迎您提出 PR，在 [社区项目列表](https://github.com/MaaXYZ/MaaFramework#%E7%A4%BE%E5%8C%BA%E9%A1%B9%E7%9B%AE) 中添加上您的项目！

## FAQ

### 0. 我是第一次使用 git，这是什么？视频演示中那个黑框框命令行哪来的？

黑框框是 git bash，几乎任何现代软件的开发都离不开 git，建议先参考 [菜鸟教程](https://www.runoob.com/git/git-install-setup.html) 或搜索一些视频，学习完 git 后再来进行后续开发工作。

### 1. 我是第一次使用 Python，在命令行输入 `python ./configure.py` 或 `python -m pip install MaaFW` 之后没有反应？没有报错，也没有提示成功，什么都没有

Win10 或者 Win11 系统自带了一份 "Python"，但它其实只是一个安装器，是没法用的。  
你需要做的是关闭它或者删除它的环境变量，然后自己去 Python 官网下载并安装一份 Python。  
[参考方法](https://www.bilibili.com/read/cv24692025/)

### 2. 使用 MaaDebugger 或 MaaPicli 时弹窗报错，应用程序错误：应用程序无法正常启动

![缺少运行库](https://github.com/user-attachments/assets/942df84b-f47d-4bb5-98b5-ab5d44bc7c2a)

一般是电脑缺少某些运行库，请安装一下 [vc_redist](https://aka.ms/vs/17/release/vc_redist.x64.exe) 。

### 3. 我在这个仓库里提了 Issue 很久没人回复

这里是《项目模板》仓库，它仅仅是一个模板，一般很少会修改，开发者也较少关注。  
在此仓库请仅提问模板相关问题，其他问题最好前往对应的仓库提出，如果有 log，最好也带上它（`debug/maa.log` 文件）

- MaaFW 本身及 MaaPiCli 的问题：[MaaFramework/issues](https://github.com/MaaXYZ/MaaFramework/issues)
- MaaDebugger 的问题：[MaaDebugger/issues](https://github.com/MaaXYZ/MaaDebugger/issues)
- 不知道算是哪里的、其他疑问等：[讨论区](https://github.com/MaaXYZ/MaaFramework/discussions)

### 4. OCR 文字识别一直没有识别结果，报错 "Failed to load det or rec", "ocrer_ is null"

**请仔细阅读文档**，你无视了前面步骤的报错。我不想解释了，请再把本文档仔细阅读一遍！

## 鸣谢

本项目由 **[MaaFramework](https://github.com/MaaXYZ/MaaFramework)** 强力驱动！

感谢以下开发者对本项目作出的贡献（下面链接改成你自己的项目地址）:

[![Contributors](https://contrib.rocks/image?repo=MaaXYZ/MaaFramework&max=1000)](https://github.com/MaaXYZ/MaaFramework/graphs/contributors)

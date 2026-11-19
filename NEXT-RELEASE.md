# 5.0.1 维护记录与后续计划

5.0.1 已发布：[Release](https://github.com/Zeruik/zth-studio-desk/releases/tag/v5.0.1)。发布标签提交：`14fc1e50cb9607c6bc151a2bdb7ae0118b83b740`。本文件是发布后的文档更新；精确构建输入请使用发布标签。

## 本次改进

嵌入屏幕导出拒绝 Windows 设备名、非法字符及尾随点/空格；后端拒绝当前工程之外的位图资源。Linux TAR/DEB 使用明确的公开读取/执行权限，不继承私有 umask，保留正确配置的 sandbox helper。Windows 后端目录验收使用 realpath 和严格子目录判断；源码审核保留全部二进制属性规则；安装器夹具使用本次构建的图标。

## 已完成验证

同一标签提交的 portable 回归、Linux/macOS 四目标原生启动/重开与交付检查、Windows 完整构建/真实生产程序/内嵌 Python 后端/工程/源码检查/隔离安装器生命周期全部通过。早期本地验证还包括真实 umask 077 DEB 权限检查，及摘要固定的 Linux TAR/DEB 构建。

发布器逐项核对远端大小和 SHA-256 后公开 Release。五个目标平台的九个包和 SHA256SUMS 共十个附件，公开摘要和 Git 标签目标已另行核对。历史版本保留。

发布 CI：https://github.com/Zeruik/zth-studio-desk/actions/runs/44454674653

Windows Setup 未签名，macOS 为 ad-hoc 签名。安装器生命周期测试使用随机 AppId 的合成夹具；它不表示每台既有用户机器的真实升级均已验收。未执行实体设备或真实网站发布。升级前导出工程并备份 data/。

## 后续优先项

备份恢复入口、长任务错误恢复、跨平台数据目录迁移及真实用户机器的升级反馈。

# 下一轮维护计划 / Next maintenance iteration

目标：5.0.1（候选规划，尚未发布；版本字段和旧标签保持当前值）。

## 已实现 / Implemented

嵌入屏幕导出拒绝 Windows 设备名、非法字符和尾随点/空格；后端拒绝不属于当前工程的位图资源。

## 当前云实例验证 / Current cloud validation

10 core groups plus archive-path regression; 13 backend groups; 7 integrated project groups; 11 DOM groups; 4 native integration guards passed using host Python 3.12 (not bundled runtime acceptance).

New portable-regression CI workflows, where present, have not yet been observed running on GitHub. They use synthetic data and do not replace native acceptance.

## 建议优化 / Recommended follow-up

后续优先：备份恢复入口、长任务错误恢复、跨平台数据目录迁移。需分别核验原生内嵌 Python、安装升级与实际桌面交互。

## 发布条件 / Publication gates

先完成对应平台构建与升级/数据保留验收，再同步版本字段、刷新源码清单、为新版本生成附件与 SHA-256 校验。历史 Release、标签和附件不可覆盖。当前 api.github.com 在代理 CONNECT 阶段返回 403，已将该域名加入环境配置草案；草案保存不等于运行时已应用。恢复 API 后还需核验当前用户、仓库权限、既有 Release 和候选标签是否冲突。

本文件记录源码改进和实际执行范围，不表示新版本已经发布，也不将软件/模拟测试称为实板或手机验收。

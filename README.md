# 新奥燃气信息 (xinaogas_info)

基于 [xinaogas](https://github.com/ha0y/xiaomi-gas) 集成数据的 Home Assistant 燃气信息集成，提供燃气余额、阶梯计费、历史用气等信息。

## 功能

- 显示燃气账户余额
- 支持年阶梯气价、月阶梯气价、平均单价三种计费方式
- 显示日/月/年用气历史数据
- 显示抄表数、阀门状态、电池状态等燃气表信息
- 实体数据格式与 state_grid_info 保持一致，兼容同款卡片

## 前置要求

必须先安装并配置 `xinaogas` 集成，本集成从 `xinaogas` 集成读取燃气数据。

## 安装

1. 下载 Release 中的 `xinaogas_info_v1.0.0.zip`
2. 解压到 Home Assistant 的 `custom_components/xinaogas_info/` 目录
3. 重启 Home Assistant
4. 在「设置 → 设备与服务 → 添加集成」中搜索「新奥燃气信息」

## 配置

1. 选择燃气户号（从已配置的 xinaogas 集成中读取）
2. 选择计费标准：
   - 年阶梯气价
   - 月阶梯气价
   - 平均气价
3. 填写对应的阶梯档位和价格

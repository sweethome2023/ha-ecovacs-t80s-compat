# Ecovacs T80S 兼容层

这是一个很小的 Home Assistant 自定义集成，用来补上 **DEEBOT T80S（设备类 `yaj2zg`）** 在旧版 `deebot-client` 中缺失的机型能力。

## 它解决什么问题

HA 2026.10.1 自带的官方 `ecovacs` 集成依赖 `deebot-client==18.6.0`。这个版本里没有 `yaj2zg` 的设备文件，所以日志会出现：

```text
Device class "yaj2zg" not recognized. Please add support for it
Device "DEEBOT T80S" not supported
```

T80S 与 T80s Pro（`9jc32i`）是同一代协议，上游已经把 `yaj2zg` 的能力配置按 `9jc32i` 补齐。本集成在运行时把 `9jc32i` 的能力注册到 `yaj2zg`，然后重载现有的官方 `ecovacs` 配置项；不会替换、复制或修改官方集成。

## 安装

通过 HACS 添加本仓库为 **Integration** 自定义仓库，安装后重启 Home Assistant。

重启后到 **设置 → 设备与服务 → 添加集成**，搜索 **Ecovacs T80S 兼容层** 并添加。添加完成后它会自动重载一次官方 `ecovacs`，T80S 应该会出现 `vacuum`、电量、基站、耗材等实体。

## 适用版本

- HA 2026.10.x（`deebot-client 18.6.0`）
- 也兼容之后仍缺少 `yaj2zg` 的版本；如果官方版本已经自带 `yaj2zg`，则不需要本集成。

## 说明

本集成只做运行时注册，不改官方组件文件，不碰设备硬件。它依赖官方 `ecovacs` 集成和 `deebot-client`，所以必须先把官方 Ecovacs 账号配置好。

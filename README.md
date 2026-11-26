# livecontainer-source

LiveContainer 自用自动更新源。每天 11:00（北京时间）自动检查上游新版本并更新 `apps.json`。

## 添加到 LiveContainer

来源 → `+` → 粘贴：

```
https://raw.githubusercontent.com/ZEERDEER/livecontainer-source/main/apps.json
```

## 包含的应用

| 应用 | 上游 |
| --- | --- |
| GestaltX | huami1314/GestaltX |
| Roam Control | seanhowarthdev/Roam-Control |
| twoyi | twoyi.app/ios/ |
| Tamio | zxfccmm4/tamio |
| WrapPin | suversal/WrapPin |
| Nestvane | atomsprout/nestvane |

## 同步官方源

每天自动拉取以下官方源的全部应用合并进来：

| 官方源 | 应用 |
| --- | --- |
| kolbicz/WQFiles | WQ Files |
| ios151/Insav-releases | INSAV |
| Kianuni/Erosion-CN | Erosion-CN |
| imxieyi/Kernarium | Andarium |
| FrizzleM/SideInstaller | SideInstaller、Nightflix |

WQ Files、INSAV、Erosion-CN、Andarium、SideInstaller 不再需要单独添加官方源，只加这一个源就行。

WQ Files、INSAV、Erosion-CN、Andarium 都有官方源，直接加官方的，不在这里重复收录。

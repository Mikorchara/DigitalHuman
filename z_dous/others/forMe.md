1. 
lappmodel.ts 改动
  _autoIdle = false  ← 从 true 改成 false
  // 【关键改动】false = 不自动循环待机，保持初始姿态一致；true = 自动随机 idle

2. 
默认姿势不是代码定义的，是建模师在 Live2D Cubism Editor 里设定的默认参数值，直接烘焙在 Haru.moc3 二进制文件中。

3. 
没有在运行的（因为没有 idle 动作）：任何肢体动作、转身、表情变化——这些数据全部在 motions/*.motion3.json 里，没被播放就永远效。

4. 






=============================================================================
模型文件结构:

Haru.moc3   :模型本体（二进制），包含所有顶点、网格、骨骼、默认参数值             //默认参数值 是 目前的 待机动作
Haru.model3.json  :总索引，列出纹理/motion/物理/Pose 等文件的路径和各参数分组
Haru.cdi3.json  :参数清单，列出所有可调参数名和分组（如 ParamMouthOpenY 属 ParamGroupMouth）
Haru.physics3.json  :物理模拟，定义头发、衣服的摆动参数
Haru.pose3.json   :姿势约束，限制某些参数的取值范围（防穿模）
Haru.userdata3.json :点击区域 + 事件触发配置                                   //实际闲置中
Haru.2048/      纹理图片（2 张 2048×2048 PNG）
motions/*.motion3.json    逐帧动画数据（Idle 9个 + TapBody 1个）

back_class_normal.png   : 背景
icon_gear.png           : 齿轮图标


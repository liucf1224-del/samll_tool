### 版本打包

#### pyinstall 打包
```
如果是在pyqt里面打包的话就是会有个对应的环境限制要求 对应的包只能在对应的环境下去打包
windows 直接打包
pyinstaller --onefile --windowed --icon=res/Icon1.ico --name="圣诞树桌面" --add-data "res;res" christmas_tree_app_pyqt5.py


mac打包 但是需要在mac上打包
pyinstaller --onefile --windowed --icon=res/Icon1.ico --name="圣诞树" --add-data "res:res" christmas_tree_app_pyqt5.py

```
#### pyqt->pyi 打包
```
使用spec文件自定义打包
pyi-makespec --onefile --windowed --icon=res/Icon1.ico --name="圣诞树" christmas_tree_app_pyqt5.py
对应的操作的结果就是
Wrote D:\samll_tool\圣诞树.spec.
Now run pyinstaller.py to build the executable.
分析当前的依赖
# 查看PyInstaller自动分析出的依赖 这个会打包
pyinstaller --log-level=DEBUG christmas_tree_app_pyqt5.py > analysis.log 2>&1
# 然后查看analysis.log中的"Analyzing"和"Collecting"部分
# 这个是只分析
# 只执行分析阶段，不生成可执行文件
pyi-analyze christmas_tree_app_pyqt5.py --log-level=DEBUG > analysis.log 2>&1

pyinstaller 圣诞树.spec

```

对应的qt的开发的还有比如
delphi 这个是拖拉拽加对应的代码开发的逻辑 理论上是可以一个环境打别的环境的包 但是需要安装别的环境的那种sdk才可以打
但是不是很熟悉的就有点打脑壳  这个应该是编译的打包所以包体不会很大
pyqt限制刚刚也说了 对应的包得在对应的环境下去使用 环境倒是好搭建 这个需要把运行环境的包打进去可能也有点大 但是小于electron应该是
.net  这个也是不太熟悉但是理论上应该也是可以一个环境打别的环境的包这个操作 这个c# 本来也是微软的那种所以打包大概率也不会特别大
electron这个的话就是对应的 vue+套个壳子 这个但是本质是个web端 对应的包打出来会比较臃肿然后体验性可能不是那么那个

按照我的理解的话 包从小到大是 这种嘛 
delphi 或者 .net < pyqt < electron
实际上是

- 打包大小 ：原生编译语言（C++、Delphi） < .NET AOT < PyQt < Electron
- 性能 ：原生编译语言 > .NET AOT > PyQt > Electron
- 开发效率 ：PyQt > .NET MAUI > Delphi > C++ Qt > Electron
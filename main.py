# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。
import sys
from ai3 import ChatWindow, QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())


# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助

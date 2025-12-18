import sys
import json
import re
import html
import logging
from PyQt5.QtCore import Qt, QSettings, QTimer, QUrl
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtGui import QFont, QTextCursor, QColor, QTextCharFormat
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# 配置日志
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# 创建 FileHandler 并设置编码为 utf-8
file_handler = logging.FileHandler('chat_debug.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 设置日志格式
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 添加 handler 到 logger
logger.addHandler(file_handler)

TOKEN_LIMIT = 2500
API_URL = "http://110.40.188.181:11434/api/chat"  # Ollama API地址


class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepSeek-R1 聊天工具")
        self.resize(800, 600)

        # 状态变量
        self.history = []
        self.token_count = 0
        self.is_waiting = False
        self.streaming_response = ""
        self.streaming = False
        self.last_streaming_response = ""
        self.buffer = bytearray()
        self.typing_message_added = False  # 标记是否已添加"正在输入"消息
        self.char_buffer = ""  # 用于累积字符的缓冲区
        self.char_threshold = 5  # 累积多少字符后更新一次UI

        # 网络管理器
        self.network_manager = QNetworkAccessManager()
        self.reply = None

        # 创建UI
        self.init_ui()

        # 加载历史记录
        self.load_history()

        # 添加初始消息
        self.add_message("assistant", "你好！我是DeepSeek-R1，有什么可以帮您的吗？")
        self.update_token_count()

    def init_ui(self):
        # 主部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 聊天区域
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFont(QFont("Microsoft YaHei", 10))
        self.chat_area.document().setDefaultStyleSheet("""
            pre {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
            }
            code {
                background-color: #f5f5f5;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .user-msg { color: #1e3a8a; }
            .assistant-msg { color: #374151; }
            .typing-indicator {
                display: inline-flex;
                align-items: center;
            }
            .typing-dot {
                width: 6px;
                height: 6px;
                background-color: #6366f1;
                border-radius: 50%;
                margin: 0 2px;
                animation: bounce 1.4s infinite ease-in-out both;
            }
            .typing-dot:nth-child(1) { animation-delay: -0.32s; }
            .typing-dot:nth-child(2) { animation-delay: -0.16s; }
            @keyframes bounce {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }
        """)
        main_layout.addWidget(self.chat_area, 5)

        # 摘要区域
        self.summary_area = QTextEdit()
        self.summary_area.setReadOnly(True)
        self.summary_area.setMaximumHeight(100)
        self.summary_area.setFont(QFont("Microsoft YaHei", 9))
        self.summary_area.setStyleSheet("background-color: #f8f8f8; border: 1px solid #e0e0e0;")
        main_layout.addWidget(self.summary_area)

        # 状态栏
        status_layout = QHBoxLayout()
        self.token_label = QLabel(f"当前 Token 使用量: 0/{TOKEN_LIMIT}")
        status_layout.addWidget(self.token_label)

        self.reset_btn = QPushButton("重置对话")
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
            QPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        self.reset_btn.clicked.connect(self.reset_conversation)
        status_layout.addWidget(self.reset_btn)

        main_layout.addLayout(status_layout)

        # 输入区域
        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.setFont(QFont("Microsoft YaHei", 10))
        self.input_field.setMaximumHeight(100)
        self.input_field.textChanged.connect(self.adjust_input_height)
        input_layout.addWidget(self.input_field, 5)

        self.send_btn = QPushButton("发送")
        self.send_btn.setMinimumHeight(60)
        self.send_btn.setStyleSheet("background-color: #6366f1; color: white;")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)

        main_layout.addLayout(input_layout, 1)

        # 底部状态栏
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("已连接 | 模型: deepseek-r1:7b")

    def adjust_input_height(self):
        doc = self.input_field.document()
        height = doc.size().height() + 10
        self.input_field.setMinimumHeight(min(max(int(height), 60), 200))

    def add_message(self, role, content, is_streaming=False):
        self.chat_area.moveCursor(QTextCursor.End)
        cursor = self.chat_area.textCursor()

        # 添加角色标签
        role_format = QTextCharFormat()
        role_format.setFontWeight(QFont.Bold)
        if role == "user":
            role_format.setForeground(QColor("#1e3a8a"))
            cursor.insertText("您: ", role_format)
        else:
            role_format.setForeground(QColor("#374151"))
            cursor.insertText("DeepSeek-R1: ", role_format)

        # 添加消息内容
        if is_streaming:
            # 添加"正在输入"指示器
            typing_html = """
            <div class='typing-indicator'>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
            """
            cursor.insertHtml(typing_html)
            self.typing_message_added = True
        else:
            formatted_content = self.format_message(content, role)
            cursor.insertHtml(formatted_content)

        # 添加换行
        cursor.insertText("\n\n")

        # 滚动到底部
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )

        # 更新摘要
        self.update_summary()

    def update_streaming_message(self, new_content=""):
        """更新流式消息，只更新新增内容"""
        if not self.typing_message_added or not self.streaming:
            return

        # 查找最后一条消息
        cursor = self.chat_area.textCursor()
        cursor.movePosition(QTextCursor.End)

        # 找到最后一条消息的起始位置
        cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.PreviousBlock, QTextCursor.KeepAnchor)

        # 检查是否是助手消息
        if "DeepSeek-R1:" in cursor.selectedText():
            # 移动到消息内容开始位置
            cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.MoveAnchor)
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len("DeepSeek-R1:") + 1)

            # 如果是第一次更新，移除打字指示器
            if self.last_streaming_response == "":
                # 移除打字指示器
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()

            # 追加新内容
            formatted_content = self.format_message(new_content, "assistant")
            cursor.insertHtml(formatted_content)

            # 滚动到底部
            self.chat_area.verticalScrollBar().setValue(
                self.chat_area.verticalScrollBar().maximum()
            )

    def format_message(self, content, role=None):
        # 过滤掉<think>标签及其内容
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        content = content.strip()

        escaped = html.escape(content)

        # 检测代码块
        escaped = re.sub(r'```([\s\S]*?)```',
                         r'<pre>\1</pre>',
                         escaped)

        # 检测行内代码
        escaped = re.sub(r'`([^`]+)`',
                         r'<code>\1</code>',
                         escaped)

        # 替换换行符
        if '<pre>' not in escaped and '<code>' not in escaped:
            escaped = escaped.replace('\n', '<br>')

        # 添加样式类
        if '<pre>' in escaped or '<code>' in escaped:
            return escaped

        if role == "user":
            return f'<span class="user-msg">{escaped}</span>'
        elif role == "assistant":
            return f'<span class="assistant-msg">{escaped}</span>'
        else:
            return escaped

    def send_message(self):
        try:
            message = self.input_field.toPlainText().strip()
            logging.debug(f"【用户输入内容】: {repr(message)}")  # 使用 repr 避免日志记录 Unicode 错误

            if not message or self.is_waiting:
                return

            # 添加到历史记录
            self.history.append({"role": "user", "content": message})

            # 添加到UI
            self.add_message("user", message)

            # 清空输入框
            self.input_field.clear()

            # 更新token计数
            self.update_token_count()

            # 检查token限制
            if self.token_count >= TOKEN_LIMIT:
                QMessageBox.warning(self, "Token 限制", "已达到Token上限，请重置对话")
                return

            # 发送请求
            self.is_waiting = True

            # 初始化流式传输状态
            self.streaming = True
            self.streaming_response = ""
            self.char_buffer = ""
            self.last_streaming_response = ""
            self.buffer = bytearray()
            self.typing_message_added = False

            # 显示正在输入指示器
            self.add_message("assistant", "", is_streaming=True)

            # 准备请求数据
            data = {
                "model": "deepseek-r1:7b",
                "messages": self.history,
                "stream": True
            }
            logging.debug(f"【发送给后端的请求数据】: {data}")

            # 发送网络请求
            request_url = QUrl(API_URL)
            request = QNetworkRequest(request_url)
            request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
            request.setRawHeader(b"Accept", b"text/event-stream")

            # 创建新的网络请求
            self.reply = self.network_manager.post(
                request,
                json.dumps(data).encode('utf-8')
            )
            self.reply.readyRead.connect(self.handle_stream_data)
            self.reply.finished.connect(self.handle_stream_finished)
            self.reply.errorOccurred.connect(self.handle_network_error)

        except Exception as e:
            logging.error(f"发送消息时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            self.is_waiting = False
            self.status_bar.showMessage(f"错误: {str(e)}")

    def handle_network_error(self, code):
        if self.reply:
            error_msg = self.reply.errorString()
            logging.error(f"网络错误 [{code}]: {error_msg}")
            self.status_bar.showMessage(f"网络错误: {error_msg}")
            self.is_waiting = False
            self.streaming = False
            self.typing_message_added = False

    def handle_stream_data(self):
        try:
            if not self.reply or not self.streaming:
                return

            data = self.reply.readAll()
            if data.isEmpty():
                return

            self.buffer.extend(data.data())
            lines = self.buffer.split(b'\n')
            self.buffer = lines.pop()  # 保留不完整行

            # 处理所有完整行
            for line in lines:
                if not line:  # 跳过空行
                    continue

                try:
                    line_str = line.decode('utf-8').strip()
                    if not line_str:
                        continue

                    # 记录原始行，仅当其可能为有效SSE数据时
                    if line_str.startswith("data:"):
                        logging.debug(f"【接收到的 SSE 行】: {repr(line_str)}")  # 使用 repr 避免日志记录 Unicode 错误
                    else:
                        # 可选：记录其他类型的行，用于调试或忽略
                        # logging.debug(f"【非SSE数据行】: {line_str}")
                        pass

                    # 解析JSON并提取内容
                    chunk = json.loads(line_str)
                    content_chunk = chunk.get("message", {}).get("content", "")

                    if content_chunk:
                        # 累积到字符缓冲区
                        self.char_buffer += content_chunk
                        self.streaming_response += content_chunk

                        # 检查是否需要更新UI
                        if (len(self.char_buffer) >= self.char_threshold or
                                any(punct in content_chunk for punct in ['.', '?', '!', '。', '？', '！', '，', ','])):
                            # 更新UI
                            self.update_streaming_message(self.char_buffer)

                            # 更新最后一条消息内容
                            self.last_streaming_response = self.char_buffer

                            # 重置字符缓冲区
                            self.char_buffer = ""

                except json.JSONDecodeError:
                    logging.warning(f"JSON解析失败: {line_str}")
                except Exception as e:
                    logging.error(f"处理行时出错: {e}")

        except Exception as e:
            logging.error(f"处理流数据异常: {e}")

    def handle_stream_finished(self):
        try:
            # 处理缓冲区中剩余的数据
            if self.buffer:
                try:
                    line_str = self.buffer.decode('utf-8', errors='ignore').strip()
                    if line_str:
                        logging.debug(f"【处理缓冲区剩余数据】: {repr(line_str)}")  # 使用 repr 避免日志记录 Unicode 错误

                        # 尝试解析剩余数据
                        try:
                            chunk = json.loads(line_str)
                            content_chunk = chunk.get("message", {}).get("content", "")
                            if content_chunk:
                                self.char_buffer += content_chunk
                                self.streaming_response += content_chunk
                        except:
                            pass  # 忽略解析错误
                except:
                    pass
                self.buffer.clear()

            # 刷新字符缓冲区
            if self.char_buffer:
                self.update_streaming_message(self.char_buffer)
                self.char_buffer = ""

            self.is_waiting = False

            # 确保更新最后的流式消息
            if self.typing_message_added:
                # 移除打字指示器（如果还在）
                cursor = self.chat_area.textCursor()
                cursor.movePosition(QText.End)
                cursor.select(QTextCursor.BlockUnderCursor)
                if "typing-indicator" in cursor.selectedText():
                    cursor.removeSelectedText()

                # 添加最终响应内容
                self.add_message("assistant", self.streaming_response)

            # 添加最终消息到历史记录
            if self.streaming_response:
                # 添加到历史记录（替换临时消息）
                self.history.append({"role": "assistant", "content": self.streaming_response})
                self.update_token_count()
            else:
                if self.reply and self.reply.error() != QNetworkReply.NoError:
                    error_msg = self.reply.errorString()
                    self.history.append({"role": "assistant", "content": f"错误: {error_msg}"})
                    self.status_bar.showMessage(f"错误: {error_msg}")
                else:
                    self.history.append({"role": "assistant", "content": "未收到响应，请重试"})

            # 确保释放资源
            if self.reply and self.reply.isFinished():
                self.reply.deleteLater()
                self.reply = None

        except Exception as e:
            logging.error(f"流完成处理时出错: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_waiting = False
            self.streaming = False
            self.typing_message_added = False
            self.streaming_response = ""
            self.char_buffer = ""
            self.last_streaming_response = ""

    def estimate_tokens(self, text):
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        other_chars = len(text) - chinese_chars - english_chars
        return int(chinese_chars * 1.5 + english_chars * 0.25 + other_chars * 0.5)

    def update_token_count(self):
        self.token_count = 0
        for msg in self.history:
            self.token_count += self.estimate_tokens(msg["content"])

        self.token_label.setText(f"当前 Token 使用量: {self.token_count}/{TOKEN_LIMIT}")

        if self.token_count > TOKEN_LIMIT * 0.9:
            self.token_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.token_label.setStyleSheet("")

    def update_summary(self):
        summary = ""
        for msg in self.history[-5:]:
            role = "用户" if msg["role"] == "user" else "助手"
            content = msg["content"]
            if len(content) > 60:
                content = content[:57] + "..."
            summary += f"<b>{role}:</b> {html.escape(content)}<br>"

        self.summary_area.setHtml(summary)

    def reset_conversation(self):
        if QMessageBox.question(
                self,
                "重置对话",
                "确定要重置对话吗？当前对话历史将被清除",
                QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            self.history = []
            self.chat_area.clear()
            self.summary_area.clear()
            self.token_count = 0
            self.token_label.setText(f"当前 Token 使用量: 0/{TOKEN_LIMIT}")
            self.token_label.setStyleSheet("")
            self.add_message("assistant", "你好！我是DeepSeek-R1，有什么可以帮您的吗？")
            self.save_history()

    def load_history(self):
        settings = QSettings("DeepSeek", "ChatTool")
        history_data = settings.value("history", "[]")
        try:
            self.history = json.loads(history_data)
            for msg in self.history:
                self.add_message(msg["role"], msg["content"])
        except:
            self.history = []

    def save_history(self):
        settings = QSettings("DeepSeek", "ChatTool")
        settings.setValue("history", json.dumps(self.history))

    def closeEvent(self, event):
        try:
            if self.reply:
                self.reply.abort()
                self.reply.deleteLater()

            self.save_history()
        finally:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圣诞树桌面插件 - PyQt5
作者： codeliu
"""

import sys
import math
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QMenu,
                            QSystemTrayIcon, QMessageBox, QAction)
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QObject
from PyQt5.QtGui import (QPixmap, QPainter, QColor, QPen, QBrush, QFont,
                        QIcon, QPolygon)
from PyQt5.QtWidgets import QStyle
import json
import os

try:
    from PyQt5.QtWinExtras import QtWin
    WINDOWS_EXTRAS_AVAILABLE = True
except ImportError:
    WINDOWS_EXTRAS_AVAILABLE = False
    print("警告：PyQt5.WinExtras未安装，某些Windows特定功能可能不可用")


class ParticleSystem(QObject):
    """星星粒子系统 - 直接在主线程中使用定时器更新，避免UI阻塞"""
    position_updated = pyqtSignal(object)  # 发送粒子位置更新信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.running = False
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_particles)
        
    def start_particles(self, particle_count=30):
        """初始化粒子系统"""
        self.particles = []
        for i in range(particle_count):
            # 根据粒子索引调整初始位置，让粒子从Labubu图片上方飘落
            # 新图片人物靠中下，所以粒子初始位置集中在顶部区域
            if i < 90:  # 前90个粒子在图片顶部区域
                y = random.uniform(15, 50)  # 调整为更靠上的位置
            else:  # 后30个粒子在图片中上部区域
                y = random.uniform(50, 100)
            
            particle = {
                'x': random.uniform(50, 200),
                'y': y,
                'vx': random.uniform(-0.3, 0.3),  # 减小横向速度范围，更柔和
                'vy': random.uniform(0.2, 0.8),  # 减小纵向速度范围，飘落更慢
                'size': random.uniform(6, 12),  # 稍微调整大小范围 4, 10
                'alpha': random.uniform(200, 225),# 透明度范围  150, 255 这个是会比较暗淡的那种效果
                'rotation': random.uniform(0, 360),
                'rotation_speed': random.uniform(-60, 60),  # 增加旋转速度，更明显
                'lifetime': random.uniform(4, 10),  # 增加生命周期，飘落更慢
                'age': 0,
                'wind_phase': random.uniform(0, 2 * math.pi)  # 添加风力相位，用于模拟风吹效果
            }
            self.particles.append(particle)
        
        self.running = True
        self.update_timer.start(16)  # ~60 FPS
        
    def stop_particles(self):
        """停止粒子系统"""
        self.running = False
        self.update_timer.stop()
        
    def update_particles(self):
        """更新粒子位置和属性"""
        if not self.running:
            return
            
        updated_positions = []
        
        for particle in self.particles[:]:
            # 更新位置
            # 添加风力效果，让横向速度随时间变化
            # 计算风力影响，使用正弦函数模拟风吹的周期性
            wind_strength = 0.05  # 风力强度
            wind_variation = math.sin(particle['age'] * 2 + particle['wind_phase']) * wind_strength
            
            # 更新横向速度，加入风力影响
            particle['vx'] += wind_variation
            
            # 限制横向速度范围，避免粒子飞得太快
            particle['vx'] = max(-0.5, min(0.5, particle['vx']))
            
            # 更新位置
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['rotation'] += particle['rotation_speed'] * 0.016  # 16ms = 60FPS
            
            # 更新年龄和透明度
            particle['age'] += 0.016
            age_ratio = particle['age'] / particle['lifetime']
            #particle['alpha'] = max(0, 255 * (1 - age_ratio)) #粒子的透明度的变化状态 这个会变的特别暗淡的那种
            particle['alpha'] = max(150, 255 * (1 - age_ratio))
            
            # 粒子生命周期结束，重置
            if particle['age'] >= particle['lifetime']:
                particle['x'] = random.uniform(50, 200)
                # 随机决定重置到顶部还是中间，保持顶部多、中间少的比例
                if random.random() < 0.7:  # 70%的概率重置到顶部区域
                    particle['y'] = random.uniform(15, 50)
                else:  # 30%的概率重置到中上部区域
                    particle['y'] = random.uniform(50, 100)
                particle['vx'] = random.uniform(-0.3, 0.3)  # 减小横向速度范围
                particle['vy'] = random.uniform(0.2, 0.8)  # 减小纵向速度范围
                particle['age'] = 0
                particle['alpha'] = random.uniform(200, 225)  # 重置透明度范围  150, 255 这个是比较暗淡的
                particle['rotation'] = random.uniform(0, 360)
                particle['rotation_speed'] = random.uniform(-60, 60)  # 增加旋转速度
                particle['lifetime'] = random.uniform(4, 10)  # 增加生命周期
                particle['wind_phase'] = random.uniform(0, 2 * math.pi)  # 添加风力相位
                
            # 边界检测 - 底部超出则重置
            if particle['y'] > 400 or particle['x'] < -50 or particle['x'] > 300:
                particle['x'] = random.uniform(50, 200)
                # 随机决定重置到顶部还是中间，保持顶部多、中间少的比例
                if random.random() < 0.7:  # 70%的概率重置到顶部区域
                    particle['y'] = random.uniform(15, 50)
                else:  # 30%的概率重置到中上部区域
                    particle['y'] = random.uniform(50, 100)
                particle['vx'] = random.uniform(-0.3, 0.3)  # 减小横向速度范围
                particle['vy'] = random.uniform(0.2, 0.8)  # 减小纵向速度范围
                particle['rotation'] = random.uniform(0, 360)
                particle['rotation_speed'] = random.uniform(-60, 60)  # 增加旋转速度
                particle['wind_phase'] = random.uniform(0, 2 * math.pi)  # 添加风力相位
                
            updated_positions.append(particle.copy())
            
        # 发送位置更新信号
        self.position_updated.emit(updated_positions)


class TransparentWidget(QWidget):
    """透明窗口基类（PyQt5兼容版）"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置窗口标志（PyQt5兼容方式）
        self.setWindowFlags(Qt.FramelessWindowHint | 
                           Qt.WindowStaysOnTopHint |
                           Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        # 设置窗口透明度
        self.global_alpha = 230  # 90%透明度
        self.setWindowOpacity(self.global_alpha / 255.0)
        
        # 鼠标拖拽支持
        self.dragging = False
        self.drag_start_pos = QPoint()
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            event.ignore()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_pos)
            event.accept()
        else:
            event.ignore()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            event.ignore()


class ChristmasTreeWidget(TransparentWidget):
    """Labubu桌面插件主窗口（PyQt5兼容版）"""
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 400)
        
        # 加载图片资源
        self.load_resources()
        
        # 状态变量
        self.stars_enabled = True
        self.current_garland_frame = 0
        self.garland_frame_count = 4
        self.is_mirrored = False  # 左右镜像状态
        
        # Labubu上下移动动画参数
        self.man_y_offset = 0
        self.man_move_direction = 1  # 1 向下，-1 向上
        self.man_move_speed = 0.5
        self.man_min_y = 50
        self.man_max_y = 70
        
        # 动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(60)  # ~16 FPS
        
        # 星星坐标和速度数组
        self.star_coords = []
        self.star_speeds = []
        for i in range(6):
            self.star_coords.append([0.0, 0.0])  # x, y
            self.star_speeds.append([0.0, 0.0])  # vx, vy
            
        # 初始化星星位置
        self.init_star_positions()
        
        # 粒子系统
        self.particle_system = ParticleSystem()
        self.particle_system.position_updated.connect(self.update_particles)
        self.current_particles = []  # 初始化粒子列表
        
        # 右键菜单
        self.setup_context_menu()
        
        # 加载用户配置
        self.load_config()
        
        # 显示粒子效果
        QTimer.singleShot(1000, lambda: self.particle_system.start_particles(120))
        
        # 设置系统托盘
        self.setup_system_tray()
        
    def setup_system_tray(self):
        """设置系统托盘"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            # 使用自定义图标
            current_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(current_dir, "res", "Icon1.ico")
            
            if os.path.exists(icon_path):
                self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self)
            else:
                # 如果图标不存在，使用系统默认图标
                self.tray_icon = QSystemTrayIcon(self)
                self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
            
            self.tray_icon.setToolTip("Labubu桌面插件")
            
            # 创建托盘菜单
            tray_menu = QMenu()
            
            show_action = QAction("显示Labubu", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            hide_action = QAction("隐藏Labubu", self)
            hide_action.triggered.connect(self.hide)
            tray_menu.addAction(hide_action)
            
            tray_menu.addSeparator()
            
            quit_action = QAction("退出", self)
            quit_action.triggered.connect(self.quit_app)
            tray_menu.addAction(quit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            
    def quit_app(self):
        """退出应用程序"""
        # 停止动画定时器
        if hasattr(self, 'animation_timer') and self.animation_timer.isActive():
            self.animation_timer.stop()
        
        # 停止粒子系统
        if hasattr(self, 'particle_system'):
            self.particle_system.stop_particles()
        
        # 关闭系统托盘
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        
        # 退出应用
        QApplication.quit()  # 增加粒子数量到12个
        
    def get_config_path(self):
        """获取配置文件路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "config.json")
        
    def load_config(self):
        """加载用户配置"""
        config_path = self.get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 恢复透明度设置
                if 'global_alpha' in config:
                    self.global_alpha = config['global_alpha']
                    self.setWindowOpacity(self.global_alpha / 255.0)
                
                # 恢复置顶状态
                if 'topmost' in config:
                    flags = self.windowFlags()
                    if config['topmost']:
                        self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
                    else:
                        self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
                    self.show()
                
                # 恢复特效开关状态
                if 'stars_enabled' in config:
                    self.stars_enabled = config['stars_enabled']
                
                # 恢复左右镜像状态
                if 'is_mirrored' in config:
                    self.is_mirrored = config['is_mirrored']
                    
            except Exception as e:
                print(f"加载配置失败: {e}")
        
    def save_config(self):
        """保存用户配置"""
        config_path = self.get_config_path()
        try:
            config = {
                'global_alpha': self.global_alpha,
                'topmost': bool(self.windowFlags() & Qt.WindowStaysOnTopHint),
                'stars_enabled': self.stars_enabled,
                'is_mirrored': self.is_mirrored
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def load_resources(self):
        """加载图片资源"""
        try:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 检查并创建res目录
            res_dir = os.path.join(current_dir, "res")
            if not os.path.exists(res_dir):
                os.makedirs(res_dir)

            # 加载Labubu图片
            man_path = os.path.join(res_dir, "p_labubu.png")
            if os.path.exists(man_path):
                original_pixmap = QPixmap(man_path)
                # 缩放Labubu图片到合适的大小，保持宽高比
                self.tree_pixmap = original_pixmap.scaled(200, 310, Qt.KeepAspectRatio, 
                                                          Qt.SmoothTransformation)
                self.original_pixmap = self.tree_pixmap.copy()  # 保存原始图片副本
            else:
                self.tree_pixmap = self.create_fallback_tree()
                self.original_pixmap = self.tree_pixmap.copy()  # 保存原始图片副本
            
            # 加载星星图片
            # "Star1.png"太暗淡了 "Star3.png",还行 直接放最亮的4个  "Star2.png",
            star_filenames = [ "Star6.png","Star4.png","Star5.png"]
            self.star_pixmaps = []
            for filename in star_filenames:
                star_path = os.path.join(res_dir, filename)
                if os.path.exists(star_path):
                    pixmap = QPixmap(star_path)
                    self.star_pixmaps.append(pixmap.scaled(19, 20, Qt.KeepAspectRatio,
                                                         Qt.SmoothTransformation))
                else:
                    # 创建备用星星
                    self.star_pixmaps.append(self.create_fallback_star())
                    
        except Exception as e:
            error_msg = f"资源加载错误: {e}\n将使用备用资源"
            print(error_msg)
            QMessageBox.warning(self, "资源加载警告", error_msg)
            self.create_fallback_resources()
            
    def create_fallback_tree(self):
        """创建备用圣诞老人图片"""
        pixmap = QPixmap(200, 310)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制圣诞老人轮廓（红色圆形身体）
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(50, 100, 100, 150)
        
        # 绘制圣诞老人头部（白色圆形）
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(75, 50, 50, 50)
        
        # 绘制圣诞老人帽子（红色三角形）
        painter.setBrush(QBrush(QColor(255, 0, 0)))
        points = QPolygon([
            QPoint(100, 20),
            QPoint(70, 50),
            QPoint(130, 50)
        ])
        painter.drawPolygon(points)
        
        painter.end()
        return pixmap
        
    def create_fallback_star(self):
        """创建备用星星图片"""
        pixmap = QPixmap(19, 20)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制五角星
        painter.setBrush(QBrush(QColor(255, 215, 0)))
        painter.setPen(Qt.NoPen)
        
        center_x, center_y = 9.5, 10
        outer_radius = 8
        inner_radius = 4
        
        points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append(QPoint(int(x), int(y)))
            
        painter.drawPolygon(points)
        painter.end()
        return pixmap
        
    def create_fallback_resources(self):
        """创建所有备用资源"""
        self.tree_pixmap = self.create_fallback_tree()
        self.original_pixmap = self.tree_pixmap.copy()  # 保存原始图片副本
        self.star_pixmaps = [self.create_fallback_star() for _ in range(6)]
        
    def init_star_positions(self):
        """初始化星星位置"""
        for i in range(6):
            ### v1版本
            # self.star_coords[i][0] = random.uniform(50, 250)  # x坐标
            # self.star_coords[i][1] = random.uniform(-50, 50)  # y坐标
            # self.star_speeds[i][0] = random.uniform(-0.2, 0.2)  # x速度
            # self.star_speeds[i][1] = random.uniform(1, 3)  # y速度
            self.star_coords[i][0] = random.uniform(80, 220)  # 缩小x范围，更靠近树
            self.star_coords[i][1] = random.uniform(15, 40)  # 调整y范围，更靠近树尖
            self.star_speeds[i][0] = random.uniform(-0.1, 0.1)  # 减小横向速度
            self.star_speeds[i][1] = random.uniform(0.3, 0.8)  # 减小纵向速度，飘落更慢
            
    def update_animation(self):
        """更新动画帧"""
        # 更新星星位置
        if self.stars_enabled:
            self.update_stars()
            
        # 更新Labubu上下移动
        self.man_y_offset += self.man_move_direction * self.man_move_speed
        
        # 边界检测和方向反转
        if self.man_y_offset >= self.man_max_y - self.man_min_y:
            self.man_move_direction = -1
        elif self.man_y_offset <= 0:
            self.man_move_direction = 1
        
        # 重绘窗口
        self.update()
        
    def update_stars(self):
        """更新星星位置"""
        for i in range(6):
            # 更新位置
            self.star_coords[i][0] += self.star_speeds[i][0]
            self.star_coords[i][1] += self.star_speeds[i][1]
            
            # 边界检测和重置
            if self.star_coords[i][1] > 400:
                # v1版本
                # self.star_coords[i][1] = random.uniform(-100, -50) # 重置到顶部上方很远的地方
                # self.star_coords[i][0] = random.uniform(50, 250) # 重置x坐标
                self.star_coords[i][1] = random.uniform(15, 40)  # 重置到靠近树尖的位置
                self.star_coords[i][0] = random.uniform(80, 220)  # 重置到靠近树的x范围
                
            if (self.star_coords[i][0] < 0 or self.star_coords[i][0] > 300):
                self.star_speeds[i][0] = -self.star_speeds[i][0]
                
    def update_particles(self, particles):
        """更新粒子位置"""
        self.current_particles = particles
        self.update()  # 触发重绘
        
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制Labubu
        if hasattr(self, 'tree_pixmap'):
            tree_x = (300 - self.tree_pixmap.width()) // 2
            tree_y = int(self.man_min_y + self.man_y_offset)
            
            if self.is_mirrored:
                # 保存当前变换矩阵
                painter.save()
                
                # 水平翻转绘制
                center_x = tree_x + self.tree_pixmap.width() // 2
                painter.translate(center_x, tree_y)
                painter.scale(-1, 1)
                painter.translate(-center_x, -tree_y)
                
                painter.drawPixmap(tree_x, tree_y, self.tree_pixmap)
                
                # 恢复变换矩阵
                painter.restore()
            else:
                # 正常绘制
                painter.drawPixmap(tree_x, tree_y, self.tree_pixmap)
            
        # 绘制星星
        if self.stars_enabled:
            self.draw_stars(painter)
            
        # 绘制粒子效果
        if self.stars_enabled and hasattr(self, 'current_particles'):
            self.draw_particles(painter)
            
    def draw_stars(self, painter):
        """绘制飘落的星星"""
        # 只绘制实际加载的星星数量，避免绘制备用黄色圆形
        for i in range(len(self.star_pixmaps)):
            x = int(self.star_coords[i][0])
            y = int(self.star_coords[i][1])
            
            if y > -20 and y < 400 and x > -20 and x < 320:
                painter.drawPixmap(x - 9, y - 10, self.star_pixmaps[i])
                    
    def draw_particles(self, painter):
        """绘制粒子效果"""
        for particle in self.current_particles:
            x = int(particle['x'])
            y = int(particle['y'])
            alpha = int(particle['alpha'])
            size = int(particle['size'])
            rotation = particle['rotation']
            
            # 设置透明度
            painter.setOpacity(alpha / 255.0)
            
            # 保存当前变换矩阵
            painter.save()
            
            # 平移到粒子位置
            painter.translate(x, y)
            
            # 旋转
            painter.rotate(rotation)
            
            # 使用加载的星星图片而不是十字架
            if hasattr(self, 'star_pixmaps') and self.star_pixmaps:
                # 随机选择一个星星图片
                star_index = random.randint(0, len(self.star_pixmaps) - 1)
                star_pixmap = self.star_pixmaps[star_index]
                
                # 根据粒子大小缩放图片
                scaled_pixmap = star_pixmap.scaled(size * 2, size * 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # 居中绘制
                painter.drawPixmap(-scaled_pixmap.width() // 2, -scaled_pixmap.height() // 2, scaled_pixmap)
            
            # 恢复变换矩阵
            painter.restore()
        
        # 恢复不透明度
        painter.setOpacity(1.0)
        
    def setup_context_menu(self):
        """设置右键菜单"""
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)
        
        menu.addSeparator()
        
        # 星星开关
        stars_action = QAction("星星特效", self)
        stars_action.setCheckable(True)
        stars_action.setChecked(self.stars_enabled)
        stars_action.triggered.connect(self.toggle_stars)
        menu.addAction(stars_action)
        
        # 左右镜像开关
        mirror_action = QAction("左右镜像", self)
        mirror_action.setCheckable(True)
        mirror_action.setChecked(self.is_mirrored)
        mirror_action.triggered.connect(self.toggle_mirror)
        menu.addAction(mirror_action)
        
        menu.addSeparator()
        
        # 透明度设置
        transparency_menu = menu.addMenu("透明度")
        for alpha, text in [(255, "0%"), (230, "10%"), (204, "20%"), 
                           (179, "30%"), (153, "40%"), (128, "50%"),
                           (102, "60%"), (77, "70%"), (51, "80%"), (26, "90%")]:
            action = QAction(text, self)
            action.setCheckable(True)
            if alpha == self.global_alpha:
                action.setChecked(True)
            action.triggered.connect(lambda checked, a=alpha: self.set_transparency(a))
            transparency_menu.addAction(action)
            
        menu.addSeparator()
        
        # 置顶开关
        top_action = QAction("置顶显示", self)
        top_action.setCheckable(True)
        # 动态检查当前置顶状态
        top_action.setChecked(self.windowFlags() & Qt.WindowStaysOnTopHint)
        top_action.triggered.connect(self.toggle_topmost)
        menu.addAction(top_action)
        
        menu.addSeparator()
        
        # 退出
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
        
        menu.exec(self.mapToGlobal(position))
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "Labubu桌面插件\n\n"
                         "作者：codeliu\n"
                         "版本：1.0\n"
                         "更多：https://github.com/liucf1224-del?tab=repositories\n")
                         
    def toggle_stars(self):
        """切换星星效果"""
        self.stars_enabled = not self.stars_enabled
        self.save_config()
        
        # 控制粒子系统的启停
        if hasattr(self, 'particle_system'):
            if self.stars_enabled:
                self.particle_system.start_particles(120)  # 启动粒子系统
            else:
                self.particle_system.stop_particles()  # 停止粒子系统
        
    def toggle_mirror(self):
        """切换左右镜像效果"""
        self.is_mirrored = not self.is_mirrored
        self.save_config()
        self.update()  # 触发重绘
    
    def set_transparency(self, alpha):
        """设置透明度"""
        self.global_alpha = alpha
        self.setWindowOpacity(alpha / 255.0)
        self.save_config()
        
    def toggle_topmost(self):
        """切换置顶显示"""
        flags = self.windowFlags()
        if flags & Qt.WindowStaysOnTopHint:
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
        self.show()
        self.save_config()
        
    def closeEvent(self, event):
        """关闭事件"""
        # 保存配置
        self.save_config()
        # 停止动画定时器
        if hasattr(self, 'animation_timer') and self.animation_timer.isActive():
            self.animation_timer.stop()
        # 停止粒子系统
        if hasattr(self, 'particle_system'):
            self.particle_system.stop_particles()
        event.accept()





def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("Labubu桌面插件")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("codeliu")
    
    # 设置应用程序图标
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "res", "Icon1.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # 直接创建Labubu窗口，不使用主窗口
    tree_widget = ChristmasTreeWidget()
    tree_widget.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
from PySide6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QSequentialAnimationGroup,
    QRect,
    QPoint,
)
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QEasingCurve
from typing import Union, Dict, List, Optional
from limekit.framework.core.engine.parts import EnginePart


class Animation(EnginePart):

    def __init__(self, widget: QWidget):
        self.widget = widget
        self.animation = QPropertyAnimation(self.widget, b"geometry")

    def animate(self):
        start_rect = self.widget.geometry()
        end_rect = QRect(
            start_rect.x() + 100,
            start_rect.y() + 100,
            start_rect.width(),
            start_rect.height(),
        )

        self.animation.setStartValue(start_rect)
        self.animation.setEndValue(end_rect)
        self.animation.setDuration(1200)
        self.animation.setEasingCurve(QEasingCurve.InElastic)
        self.animation.start()

    def emerge_from_bottom(self):
        """Creates a subtle emerging effect from slightly behind"""
        # Create parallel animation group
        group = QParallelAnimationGroup()

        # 1. Opacity animation (fade in)
        opacity_anim = QPropertyAnimation(self.widget, b"windowOpacity")
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setDuration(800)

        # 2. Position animation (subtle upward movement)
        pos_anim = QPropertyAnimation(self.widget, b"pos")
        original_pos = self.widget.pos()
        pos_anim.setStartValue(original_pos + QPoint(0, 20))  # Start slightly below
        pos_anim.setEndValue(original_pos)
        pos_anim.setEasingCurve(QEasingCurve.OutBack)
        pos_anim.setDuration(1000)

        # 3. Optional: Slight size change for depth effect
        size_anim = QPropertyAnimation(self.widget, b"size")
        original_size = self.widget.size()
        size_anim.setStartValue(original_size * 0.95)  # Start slightly smaller
        size_anim.setEndValue(original_size)
        size_anim.setDuration(1000)

        # Add animations to group
        group.addAnimation(opacity_anim)
        group.addAnimation(pos_anim)
        group.addAnimation(size_anim)

        # Start the animation
        group.start(QPropertyAnimation.DeleteWhenStopped)

        # Store reference to prevent garbage collection
        self.current_animation = group

    def animate(self):
        """Simpler version with just opacity and position"""
        group = QParallelAnimationGroup()

        # Fade in
        opacity_anim = QPropertyAnimation(self.widget, b"windowOpacity")
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setDuration(600)

        # Move up slightly
        pos_anim = QPropertyAnimation(self.widget, b"pos")
        original_pos = self.widget.pos()
        pos_anim.setStartValue(original_pos + QPoint(0, 10))
        pos_anim.setEndValue(original_pos)
        pos_anim.setDuration(800)
        pos_anim.setEasingCurve(QEasingCurve.OutQuad)

        group.addAnimation(opacity_anim)
        group.addAnimation(pos_anim)
        group.start()

        self.current_animation = group

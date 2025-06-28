#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试位置个性化功能
"""

def get_personalized_location_text(tool_id: str, location_text: str) -> str:
    """
    根据工具类型和位置文本返回个性化的位置描述
    
    Args:
        tool_id: 工具ID (glassCover, hand, catPaw, broom)
        location_text: 原始位置文本
    
    Returns:
        个性化的位置描述文本
    """
    # 如果位置不是"当前位置"，直接返回原文本
    if location_text != "当前位置":
        return location_text
    
    # 根据不同工具返回个性化文案
    tool_location_map = {
        "glassCover": "意念定位中…",          # 水晶球工具
        "hand": "摸鱼时区深处",               # 手工具
        "catPaw": "躲猫猫冠军认证点🐾",        # 猫爪工具
        "broom": "所有可能性的交汇处"          # 红笔工具
    }
    
    return tool_location_map.get(tool_id, location_text)

def test_location_personalization():
    """测试位置个性化功能"""
    print("=== 测试位置个性化功能 ===")
    
    # 测试用例
    test_cases = [
        # (工具ID, 原始位置, 期望结果)
        ("glassCover", "当前位置", "意念定位中…"),
        ("hand", "当前位置", "摸鱼时区深处"),
        ("catPaw", "当前位置", "躲猫猫冠军认证点🐾"),
        ("broom", "当前位置", "所有可能性的交汇处"),
        ("glassCover", "北京市朝阳区", "北京市朝阳区"),  # 非"当前位置"应该保持原样
        ("unknown_tool", "当前位置", "当前位置"),  # 未知工具应该返回原文本
    ]
    
    for tool_id, original_location, expected in test_cases:
        result = get_personalized_location_text(tool_id, original_location)
        status = "✅ 通过" if result == expected else "❌ 失败"
        print(f"{status} 工具: {tool_id}, 输入: '{original_location}' -> 输出: '{result}' (期望: '{expected}')")
    
    print("\n=== 个性化文案展示 ===")
    tools = ["glassCover", "hand", "catPaw", "broom"]
    tool_names = {
        "glassCover": "水晶球",
        "hand": "手",
        "catPaw": "猫爪",
        "broom": "红笔"
    }
    
    for tool_id in tools:
        personalized_text = get_personalized_location_text(tool_id, "当前位置")
        tool_name = tool_names.get(tool_id, tool_id)
        print(f"🔮 {tool_name}工具: {personalized_text}")

if __name__ == "__main__":
    test_location_personalization() 
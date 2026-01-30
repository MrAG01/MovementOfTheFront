import arcade.color
from arcade.gui import UIBoxLayout, UITextureButton, UILabel

from GUI.ui_texture import UITexture


def regenerate_cost_layout(resource_manager, cost_layout, cost, local_base_width=50,
                           local_base_height=40, texture_size=30, text_color=arcade.color.Color(255, 255, 255),
                           text_size=15):
    cost_layout.clear()
    if cost:
        for item_name, item in cost:
            local_layout = UIBoxLayout(vertical=False, width=local_base_width, height=local_base_height,
                                       space_between=2)
            raw_texture = resource_manager.get_texture(f"item_icon_{item_name}")
            item_texture = UITexture(texture=raw_texture.get(), width=texture_size,
                                           height=texture_size)
            local_layout.add(item_texture)
            local_layout.add(UILabel(str(item.amount), font_name="GNF", font_size=text_size, text_color=text_color))

            cost_layout.add(local_layout)
    elif cost is not None:
        cost_layout.add(
            UILabel(resource_manager.get_located_text("free_text", "text"), font_name="GNF", font_size=round(text_size * 0.8)))


def generate_cost_layout(resource_manager, cost, cost_layout_kwargs, local_base_width=50,
                         local_base_height=40, texture_size=30, text_color=arcade.color.Color(255, 255, 255),
                         text_size=15):
    cost_layout = UIBoxLayout(vertical=False, **cost_layout_kwargs)
    regenerate_cost_layout(resource_manager, cost_layout, cost, local_base_width, local_base_height, texture_size,
                           text_color, text_size)
    return cost_layout

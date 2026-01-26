import arcade.color
from arcade.gui import UIBoxLayout, UITextureButton, UILabel


def regenerate_cost_layout(resource_manager, cost_layout, cost, local_base_width=50,
                           local_base_height=40, texture_size=30, text_color=arcade.color.Color(255, 255, 255)):
    cost_layout.clear()
    if cost:
        for item_name, item in cost:
            local_layout = UIBoxLayout(vertical=False, width=local_base_width, height=local_base_height,
                                       space_between=2)
            raw_texture = resource_manager.get_texture(f"item_icon_{item_name}")
            item_texture = UITextureButton(texture=raw_texture.get(), width=texture_size,
                                           height=texture_size)
            local_layout.add(item_texture)
            local_layout.add(UILabel(str(item.amount), font_name="GNF", font_size=15, text_color=text_color))

            cost_layout.add(local_layout)
    elif cost is not None:
        cost_layout.add(
            UILabel(resource_manager.get_located_text("free_text", "text"), font_name="GNF", font_size=12))


def generate_cost_layout(resource_manager, cost, cost_layout_kwargs, local_base_width=50,
                         local_base_height=40, texture_size=30, text_color=arcade.color.Color(255, 255, 255)):
    cost_layout = UIBoxLayout(vertical=False, **cost_layout_kwargs)
    regenerate_cost_layout(resource_manager, cost_layout, cost, local_base_width, local_base_height, texture_size,
                           text_color)
    return cost_layout

import arcade
from arcade.gui import UIWidget, UIBoxLayout, UITextureButton, UIAnchorLayout, UILabel, Surface

from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData


class UIResourcePackWidget(UIWidget):
    def __init__(self, resource_pack_metadata, **kwargs):
        super().__init__(**kwargs)
        self.pack_metadata: ResourcePackMetaData = resource_pack_metadata
        self.preview_image_texture: arcade.Texture = self.pack_metadata.preview_image.get()
        self.base_horizontal_layout = UIBoxLayout(vertical=False, size_hint=(1.0, 1.0))

        self.image_container = UIAnchorLayout(
            size_hint=(0.2, 1.0),
            size_hint_min=(80, 80)
        )
        self.preview_image_widget = UITextureButton(
            texture=self.preview_image_texture,
            size_hint=(0.9, 0.9),
            size_hint_min=(80, 80)
        )

        self.image_container.add(self.preview_image_widget,
                                 anchor_x="center",
                                 anchor_y="center"
                                 )
        self.base_horizontal_layout.add(self.image_container)
        self.center_vertical_layout = UIBoxLayout(
            vertical=True,
            size_hint=(0.6, 1.0)
        )

        self.title_label = UILabel(
            text=self.pack_metadata.name,
            font_size=16,
            bold=True,
            text_color=arcade.color.WHITE,
            size_hint=(1.0, 0.3),
            multiline=False
        )

        self.description_label = UILabel(
            text=self.pack_metadata.description,
            font_size=12,
            text_color=arcade.color.LIGHT_GRAY,
            size_hint=(1.0, 0.7),
            multiline=True
        )
        self.center_vertical_layout.add(self.title_label)
        self.center_vertical_layout.add(self.description_label)

        self.base_horizontal_layout.add(self.center_vertical_layout)

        self.add(self.base_horizontal_layout)

    def do_render(self, surface: Surface):
        arcade.draw_rect_filled(self.content_rect, arcade.color.Color(255, 0, 0, 100))

        super().do_render(surface)

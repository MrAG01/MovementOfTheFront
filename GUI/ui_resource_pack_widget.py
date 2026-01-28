import arcade
from arcade.gui import UIWidget, UIBoxLayout, UITextureButton, UIAnchorLayout, UILabel, Surface

from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData


class UIResourcePackWidget(UIAnchorLayout):
    def __init__(self, resource_manager, resource_pack_metadata, ui, ui_hint=(0.08, 1), **kwargs):
        super().__init__(**kwargs)

        main_layout = UIBoxLayout(size_hint=(0.96, 0.95), vertical=False, space_between=10)

        self.pack_metadata: ResourcePackMetaData = resource_pack_metadata
        self.preview_image_texture: arcade.Texture = self.pack_metadata.preview_image.get()

        self.preview_image_widget = UITextureButton(
            texture=self.preview_image_texture,
            width=80,
            height=80
        )

        main_layout.add(self.preview_image_widget)
        self.center_vertical_layout = UIBoxLayout(
            vertical=True,
            size_hint=(0.72, 1.0)
        )
        font = resource_manager.get_default_font()
        self.title_label = UILabel(
            text=self.pack_metadata.name,
            font_size=16,
            font_name=font,
            bold=True,
            text_color=arcade.color.WHITE,
            size_hint=(1.0, 0.3),
            multiline=False
        )

        self.description_label = UILabel(
            text=self.pack_metadata.description,
            font_size=12,
            font_name=font,
            text_color=arcade.color.LIGHT_GRAY,
            size_hint=(1.0, 0.7),
            multiline=True
        )
        self.center_vertical_layout.add(self.title_label)
        self.center_vertical_layout.add(self.description_label)

        main_layout.add(self.center_vertical_layout)

        ui_anchor = UIAnchorLayout(size_hint=ui_hint)
        ui_anchor.add(ui)

        self.add(resource_manager.create_widget("secondary_background"))
        self.add(main_layout)
        self.add(ui_anchor, anchor_x="right", anchor_y="center")

    def do_render(self, surface: Surface):
        super().do_render(surface)

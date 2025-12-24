import arcade
from arcade.gui import UIWidget, UIBoxLayout, UITextureButton, UIAnchorLayout, UILabel, Surface

from resources.resource_packs.resource_pack_meta_data import ResourcePackMetaData


class UIResourcePackWidget(UIWidget):
    def __init__(self, resource_pack_metadata):
        super().__init__()
        self.pack_metadata: ResourcePackMetaData = resource_pack_metadata
        self.preview_image_texture: arcade.Texture = self.pack_metadata.preview_image.get()
        self.base_horizontal_layout = UIBoxLayout(vertical=False)

        self.image_container = UIAnchorLayout(
            width=100,
            height=100
        )
        self.preview_image_widget = UITextureButton(
            width=90,
            height=90,
            texture=self.preview_image_texture
        )

        self.image_container.add(self.preview_image_widget,
                                 anchor_x="center",
                                 anchor_y="center"
                                 )
        self.base_horizontal_layout.add(self.image_container)
        self.center_vertical_layout = UIBoxLayout(
            vertical=True,
            width=300,
            align="left"
        )

        self.title_label = UILabel(
            text=self.pack_metadata.name,
            font_size=16,
            bold=True,
            text_color=arcade.color.WHITE,
            width=300,
            multiline=False
        )

        self.description_label = UILabel(
            text=self.pack_metadata.description,
            font_size=12,
            text_color=arcade.color.LIGHT_GRAY,
            width=300,
            multiline=True,
            height=60
        )
        self.center_vertical_layout.add(self.title_label)
        self.center_vertical_layout.add(self.description_label)
        self.base_horizontal_layout.add(self.center_vertical_layout)

        self.add(self.base_horizontal_layout)
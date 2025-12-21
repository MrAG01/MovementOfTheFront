import arcade.gui
from arcade import Texture, SpriteList, Sprite
from arcade.gui import UIOnClickEvent


class UIResizableTextureButton(arcade.gui.UIFlatButton):
    def __init__(self, x, y, width, height, text,
                 normal_texture_handler,
                 hovered_texture_handler,
                 pressed_texture_handler, border_size):
        super().__init__(x=x,
                         y=y,
                         width=width,
                         height=height,
                         text=text)
        self.base_texture_handlers = {
            "normal": normal_texture_handler,
            "hovered": hovered_texture_handler,
            "pressed": pressed_texture_handler
        }
        self.border_size = border_size
        self.textures_cache: dict[str, SpriteList] = {}

    def on_click(self, event: UIOnClickEvent):
        print("HERE")

    def _create_slices(self, base_texture: Texture):
        sprite_list = arcade.SpriteList()

        btn_w, btn_h = self.width, self.height
        tex_w, tex_h = base_texture.width, base_texture.height
        border = self.border_size
        border2 = border * 2

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=0,
                    y=0,
                    width=border,
                    height=border
                )
            )
        )

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=border,
                    y=0,
                    width=tex_w - border2,
                    height=border
                )
            )
        )

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=tex_w - border,
                    y=0,
                    width=border,
                    height=border
                )
            )
        )

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=tex_w - border,
                    y=border,
                    width=border,
                    height=tex_h - border2
                )
            )
        )

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=tex_w - border,
                    y=tex_h - border,
                    width=border,
                    height=border
                )
            )
        )

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=border,
                    y=tex_h - border,
                    width=tex_w - border2,
                    height=border
                )
            )
        )

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=0,
                    y=tex_h - border,
                    width=border,
                    height=border
                )
            )
        )

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=0,
                    y=border,
                    width=border,
                    height=tex_h - border2
                )
            )
        )

        sprite_list.append(
            Sprite(
                texture=base_texture.crop(
                    x=border,
                    y=border,
                    width=tex_w - border2,
                    height=tex_h - border2
                )
            )
        )

        return sprite_list

    def trigger_full_render(self):
        super().trigger_full_render()

        current_size = self.width, self.height
        if hasattr(self, "_last_size"):
            if current_size != self._last_size:
                self._on_size_changed()
        self._last_size = current_size

    def _on_size_changed(self):
        self.textures_cache.clear()

    def _get_current_texture(self):
        state = self.get_current_state()
        if state in self.textures_cache:
            return self.textures_cache[state]
        else:
            if state in self.base_texture_handlers:
                base_texture = self.base_texture_handlers[state].get()
                self.textures_cache[state] = self._create_slices(base_texture)

    def move(self, dx=0, dy=0):
        super().move(dx, dy)

    def do_render(self, surface):
        texture: SpriteList = self._get_current_texture()
        texture.draw()
        super().do_render(surface)

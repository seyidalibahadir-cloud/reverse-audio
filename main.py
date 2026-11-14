"""Reverse Audio - initial Kivy interface.

This first version builds the Android app's interface and validates YouTube URLs.
Actual YouTube playback and reverse-audio processing are intentionally not
implemented yet; they require a playback/source approach compatible with
YouTube's terms and Android's media APIs.
"""

import re
from urllib.parse import urlparse, parse_qs

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex


BACKGROUND = get_color_from_hex("#10141E")
PANEL = get_color_from_hex("#1B2332")
ACCENT = get_color_from_hex("#7567F8")
TEXT = get_color_from_hex("#F4F6FC")
MUTED = get_color_from_hex("#AAB3C5")


def extract_youtube_video_id(raw_url: str):
    """Return a YouTube video ID for common YouTube URL formats, else None."""
    raw_url = raw_url.strip()
    if not raw_url:
        return None

    # Accept links pasted without a scheme, e.g. www.youtube.com/watch?v=...
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw_url):
        raw_url = "https://" + raw_url

    try:
        parsed = urlparse(raw_url)
    except ValueError:
        return None

    host = (parsed.hostname or "").lower()
    video_id = None

    if host in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif parsed.path.startswith(("/embed/", "/shorts/", "/live/")):
            parts = parsed.path.strip("/").split("/")
            if len(parts) > 1:
                video_id = parts[1]

    if video_id and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        return video_id
    return None


class ReverseAudioApp(App):
    title = "Reverse Audio"

    def build(self):
        root = BoxLayout(
            orientation="vertical",
            padding=[dp(22), dp(28), dp(22), dp(18)],
            spacing=dp(16),
        )
        root.canvas.before.clear()
        with root.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*BACKGROUND)
            self.background_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(
            pos=lambda widget, value: setattr(self.background_rect, "pos", value),
            size=lambda widget, value: setattr(self.background_rect, "size", value),
        )

        heading = Label(
            text="REVERSE AUDIO",
            color=TEXT,
            font_size="25sp",
            bold=True,
            size_hint_y=None,
            height=dp(48),
        )
        subtitle = Label(
            text="YouTube bağlantını buraya ekle",
            color=MUTED,
            font_size="14sp",
            size_hint_y=None,
            height=dp(28),
        )
        root.add_widget(heading)
        root.add_widget(subtitle)

        self.url_input = TextInput(
            hint_text="https://www.youtube.com/watch?v=...",
            multiline=False,
            size_hint_y=None,
            height=dp(54),
            padding=[dp(13), dp(16), dp(13), dp(12)],
            background_normal="",
            background_active="",
            background_color=PANEL,
            foreground_color=TEXT,
            hint_text_color=MUTED,
            cursor_color=ACCENT,
            font_size="14sp",
        )
        root.add_widget(self.url_input)

        self.status = Label(
            text="Bir YouTube video bağlantısı gir.",
            color=MUTED,
            font_size="13sp",
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(52),
        )
        self.status.bind(size=lambda widget, value: setattr(widget, "text_size", value))
        root.add_widget(self.status)

        normal_button = Button(
            text="Normal oynat",
            size_hint_y=None,
            height=dp(54),
            background_normal="",
            background_color=ACCENT,
            color=TEXT,
            font_size="16sp",
            bold=True,
        )
        normal_button.bind(on_release=self.on_normal_play)
        root.add_widget(normal_button)

        reverse_button = Button(
            text="Yalnızca sesi tersten oynat",
            size_hint_y=None,
            height=dp(54),
            background_normal="",
            background_color=PANEL,
            color=TEXT,
            font_size="15sp",
        )
        reverse_button.bind(on_release=self.on_reverse_play)
        root.add_widget(reverse_button)

        root.add_widget(Label(size_hint_y=1))
        footer = Label(
            text="REVERSE AUDIO  •  0.1.0",
            color=MUTED,
            font_size="11sp",
            size_hint_y=None,
            height=dp(24),
        )
        root.add_widget(footer)
        return root

    def _get_video_id(self):
        video_id = extract_youtube_video_id(self.url_input.text)
        if not video_id:
            self.status.text = "Geçerli bir YouTube video bağlantısı gir."
            self.status.color = get_color_from_hex("#FF8A8A")
            return None
        self.status.color = MUTED
        return video_id

    def on_normal_play(self, _button):
        video_id = self._get_video_id()
        if not video_id:
            return
        self.status.text = (
            "Bağlantı doğrulandı. Normal YouTube oynatıcısını ekleme "
            "aşaması henüz yapılmadı."
        )

    def on_reverse_play(self, _button):
        video_id = self._get_video_id()
        if not video_id:
            return
        self.status.text = (
            "Bağlantı doğrulandı. Ters ses özelliği henüz bağlanmadı; "
            "YouTube sesini doğrudan tersine çevirmek standart oynatıcıyla mümkün değil."
        )


if __name__ == "__main__":
    ReverseAudioApp().run()

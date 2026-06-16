from __future__ import annotations

import logging
import os
import platform
import struct
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

try:
    import flet as ft  # type: ignore
except Exception as exc:  # pragma: no cover - runtime dependency
    raise RuntimeError("Flet nao esta instalado. Adicione flet ao requirements e ao build.") from exc

try:
    import pystray  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    pystray = None

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.firebird import test_connection  # noqa: E402
from launcher.api_runner import test_health  # noqa: E402
from launcher.config_store import ConfigStore  # noqa: E402


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 760
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 680
COMPACT_SCREEN_WIDTH = 1366
COMPACT_SCREEN_HEIGHT = 768

BG = "#050b14"
SURFACE = "#0b1626"
SURFACE_2 = "#0f1d31"
PANEL = "#101c2e"
PANEL_ALT = "#13243a"
BORDER = "#23344c"
INPUT_BG = "#091321"
TEXT = "#ffffff"
MUTED = "#aab6c8"
ACCENT = "#0a84ff"
ACCENT_2 = "#4fd1ff"
ACCENT_STRONG = "#005bff"
SUCCESS = "#00a85a"
DANGER = "#ff2d3d"
NEUTRAL = "#1c2436"

LOG_DIR = BACKEND_ROOT / "logs"
LOG_FILE = LOG_DIR / "launcher.log"


def _build_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("bimobile.launcher.flet")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def format_port(value: str) -> int:
    try:
        return int(value.strip())
    except Exception:
        return 3050


def build_fdb_path(caminho_base: str, nome_arquivo: str) -> str:
    if not caminho_base or not nome_arquivo:
        return ""
    return str(Path(caminho_base) / nome_arquivo)


def _point_in_ellipse(x: int, y: int, cx: float, cy: float, rx: float, ry: float) -> bool:
    if rx <= 0 or ry <= 0:
        return False
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0


class _SimpleTrayIconImage:
    def __init__(self, size: int = 32) -> None:
        self.size = size
        self._ico_bytes = self._build_ico_bytes()

    def save(self, fp, format: str | None = None, **_kwargs) -> None:
        if format is not None and format.upper() != "ICO":
            raise ValueError("fallback tray icon only supports ICO")
        fp.write(self._ico_bytes)

    def _build_ico_bytes(self) -> bytes:
        size = self.size
        bg = (5, 11, 20, 255)
        body = (12, 31, 70, 255)
        fill = (30, 144, 255, 255)
        outline = (10, 132, 255, 255)

        rows: list[bytes] = []
        for y in range(size):
            row = bytearray()
            for x in range(size):
                pixel = self._pixel_color(x, y, size, bg, body, fill, outline)
                row.extend((pixel[2], pixel[1], pixel[0], pixel[3]))
            rows.append(bytes(row))

        pixel_bytes = b"".join(reversed(rows))
        mask_row_bytes = ((size + 31) // 32) * 4
        mask_bytes = b"\x00" * (mask_row_bytes * size)
        bitmap_header = struct.pack(
            "<IiiHHIIiiII",
            40,
            size,
            size * 2,
            1,
            32,
            0,
            len(pixel_bytes) + len(mask_bytes),
            2835,
            2835,
            0,
            0,
        )
        image_bytes = bitmap_header + pixel_bytes + mask_bytes
        icon_dir = struct.pack("<HHH", 0, 1, 1)
        icon_entry = struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(image_bytes), 6 + 16)
        return icon_dir + icon_entry + image_bytes

    def _pixel_color(
        self,
        x: int,
        y: int,
        size: int,
        bg: tuple[int, int, int, int],
        body: tuple[int, int, int, int],
        fill: tuple[int, int, int, int],
        outline: tuple[int, int, int, int],
    ) -> tuple[int, int, int, int]:
        center = size / 2
        body_left = int(size * 0.22)
        body_right = int(size * 0.78)
        body_top = int(size * 0.28)
        body_bottom = int(size * 0.80)

        if body_left <= x <= body_right and body_top <= y <= body_bottom:
            color = body
        else:
            color = bg

        ellipses = (
            (center, size * 0.24, size * 0.30, size * 0.10),
            (center, size * 0.50, size * 0.30, size * 0.10),
            (center, size * 0.76, size * 0.30, size * 0.10),
        )
        for cx, cy, rx, ry in ellipses:
            if _point_in_ellipse(x, y, cx, cy, rx, ry):
                return fill
            if _point_in_ellipse(x, y, cx, cy, rx * 1.05, ry * 1.15):
                color = outline
        return color


class BIMobileManagerApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.store = ConfigStore()
        self.logger = _build_logger()
        self._compact_layout = False
        self._font_scale = 1.0
        self._margin_scale = 1.0
        self._tray_icon = None
        self._tray_lock = threading.Lock()
        self._closing_requested = False
        self._shutdown_event = threading.Event()
        self._health_thread: threading.Thread | None = None
        self._tray_thread: threading.Thread | None = None
        self._api_health = "Verificando API..."
        self._api_health_detail = ""
        self.bases: list[dict[str, Any]] = []
        self.selected_base_id: str | None = None
        self.form_mode = "new"
        self.form_base_id: str | None = None
        self._pending_focus_base_id: str | None = None
        self._confirm_action: Callable[[], None] | None = None

        self._setup_page()
        self._initialize_layout_mode()
        self._build_shell()
        try:
            self.page.run_task(self._center_window_async)
        except Exception:
            pass
        self.refresh_bases()
        self.render_list_view()
        self._start_health_monitor()

    def _setup_page(self) -> None:
        self.page.title = "ResultBI - BIMobile API Manager"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = BG
        self.page.padding = 0
        self.page.window.width = WINDOW_WIDTH
        self.page.window.height = WINDOW_HEIGHT
        self.page.window_min_width = WINDOW_MIN_WIDTH
        self.page.window_min_height = WINDOW_MIN_HEIGHT
        self.page.window_resizable = False
        self.page.window_maximizable = False
        try:
            self.page.window.prevent_close = True
        except Exception:
            pass
        try:
            self.page.on_window_event = self._on_window_event
        except Exception:
            pass
        try:
            self.page.on_close = self._on_page_close
        except Exception:
            pass

    def _build_shell(self) -> None:
        self.left_panel = ft.Container(
            width=220,
            bgcolor=PANEL,
            border=ft.border.Border(
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
            ),
            border_radius=20,
            padding=16,
            content=self._build_left_panel_content(),
        )
        self.center_host = ft.Container(expand=True, padding=0)
        self.right_host = ft.Container(
            width=130,
            bgcolor=PANEL,
            border=ft.border.Border(
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
            ),
            border_radius=20,
            padding=12,
        )

        body = ft.Row(
            controls=[
                self.left_panel,
                ft.Container(expand=True, padding=ft.padding.Padding(left=12, right=12), content=self.center_host),
                self.right_host,
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        self.root = ft.Container(
            expand=True,
            padding=16,
            bgcolor=BG,
            content=ft.Column(
                controls=[
                    self._build_top_bar(),
                    ft.Container(height=12),
                    body,
                ],
                expand=True,
                spacing=0,
            ),
        )
        self.page.add(self.root)

    def _build_top_bar(self) -> ft.Control:
        self.top_health_text = ft.Text(self._api_health, size=12, weight=ft.FontWeight.W_600, color=TEXT)
        return ft.Container(
            bgcolor=SURFACE,
            border=ft.border.Border(
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
            ),
            border_radius=20,
            padding=ft.padding.Padding(left=18, top=14, right=18, bottom=14),
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("BIMobile API Manager", size=24, weight=ft.FontWeight.W_700, color=TEXT),
                            ft.Text("Interface moderna para cadastro e monitoramento da API", size=12, color=MUTED),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        bgcolor=SURFACE_2,
                        border_radius=16,
                        padding=ft.padding.Padding(left=12, top=8, right=12, bottom=8),
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.DNS_ROUNDED, size=18, color=ACCENT_2),
                                self.top_health_text,
                            ],
                            tight=True,
                            spacing=8,
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )

    def _build_left_panel_content(self) -> ft.Control:
        return ft.Column(
            controls=[
                ft.Container(
                    height=140,
                    border_radius=28,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment(-1, -1),
                        end=ft.alignment.Alignment(1, 1),
                        colors=["#11243e", "#0b1730", "#08101d"],
                    ),
                    padding=16,
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                width=72,
                                height=72,
                                border_radius=20,
                                bgcolor="#0f2344",
                                alignment=ft.alignment.Alignment(0, 0),
                                content=ft.Icon(ft.Icons.STORAGE_ROUNDED, size=42, color=ACCENT_2),
                            ),
                            ft.Text("ResultBI", size=20, weight=ft.FontWeight.W_700, color=TEXT),
                            ft.Text("BIMobile API", size=13, color=MUTED),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        spacing=6,
                    ),
                ),
                ft.Container(height=12),
                ft.Text("Atalhos", size=13, weight=ft.FontWeight.W_700, color=MUTED),
                ft.Container(height=8),
                self._sidebar_action("Nova", self.new_base, ft.Icons.ADD_ROUNDED, ACCENT),
                self._sidebar_action("Atualizar", self.refresh_and_render, ft.Icons.REFRESH_ROUNDED, SURFACE_2),
                self._sidebar_action("Teste Bandeja", self.minimize_to_tray, ft.Icons.NOTIFICATIONS_ACTIVE_ROUNDED, SURFACE_2),
                self._sidebar_action("Selecionar", self.select_base, ft.Icons.CHECK_CIRCLE_ROUNDED, NEUTRAL),
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )

    def _sidebar_action(self, label: str, handler: Callable[[ft.ControlEvent], None] | Callable[[], None], icon: Any, color: str) -> ft.Control:
        return ft.Container(
            margin=ft.margin.Margin(bottom=8),
            content=ft.Button(
                content=label,
                icon=icon,
                on_click=handler,
                width=188,
                height=42,
                style=ft.ButtonStyle(
                    bgcolor=color,
                    color=TEXT,
                    shape=ft.RoundedRectangleBorder(radius=12),
                    padding=ft.padding.Padding(left=12, top=10, right=12, bottom=10),
                ),
            ),
        )

    def _dispatch(self, callback: Callable[[], None]) -> None:
        caller = getattr(self.page, "call_from_thread", None)
        if callable(caller):
            try:
                caller(callback)
                return
            except Exception:
                pass
        callback()
        try:
            self.page.update()
        except Exception:
            pass

    def _notify(self, message: str, *, color: str = ACCENT) -> None:
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=TEXT),
            bgcolor=color,
        )
        self.page.snack_bar.open = True
        self.page.update()

    def _confirm(self, title: str, message: str, on_yes: Callable[[], None]) -> None:
        self._confirm_action = on_yes

        def accept(_event: ft.ControlEvent) -> None:
            self._close_dialog()
            action = self._confirm_action
            self._confirm_action = None
            if action is not None:
                action()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _e: self._close_dialog()),
                ft.FilledButton("Confirmar", on_click=accept),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _close_dialog(self) -> None:
        try:
            if self.page.dialog:
                self.page.dialog.open = False
        except Exception:
            pass
        self.page.update()

    def _current_form_base(self) -> dict[str, Any]:
        if self.form_mode == "edit" and self.form_base_id:
            base = next((item for item in self.bases if str(item.get("id")) == str(self.form_base_id)), None)
            if base is not None:
                return base
        if self.selected_base_id:
            selected = next((item for item in self.bases if str(item.get("id")) == str(self.selected_base_id)), None)
            if selected is not None:
                return selected
        return {}

    def _build_form_state(self, base: dict[str, Any]) -> dict[str, Any]:
        return {
            "apelido": str(base.get("apelido", "")),
            "caminho_base": str(base.get("caminho_base", "")),
            "nome_arquivo": str(base.get("nome_arquivo", "")),
            "servidor": str(base.get("servidor", "localhost")),
            "porta": str(base.get("porta", 3050)),
            "usuario_firebird": str(base.get("usuario_firebird", "SYSDBA")),
            "senha_firebird": str(base.get("senha_firebird", "masterkey")),
            "protocolo": str(base.get("protocolo", "TCP-IP")),
            "servidor_linux": bool(base.get("servidor_linux", False)),
            "ativo": bool(base.get("ativo", True)),
            "base_padrao": bool(base.get("base_padrao", False)),
        }

    def _reset_form_controls(self) -> None:
        base = self._current_form_base() if self.form_mode == "edit" else {}
        state = self._build_form_state(base)

        self.form_apelido = ft.TextField(
            label="Apelido",
            value=state["apelido"],
            border_radius=14,
            filled=True,
            fill_color=INPUT_BG,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            color=TEXT,
        )
        self.form_path = ft.TextField(
            label="Caminho da base de dados no servidor",
            value=state["caminho_base"],
            border_radius=14,
            filled=True,
            fill_color=INPUT_BG,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            color=TEXT,
        )
        self.form_filename = ft.TextField(
            label="Nome do Arquivo B.D.",
            value=state["nome_arquivo"],
            border_radius=14,
            filled=True,
            fill_color=INPUT_BG,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            color=TEXT,
        )
        self.form_server = ft.TextField(
            label="IP Servidor",
            value=state["servidor"],
            border_radius=14,
            filled=True,
            fill_color=INPUT_BG,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            color=TEXT,
        )
        self.form_port = ft.TextField(
            label="Porta",
            value=state["porta"],
            border_radius=14,
            filled=True,
            fill_color=INPUT_BG,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            color=TEXT,
        )
        self.form_user = ft.TextField(
            label="Usuário Firebird",
            value=state["usuario_firebird"],
            border_radius=14,
            filled=True,
            fill_color=INPUT_BG,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            color=TEXT,
        )
        self.form_password = ft.TextField(
            label="Senha Firebird",
            value=state["senha_firebird"],
            password=True,
            can_reveal_password=True,
            border_radius=14,
            filled=True,
            fill_color=INPUT_BG,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            color=TEXT,
        )
        self.form_protocol = ft.Dropdown(
            label="Protocolo",
            value=state["protocolo"],
            options=[ft.dropdown.Option("TCP-IP"), ft.dropdown.Option("Local")],
            border_radius=14,
            filled=True,
            fill_color=INPUT_BG,
            bgcolor=INPUT_BG,
            border_color=BORDER,
            color=TEXT,
        )
        self.form_linux = ft.Switch(label="Servidor Linux", value=state["servidor_linux"])
        self.form_active = ft.Switch(label="Ativa", value=state["ativo"])
        self.form_default = ft.Switch(label="Base padrão", value=state["base_padrao"])

    def _build_empty_state(self) -> ft.Control:
        return ft.Container(
            expand=True,
            alignment=ft.alignment.Alignment(0, 0),
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=72, color=ACCENT_2),
                    ft.Text("Nenhuma base cadastrada. Clique em Nova para configurar.", size=18, color=MUTED, text_align=ft.TextAlign.CENTER),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _build_table(self) -> ft.Control:
        rows: list[ft.DataRow] = []
        for base in self.bases:
            base_id = str(base.get("id") or "")
            rows.append(
                ft.DataRow(
                    selected=base_id == self.selected_base_id,
                    on_select_change=lambda _event, selected_id=base_id: self._select_base(selected_id),
                    cells=[
                        ft.DataCell(ft.Text(str(base.get("descricao") or base.get("apelido") or ""), color=TEXT)),
                        ft.DataCell(ft.Text(str(base.get("servidor") or ""), color=TEXT)),
                        ft.DataCell(ft.Text(str(base.get("porta") or ""), color=TEXT)),
                        ft.DataCell(ft.Text(str(base.get("nome_arquivo") or ""), color=TEXT)),
                        ft.DataCell(ft.Text("Sim" if base.get("base_padrao") else "Nao", color=TEXT)),
                        ft.DataCell(ft.Text("Sim" if base.get("ativo", True) else "Nao", color=TEXT)),
                    ],
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Descricao")),
                ft.DataColumn(ft.Text("Servidor")),
                ft.DataColumn(ft.Text("Porta")),
                ft.DataColumn(ft.Text("Arquivo")),
                ft.DataColumn(ft.Text("Padrao")),
                ft.DataColumn(ft.Text("Ativa")),
            ],
            rows=rows,
            expand=True,
            heading_row_color=SURFACE_2,
            data_row_min_height=54,
            data_row_max_height=58,
            border=ft.border.Border(
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
            ),
            border_radius=16,
            column_spacing=20,
        )
        return ft.Container(
            expand=True,
            border_radius=16,
            border=ft.border.Border(
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
            ),
            bgcolor=INPUT_BG,
            padding=8,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Row(
                controls=[table],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
        )

    def _build_list_panel(self) -> ft.Control:
        current_select_on_start = bool(self.store.load_bases_config().get("selecionar_base_ao_iniciar", False))
        self.switch_select_on_start = ft.Switch(
            label="Selecionar base ao iniciar",
            value=current_select_on_start,
            on_change=self._toggle_select_on_start,
        )
        self.list_actions = ft.Row(
            controls=[
                ft.FilledButton("Nova", icon=ft.Icons.ADD_ROUNDED, on_click=self.new_base),
                ft.FilledButton("Editar", icon=ft.Icons.EDIT_ROUNDED, on_click=self.edit_selected),
                ft.FilledButton("Excluir", icon=ft.Icons.DELETE_ROUNDED, on_click=self.delete_selected),
                ft.FilledButton("Atualizar", icon=ft.Icons.REFRESH_ROUNDED, on_click=self.refresh_and_render),
                ft.FilledButton("Selecionar", icon=ft.Icons.CHECK_CIRCLE_ROUNDED, on_click=self.select_base),
            ],
            wrap=True,
            spacing=8,
        )

        content = ft.Column(
            controls=[
                ft.Container(
                    padding=ft.padding.Padding(bottom=10),
                    content=ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Bases cadastradas", size=22, weight=ft.FontWeight.W_700, color=TEXT),
                                    ft.Text("A lista inicia vazia ate que uma base seja criada.", size=12, color=MUTED),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.Container(
                                bgcolor=SURFACE_2,
                                border_radius=14,
                                padding=ft.padding.Padding(left=10, top=8, right=10, bottom=8),
                                content=ft.Text(f"{len(self.bases)} base(s)", size=12, color=TEXT),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ),
                self.list_actions,
                ft.Container(height=10),
                ft.Container(expand=True, content=self._build_table() if self.bases else self._build_empty_state()),
                ft.Container(height=8),
                ft.Container(
                    content=self.switch_select_on_start,
                ),
            ],
            expand=True,
            spacing=10,
        )

        self.center_host.content = ft.Container(
            expand=True,
            bgcolor=SURFACE,
            border=ft.border.Border(
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
            ),
            border_radius=20,
            padding=16,
            content=content,
        )
        self._build_right_panel_list()
        self.page.update()
        return self.center_host.content

    def _build_form_panel(self) -> ft.Control:
        self._reset_form_controls()
        header = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Cadastro de base", size=22, weight=ft.FontWeight.W_700, color=TEXT),
                        ft.Text("Preencha os campos e teste a conexao antes de salvar.", size=12, color=MUTED),
                    ],
                    expand=True,
                    spacing=2,
                ),
                ft.TextButton("Voltar", icon=ft.Icons.ARROW_BACK_ROUNDED, on_click=self.render_list_view),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        conn_row = ft.ResponsiveRow(
            controls=[
                ft.Container(col={"sm": 12, "md": 6}, content=self.form_server),
                ft.Container(col={"sm": 12, "md": 6}, content=self.form_filename),
            ],
            spacing=12,
            run_spacing=12,
        )
        auth_row = ft.ResponsiveRow(
            controls=[
                ft.Container(col={"sm": 12, "md": 6}, content=self.form_user),
                ft.Container(col={"sm": 12, "md": 6}, content=self.form_password),
            ],
            spacing=12,
            run_spacing=12,
        )
        control_row = ft.ResponsiveRow(
            controls=[
                ft.Container(col={"sm": 12, "md": 4}, content=self.form_port),
                ft.Container(col={"sm": 12, "md": 4}, content=self.form_protocol),
                ft.Container(col={"sm": 12, "md": 4}, content=ft.Column([self.form_linux, self.form_active, self.form_default], spacing=6)),
            ],
            spacing=12,
            run_spacing=12,
        )

        actions = ft.Row(
            controls=[
                ft.FilledButton("Testar conexao", icon=ft.Icons.CHECK_CIRCLE_ROUNDED, on_click=self.test_form_connection),
                ft.FilledButton("Salvar", icon=ft.Icons.SAVE_ROUNDED, on_click=self.save_form),
                ft.FilledButton("Selecionar e voltar", icon=ft.Icons.ARROW_FORWARD_ROUNDED, on_click=self.select_and_return_from_form),
                ft.OutlinedButton("Cancelar", icon=ft.Icons.CLOSE_ROUNDED, on_click=self.render_list_view),
            ],
            wrap=True,
            spacing=10,
        )

        body = ft.Column(
            controls=[
                header,
                ft.Divider(height=1, color=BORDER),
                self.form_apelido,
                self.form_path,
                conn_row,
                auth_row,
                control_row,
                actions,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=12,
        )

        self.center_host.content = ft.Container(
            expand=True,
            bgcolor=SURFACE,
            border=ft.border.Border(
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
                ft.border.BorderSide(1, BORDER),
            ),
            border_radius=20,
            padding=16,
            content=body,
        )
        self._build_right_panel_form()
        self.page.update()
        return self.center_host.content

    def _build_right_panel_common(self) -> ft.Control:
        self.right_health_title = ft.Text(self._api_health, size=13, weight=ft.FontWeight.W_700, color=TEXT)
        self.right_health_detail = ft.Text(self._api_health_detail, size=10, color=MUTED, text_align=ft.TextAlign.CENTER)
        return ft.Column(
            controls=[
                ft.Container(
                    bgcolor=SURFACE_2,
                    border_radius=14,
                    padding=12,
                    content=ft.Column(
                        controls=[
                            ft.Text("API", size=11, color=MUTED),
                            self.right_health_title,
                            self.right_health_detail,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                ),
                ft.Container(height=8),
                ft.Text("Acoes", size=11, color=MUTED),
                ft.Container(height=8),
                ft.FilledButton("Abrir", icon=ft.Icons.OPEN_IN_NEW_ROUNDED, on_click=self.restore_from_tray),
                ft.FilledButton("Fechar", icon=ft.Icons.CLOSE_ROUNDED, on_click=self.quit_from_tray),
                ft.FilledButton("Teste Bandeja", icon=ft.Icons.NOTIFICATIONS_ACTIVE_ROUNDED, on_click=self.minimize_to_tray),
            ],
            spacing=8,
        )

    def _build_right_panel_list(self) -> None:
        self.right_host.content = self._build_right_panel_common()
        self.page.update()

    def _build_right_panel_form(self) -> None:
        self.right_host.content = self._build_right_panel_common()
        self.page.update()

    def refresh_bases(self) -> None:
        config = self.store.load_bases_config()
        self.bases = list(config.get("bases", []))
        self.selected_base_id = next((str(base.get("id")) for base in self.bases if base.get("base_padrao")), None)
        if self.selected_base_id is None and self.bases:
            self.selected_base_id = str(self.bases[0].get("id"))
        if hasattr(self, "switch_select_on_start"):
            self.switch_select_on_start.value = bool(config.get("selecionar_base_ao_iniciar", False))

    def refresh_and_render(self, _event: ft.ControlEvent | None = None) -> None:
        self.refresh_bases()
        self.render_list_view()

    def render_list_view(self, _event: ft.ControlEvent | None = None) -> None:
        self.form_mode = "new"
        self.form_base_id = None
        self.refresh_bases()
        self._build_list_panel()
        self.page.update()

    def render_form_view(self, mode: str = "new", base_id: str | None = None) -> None:
        self.form_mode = mode
        self.form_base_id = base_id
        self._build_form_panel()
        self.page.update()

    def _select_base(self, base_id: str) -> None:
        self.selected_base_id = base_id
        self.page.update()

    def get_selected_base(self) -> dict[str, Any] | None:
        if not self.selected_base_id:
            return None
        return next((base for base in self.bases if str(base.get("id")) == str(self.selected_base_id)), None)

    def _build_payload_from_form(self) -> dict[str, Any]:
        apelido = self.form_apelido.value.strip() if self.form_apelido.value else ""
        caminho_base = self.form_path.value.strip() if self.form_path.value else ""
        nome_arquivo = self.form_filename.value.strip() if self.form_filename.value else ""
        servidor = self.form_server.value.strip() if self.form_server.value else "localhost"
        usuario = self.form_user.value.strip() if self.form_user.value else "SYSDBA"
        senha = self.form_password.value or "masterkey"
        protocolo = self.form_protocol.value or "TCP-IP"
        porta = format_port(self.form_port.value or "3050")
        base_id = self.form_base_id if self.form_mode == "edit" else ""
        return {
            "id": base_id or "",
            "apelido": apelido,
            "descricao": apelido,
            "servidor": servidor,
            "porta": porta,
            "caminho_base": caminho_base,
            "nome_arquivo": nome_arquivo,
            "caminho_fdb": build_fdb_path(caminho_base, nome_arquivo),
            "usuario_firebird": usuario,
            "senha_firebird": senha,
            "protocolo": protocolo,
            "servidor_linux": bool(self.form_linux.value),
            "ativo": bool(self.form_active.value),
            "base_padrao": bool(self.form_default.value),
        }

    def _validate_form(self, payload: dict[str, Any]) -> bool:
        required = [
            ("Apelido", payload.get("apelido")),
            ("Caminho da base de dados no servidor", payload.get("caminho_base")),
            ("Nome do Arquivo B.D.", payload.get("nome_arquivo")),
        ]
        missing = [label for label, value in required if not str(value or "").strip()]
        if missing:
            self._notify(
                "Preencha os campos obrigatorios: " + ", ".join(missing),
                color=DANGER,
            )
            return False
        return True

    def _save_base(self, payload: dict[str, Any]) -> dict[str, Any]:
        saved = self.store.upsert_base(payload)
        self.refresh_bases()
        self._pending_focus_base_id = str(saved.get("id") or "")
        return saved

    def new_base(self, _event: ft.ControlEvent | None = None) -> None:
        self.render_form_view("new")

    def edit_selected(self, _event: ft.ControlEvent | None = None) -> None:
        base = self.get_selected_base()
        if base is None:
            self._notify("Selecione uma base primeiro.", color=DANGER)
            return
        self.render_form_view("edit", str(base.get("id") or ""))

    def delete_selected(self, _event: ft.ControlEvent | None = None) -> None:
        base = self.get_selected_base()
        if base is None:
            self._notify("Selecione uma base primeiro.", color=DANGER)
            return
        descricao = str(base.get("descricao") or base.get("apelido") or "")

        def confirm() -> None:
            self.store.delete_base(str(base.get("id") or ""))
            self.refresh_and_render()
            self._notify(f"Base {descricao} removida.", color=SUCCESS)

        self._confirm("Excluir base", f"Excluir a base {descricao}?", confirm)

    def select_base(self, _event: ft.ControlEvent | None = None) -> None:
        base = self.get_selected_base()
        if base is None:
            self._notify("Selecione uma base primeiro.", color=DANGER)
            return
        self.selected_base_id = str(base.get("id") or "")
        self._notify("Base selecionada.", color=SUCCESS)
        self.page.update()

    def _toggle_select_on_start(self, _event: ft.ControlEvent | None = None) -> None:
        if hasattr(self, "switch_select_on_start"):
            self.store.set_select_on_start(bool(self.switch_select_on_start.value))

    def save_form(self, _event: ft.ControlEvent | None = None) -> None:
        payload = self._build_payload_from_form()
        if not self._validate_form(payload):
            return
        saved = self._save_base(payload)
        self.selected_base_id = str(saved.get("id") or "")
        self._notify("Base salva com sucesso.", color=SUCCESS)
        self.render_list_view()

    def select_and_return_from_form(self, _event: ft.ControlEvent | None = None) -> None:
        payload = self._build_payload_from_form()
        if not self._validate_form(payload):
            return
        saved = self._save_base(payload)
        self.selected_base_id = str(saved.get("id") or "")
        self._notify("Base salva e selecionada.", color=SUCCESS)
        self.render_list_view()

    def test_form_connection(self, _event: ft.ControlEvent | None = None) -> None:
        payload = self._build_payload_from_form()
        if not self._validate_form(payload):
            return

        def worker() -> None:
            result = test_connection(payload)
            message = str(result.get("message", "Resultado indisponivel."))
            color = SUCCESS if result.get("ok") else DANGER
            self._dispatch(lambda: self._notify(message, color=color))

        threading.Thread(target=worker, daemon=True).start()

    def _create_tray_image(self) -> Any:
        return _SimpleTrayIconImage(size=32)

    def _ensure_tray_icon(self) -> bool:
        if pystray is None:
            self.logger.info("Tray indisponivel: pystray ausente")
            return False
        with self._tray_lock:
            if self._tray_icon is not None:
                return True
            try:
                image = self._create_tray_image()
                menu = pystray.Menu(
                    pystray.MenuItem("Abrir", lambda _icon, _item: self._dispatch(self.restore_from_tray)),
                    pystray.MenuItem("Fechar", lambda _icon, _item: self._dispatch(self.quit_from_tray)),
                )
                self._tray_icon = pystray.Icon("BIMobileAPIManager", image, "BIMobile API Manager", menu)
                self._tray_icon.run_detached()
                return True
            except Exception as exc:
                self.logger.info("Tray indisponivel: nao foi possivel criar o icone: %s", exc)
                self._tray_icon = None
                return False

    def _set_window_visible(self, visible: bool) -> None:
        for target, attr in ((self.page, "window_visible"), (getattr(self.page, "window", None), "visible")):
            if target is None:
                continue
            try:
                setattr(target, attr, visible)
                return
            except Exception:
                continue
        try:
            setattr(self.page, "window_minimized", not visible)
        except Exception:
            pass

    def minimize_to_tray(self, _event: ft.ControlEvent | None = None) -> None:
        if self._closing_requested:
            return
        if not self._ensure_tray_icon():
            return
        self.logger.info("minimize_to_tray")
        self._set_window_visible(False)
        self.page.update()

    def restore_from_tray(self, _event: ft.ControlEvent | None = None) -> None:
        if self._closing_requested:
            return
        self.logger.info("restore_from_tray")
        self._set_window_visible(True)
        try:
            self.page.window_center()
        except Exception:
            pass
        self.page.update()

    def _stop_tray_icon(self) -> None:
        with self._tray_lock:
            icon = self._tray_icon
            self._tray_icon = None
        if icon is not None:
            try:
                icon.stop()
            except Exception:
                pass

    def quit_from_tray(self, _event: ft.ControlEvent | None = None) -> None:
        if self._closing_requested:
            return
        self._closing_requested = True
        self.logger.info("quit_from_tray")
        self._shutdown_event.set()
        self._stop_tray_icon()
        self._destroy_page()
        self.logger.info("Aplicativo encerrado")

    def _destroy_page(self) -> None:
        for method_name in ("window_destroy", "window_close", "close"):
            method = getattr(self.page, method_name, None)
            if callable(method):
                try:
                    method()
                    return
                except Exception:
                    continue
        try:
            os._exit(0)
        except Exception:
            pass

    def _on_window_event(self, event: Any) -> None:
        data = getattr(event, "data", "")
        if data == "close":
            self.minimize_to_tray()

    def _on_page_close(self, _event: Any) -> None:
        self.minimize_to_tray()

    def _start_health_monitor(self) -> None:
        if self._health_thread and self._health_thread.is_alive():
            return

        def worker() -> None:
            while not self._shutdown_event.is_set():
                try:
                    result = test_health(timeout=1.0)
                    if result.get("ok"):
                        status = "API Online"
                        detail = "Pronta para uso"
                        color = SUCCESS
                    else:
                        status = "API Offline"
                        detail = str(result.get("message", "Sem resposta"))
                        color = DANGER
                except Exception as exc:
                    status = "API Offline"
                    detail = str(exc)
                    color = DANGER

                def apply_status() -> None:
                    self._api_health = status
                    self._api_health_detail = detail
                    if hasattr(self, "top_health_text"):
                        self.top_health_text.value = self._api_health
                    if hasattr(self, "right_health_title"):
                        self.right_health_title.value = self._api_health
                    if hasattr(self, "right_health_detail"):
                        self.right_health_detail.value = self._api_health_detail
                    self.page.update()

                self._dispatch(apply_status)
                time.sleep(5)

        self._health_thread = threading.Thread(target=worker, daemon=True)
        self._health_thread.start()

    async def _center_window_async(self) -> None:
        try:
            await self.page.window.center()
        except Exception:
            pass

    def _initialize_layout_mode(self) -> None:
        try:
            width = int(getattr(self.page.window, "width", WINDOW_WIDTH) or WINDOW_WIDTH)
            height = int(getattr(self.page.window, "height", WINDOW_HEIGHT) or WINDOW_HEIGHT)
        except Exception:
            width = WINDOW_WIDTH
            height = WINDOW_HEIGHT
        self._compact_layout = width < COMPACT_SCREEN_WIDTH or height < COMPACT_SCREEN_HEIGHT
        self._font_scale = 0.9 if self._compact_layout else 1.0
        self._margin_scale = 0.85 if self._compact_layout else 1.0


def main(page: ft.Page) -> None:
    BIMobileManagerApp(page)


def run() -> None:
    ft.run(main)


if __name__ == "__main__":
    run()

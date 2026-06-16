from __future__ import annotations

import logging
import platform
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import BooleanVar, StringVar, filedialog, messagebox, ttk

try:
    import pystray  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    pystray = None

try:
    from PIL import Image, ImageDraw  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    Image = None
    ImageDraw = None

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.firebird import test_connection  # noqa: E402
from launcher.api_runner import open_docs, start_api, stop_api  # noqa: E402
from launcher.config_store import ConfigStore  # noqa: E402


WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

BG = "#050b14"
CARD = "#0b1626"
PANEL = "#0d1b2e"
PANEL_ALT = "#101d31"
BORDER = "#22324a"
INPUT_BG = "#07111f"
INPUT_BORDER = "#2a3a52"
TEXT = "#ffffff"
MUTED = "#aab6c8"
ACCENT = "#0a84ff"
ACCENT_STRONG = "#005bff"
SUCCESS = "#00a85a"
SUCCESS_SOFT = "#0f8f4e"
DANGER = "#ff2d3d"
NEUTRAL = "#1c2436"
NEUTRAL_ALT = "#243149"
LINE = "#23344c"
LOG_DIR = BACKEND_ROOT / "logs"
LOG_FILE = LOG_DIR / "launcher.log"


def _build_logger() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("bimobile.launcher")
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


class LauncherApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.store = ConfigStore()
        self.logger = _build_logger()
        self.title("ResultBI - BIMobile API Manager")
        self.configure(bg=BG)
        self.resizable(False, False)
        if platform.system() == "Windows":
            self.overrideredirect(True)

        self.mode = "list"
        self.form_mode = "new"
        self.form_base_id: str | None = None
        self.bases: list[dict[str, object]] = []
        self.selected_base_id: str | None = None
        self._pending_focus_base_id: str | None = None
        self._drag_anchor: tuple[int, int, int, int] | None = None
        self._tray_icon = None
        self._tray_thread: threading.Thread | None = None
        self._tray_lock = threading.Lock()
        self._tray_running = threading.Event()
        self._api_started = False
        self._docs_opened = False
        self._closing_requested = False

        self.select_on_start_var = BooleanVar(value=False)
        self.api_status_var = StringVar(value="Inicializando...")

        self._configure_styles()
        self._build_window()
        self._center_window()
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.after(50, self._refresh_from_store)
        self.after(200, self._start_api_async)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "BIMobile.Treeview",
            background=INPUT_BG,
            fieldbackground=INPUT_BG,
            foreground=TEXT,
            rowheight=46,
            borderwidth=0,
            font=("Segoe UI", 13, "bold"),
        )
        style.configure(
            "BIMobile.Treeview.Heading",
            background=PANEL_ALT,
            foreground="#8fb4eb",
            font=("Segoe UI", 15, "bold"),
            padding=(12, 12),
        )
        style.map(
            "BIMobile.Treeview",
            background=[("selected", ACCENT_STRONG)],
            foreground=[("selected", TEXT)],
        )
        style.configure("BIMobile.Checkbutton", background=CARD, foreground=TEXT, font=("Segoe UI", 14))
        style.configure("BIMobile.Radiobutton", background=PANEL, foreground=TEXT, font=("Segoe UI", 13))

    def _center_window(self) -> None:
        self.update_idletasks()
        width = WINDOW_WIDTH
        height = WINDOW_HEIGHT
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_window(self) -> None:
        self.shell = tk.Frame(self, bg=BG)
        self.shell.pack(fill="both", expand=True)

        self.main_card = tk.Frame(self.shell, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        self.main_card.place(relx=0.018, rely=0.026, relwidth=0.964, relheight=0.948)

        self.header = tk.Frame(self.main_card, bg=CARD)
        self.header.pack(fill="x", padx=28, pady=(22, 12))
        self.header.bind("<ButtonPress-1>", self._start_drag)
        self.header.bind("<B1-Motion>", self._drag_window)

        title = tk.Label(
            self.header,
            text="Gerenciador de Base de Dados",
            bg=CARD,
            fg=TEXT,
            font=("Segoe UI", 26, "normal"),
        )
        title.pack(anchor="w")
        title.bind("<ButtonPress-1>", self._start_drag)
        title.bind("<B1-Motion>", self._drag_window)

        self.body = tk.Frame(self.main_card, bg=CARD)
        self.body.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.left_panel = tk.Frame(self.body, bg=PANEL, width=280)
        self.left_panel.pack(side="left", fill="y", padx=(0, 14))
        self.left_panel.pack_propagate(False)

        self.center_panel = tk.Frame(self.body, bg=CARD)
        self.center_panel.pack(side="left", fill="both", expand=True)

        self.right_panel = tk.Frame(self.body, bg=PANEL, width=280, highlightbackground=BORDER, highlightthickness=1)
        self.right_panel.pack(side="right", fill="y", padx=(14, 0))
        self.right_panel.pack_propagate(False)

        self.content_host = tk.Frame(self.center_panel, bg=CARD)
        self.content_host.place(relx=0.5, rely=0, anchor="n", relheight=1, width=930)

        self._build_left_sidebar()

    def _build_left_sidebar(self) -> None:
        top = tk.Frame(self.left_panel, bg=PANEL)
        top.pack(fill="both", expand=True, padx=16, pady=16)

        logo = tk.Canvas(top, width=220, height=250, bg=PANEL, highlightthickness=0)
        logo.pack(pady=(12, 6))
        self._draw_logo(logo)

        text_box = tk.Frame(top, bg=PANEL)
        text_box.pack(fill="x", pady=(6, 0))
        tk.Label(text_box, text="ResultBI", bg=PANEL, fg=TEXT, font=("Segoe UI", 23, "bold")).pack(anchor="w")
        tk.Label(text_box, text="BIMobile API", bg=PANEL, fg="#dfe9f8", font=("Segoe UI", 17, "normal")).pack(anchor="w", pady=(2, 0))

        line = tk.Frame(text_box, bg=LINE, height=2, width=180)
        line.pack(anchor="w", pady=(18, 10))
        tk.Frame(line, bg=ACCENT, height=2, width=46).pack(side="left")

        tk.Label(
            text_box,
            text="Conexão local segura com Firebird",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 11, "normal"),
        ).pack(anchor="w", pady=(4, 0))

        decor = tk.Canvas(self.left_panel, width=280, height=210, bg=PANEL, highlightthickness=0)
        decor.place(relx=0, rely=0.77)
        decor.create_oval(-58, 42, 128, 228, fill="#0a1220", outline="#0a1220")
        decor.create_oval(84, 86, 250, 252, fill="#0c1424", outline="#0c1424")
        decor.create_oval(208, 130, 372, 292, fill="#10192b", outline="#10192b")

    def _draw_logo(self, canvas: tk.Canvas) -> None:
        # Simple neon database mark drawn directly on the canvas.
        base_x = 56
        base_y = 20
        for offset in (0, 48, 96):
            y = base_y + offset
            canvas.create_oval(base_x, y, base_x + 132, y + 42, fill="#133d8e", outline="#1e90ff", width=2)
            canvas.create_rectangle(base_x, y + 21, base_x + 132, y + 62, fill="#0c1f46", outline="#0c1f46")
            canvas.create_oval(base_x, y + 40, base_x + 132, y + 76, fill="#0c1f46", outline="#0c1f46")
            canvas.create_arc(base_x, y + 46, base_x + 132, y + 82, start=180, extent=180, style="arc", outline="#1e90ff", width=2)

        canvas.create_text(138, 144, text="⚙", fill=ACCENT, font=("Segoe UI Symbol", 58, "bold"))

    def _clear_frame(self, frame: tk.Widget) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _rounded_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        *,
        bg: str,
        fg: str = TEXT,
        width: int | None = None,
        font: tuple[str, int, str] = ("Segoe UI", 16, "normal"),
        padx: int = 18,
        pady: int = 14,
        anchor: str = "center",
    ) -> tk.Button:
        kwargs: dict[str, object] = {
            "text": text,
            "command": command,
            "bg": bg,
            "fg": fg,
            "activebackground": bg,
            "activeforeground": fg,
            "bd": 0,
            "relief": "flat",
            "highlightthickness": 1,
            "highlightbackground": BORDER,
            "highlightcolor": BORDER,
            "font": font,
            "padx": padx,
            "pady": pady,
            "justify": "center",
            "anchor": anchor,
        }
        if width is not None:
            kwargs["width"] = width
        return tk.Button(parent, **kwargs)

    def _panel_card(self, parent: tk.Widget, bg: str = PANEL) -> tk.Frame:
        return tk.Frame(parent, bg=bg, highlightbackground=BORDER, highlightthickness=1)

    def _label_entry(
        self,
        parent: tk.Widget,
        label: str,
        variable: StringVar,
        *,
        show: str | None = None,
        width: int | None = None,
    ) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=parent["bg"])
        tk.Label(wrapper, text=label, bg=parent["bg"], fg=TEXT, font=("Segoe UI", 13, "normal")).pack(anchor="w", pady=(0, 6))
        entry = tk.Entry(
            wrapper,
            textvariable=variable,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=INPUT_BORDER,
            highlightcolor=ACCENT,
            font=("Segoe UI", 15, "normal"),
            show=show or "",
            width=width,
        )
        entry.pack(fill="x", ipady=8)
        return wrapper

    def _section_title(self, parent: tk.Widget, title: str) -> tk.Frame:
        row = tk.Frame(parent, bg=parent["bg"])
        tk.Label(row, text=title, bg=parent["bg"], fg=ACCENT, font=("Segoe UI", 18, "bold")).pack(side="left")
        line = tk.Frame(row, bg=LINE, height=2)
        line.pack(side="left", fill="x", expand=True, padx=(12, 0), pady=10)
        return row

    def _toggle_password(self) -> None:
        if self.password_entry.cget("show"):
            self.password_entry.configure(show="")
            self.password_visible = True
        else:
            self.password_entry.configure(show="•")
            self.password_visible = False

    def _browse_base_path(self) -> None:
        current = self.caminho_base_var.get().strip() or str(Path.home())
        selected = filedialog.askdirectory(parent=self, initialdir=current, title="Selecionar pasta da base")
        if selected:
            path = selected if selected.endswith(("\\", "/")) else f"{selected}\\"
            self.caminho_base_var.set(path)

    def _start_drag(self, event: tk.Event) -> None:
        self._drag_anchor = (event.x_root, event.y_root, self.winfo_x(), self.winfo_y())

    def _drag_window(self, event: tk.Event) -> None:
        if self._drag_anchor is None:
            return
        start_x, start_y, win_x, win_y = self._drag_anchor
        delta_x = event.x_root - start_x
        delta_y = event.y_root - start_y
        self.geometry(f"+{win_x + delta_x}+{win_y + delta_y}")

    def _create_tray_image(self):
        if Image is None:
            return None
        image = Image.new("RGBA", (64, 64), (5, 11, 20, 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse((10, 8, 54, 22), fill=(30, 144, 255, 255), outline=(10, 132, 255, 255))
        draw.rectangle((10, 15, 54, 32), fill=(12, 31, 70, 255))
        draw.ellipse((10, 24, 54, 38), fill=(12, 31, 70, 255))
        draw.arc((10, 24, 54, 38), start=180, end=360, fill=(10, 132, 255, 255), width=2)
        draw.ellipse((14, 34, 50, 50), fill=(14, 40, 95, 255), outline=(10, 132, 255, 255))
        draw.line((34, 27, 40, 39), fill=(10, 132, 255, 255), width=3)
        draw.line((38, 31, 29, 37), fill=(10, 132, 255, 255), width=3)
        return image

    def _start_tray_icon(self) -> None:
        if pystray is None or Image is None or ImageDraw is None:
            self.logger.info("Tray indisponivel: pystray/pillow ausente")
            return
        with self._tray_lock:
            if self._tray_icon is not None:
                return

            image = self._create_tray_image()
            if image is None:
                return

            menu = pystray.Menu(
                pystray.MenuItem("Abrir", lambda _icon, _item: self.after(0, self.restore_window)),
                pystray.MenuItem("Fechar", lambda _icon, _item: self.after(0, self.quit_app)),
            )
            self._tray_icon = pystray.Icon("BIMobileAPIManager", image, "BIMobile API Manager", menu)
            self._tray_running.set()

            def run_icon() -> None:
                try:
                    self._tray_icon.run()
                finally:
                    self._tray_running.clear()

            self._tray_thread = threading.Thread(target=run_icon, daemon=True)
            self._tray_thread.start()

    def minimize_to_tray(self) -> None:
        if self._closing_requested:
            return
        self._start_tray_icon()
        self.withdraw()
        self.logger.info("Janela enviada para bandeja")

    def restore_window(self) -> None:
        if self._closing_requested:
            return
        self.deiconify()
        self.state("normal")
        self.lift()
        self.focus_force()
        self.logger.info("Janela restaurada")

    def quit_app(self) -> None:
        if self._closing_requested:
            return
        self._closing_requested = True
        self.logger.info("Aplicativo encerrando")

        def worker() -> None:
            stop_api()
            self.after(0, self._shutdown_from_worker)

        threading.Thread(target=worker, daemon=True).start()

    def _shutdown_from_worker(self) -> None:
        self.logger.info("API encerrada")
        self._stop_tray_icon()
        self.logger.info("Aplicativo encerrado")
        self.destroy()

    def _stop_tray_icon(self) -> None:
        with self._tray_lock:
            icon = self._tray_icon
            self._tray_icon = None
        if icon is not None:
            try:
                icon.stop()
            except Exception:
                pass

    def _on_window_close(self) -> None:
        self.minimize_to_tray()

    def _refresh_from_store(self) -> None:
        self.refresh_bases()
        if self.mode == "list":
            self.show_list_view()

    def refresh_bases(self) -> None:
        config = self.store.load_bases_config()
        self.bases = list(config.get("bases", []))
        self.select_on_start_var.set(bool(config.get("selecionar_base_ao_iniciar", False)))

        selected = next((base for base in self.bases if base.get("base_padrao")), None)
        if selected is None and self.bases:
            selected = self.bases[0]
        self.selected_base_id = str(selected.get("id")) if selected else None

    def show_list_view(self) -> None:
        self.mode = "list"
        self.form_mode = "new"
        self.form_base_id = None
        self._clear_frame(self.content_host)
        self._clear_frame(self.right_panel)
        self._build_list_view()
        self._build_right_panel_list()
        self._load_tree_data()

    def show_form_view(self, mode: str = "new", base_id: str | None = None) -> None:
        self.mode = "form"
        self.form_mode = mode
        self.form_base_id = base_id
        self._clear_frame(self.content_host)
        self._clear_frame(self.right_panel)
        self._build_form_view()
        self._build_right_panel_form()

    def _build_list_view(self) -> None:
        wrapper = tk.Frame(self.content_host, bg=CARD)
        wrapper.pack(fill="both", expand=True, padx=(0, 10))

        panel = self._panel_card(wrapper, bg=PANEL)
        panel.pack(fill="both", expand=True, pady=(0, 14))

        tk.Label(panel, text="Descrição", bg=PANEL, fg="#93b5ec", font=("Segoe UI", 17, "bold")).pack(
            anchor="w", padx=20, pady=(14, 10)
        )

        table_frame = tk.Frame(panel, bg=INPUT_BG, highlightbackground=BORDER, highlightthickness=1)
        table_frame.pack(fill="both", expand=True, padx=14, pady=(0, 0))

        self.tree = ttk.Treeview(
            table_frame,
            columns=("descricao",),
            show="headings",
            selectmode="browse",
            style="BIMobile.Treeview",
        )
        self.tree.heading("descricao", text="Descrição")
        self.tree.column("descricao", width=760, anchor="w", stretch=True)
        self.tree.pack(fill="both", expand=True, padx=(0, 0), pady=(0, 0))
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", lambda _event: self.edit_selected())

        nav = tk.Frame(panel, bg=PANEL)
        nav.pack(fill="x", padx=14, pady=(0, 10))
        self._rounded_button(nav, "‹", self._noop_navigation, bg=PANEL, fg="#9fb1cf", font=("Segoe UI", 24, "bold"), padx=8, pady=0).pack(
            side="left"
        )
        self._rounded_button(nav, "›", self._noop_navigation, bg=PANEL, fg="#9fb1cf", font=("Segoe UI", 24, "bold"), padx=8, pady=0).pack(
            side="right"
        )

        actions = tk.Frame(wrapper, bg=CARD)
        actions.pack(fill="x", pady=(0, 16))
        self._rounded_button(actions, "＋  Nova", self.new_base, bg=ACCENT, font=("Segoe UI", 17, "normal"), padx=18, pady=14).pack(
            side="left", fill="x", expand=True, padx=(0, 14)
        )
        self._rounded_button(actions, "✎  Editar", self.edit_selected, bg=ACCENT_STRONG, font=("Segoe UI", 17, "normal"), padx=18, pady=14).pack(
            side="left", fill="x", expand=True, padx=(0, 14)
        )
        self._rounded_button(actions, "🗑  Excluir", self.delete_selected, bg=DANGER, font=("Segoe UI", 17, "normal"), padx=18, pady=14).pack(
            side="left", fill="x", expand=True
        )

        footer = tk.Frame(wrapper, bg=CARD)
        footer.pack(fill="x", pady=(0, 8))
        tk.Checkbutton(
            footer,
            text="Selecionar Base ao iniciar o sistema?",
            variable=self.select_on_start_var,
            command=self._toggle_select_on_start,
            bg=CARD,
            fg=TEXT,
            activebackground=CARD,
            activeforeground=TEXT,
            selectcolor=CARD,
            font=("Segoe UI", 13, "normal"),
            bd=0,
            highlightthickness=0,
        ).pack(anchor="w", pady=(4, 0))

    def _build_form_view(self) -> None:
        base = self._get_form_base()
        self.apelido_var = StringVar(value=str(base.get("apelido", "")))
        self.caminho_base_var = StringVar(value=str(base.get("caminho_base", "")))
        self.nome_arquivo_var = StringVar(value=str(base.get("nome_arquivo", "")))
        self.servidor_var = StringVar(value=str(base.get("servidor", "localhost")))
        self.usuario_var = StringVar(value=str(base.get("usuario_firebird", "SYSDBA")))
        self.senha_var = StringVar(value=str(base.get("senha_firebird", "masterkey")))
        self.porta_var = StringVar(value=str(base.get("porta", 3050)))
        self.protocolo_var = StringVar(value=str(base.get("protocolo", "TCP-IP")))
        self.servidor_linux_var = BooleanVar(value=bool(base.get("servidor_linux", False)))
        self.ativo_var = BooleanVar(value=bool(base.get("ativo", True)))
        self.base_padrao_var = BooleanVar(value=bool(base.get("base_padrao", False)))
        self.password_visible = False

        wrapper = tk.Frame(self.content_host, bg=CARD)
        wrapper.pack(fill="both", expand=True, padx=(0, 10))

        panel = self._panel_card(wrapper, bg=PANEL)
        panel.pack(fill="both", expand=True, pady=(0, 0))

        form = tk.Frame(panel, bg=PANEL)
        form.pack(fill="both", expand=True, padx=26, pady=22)

        self._label_title(form, "Apelido:").pack(fill="x")
        self.apelido_entry = self._entry(
            form,
            self.apelido_var,
            font=("Segoe UI", 15, "normal"),
        )
        self.apelido_entry.pack(fill="x", pady=(8, 16), ipady=6)

        self._section_title(form, "Conexão").pack(fill="x", pady=(0, 8))

        path_row = tk.Frame(form, bg=PANEL)
        path_row.pack(fill="x", pady=(2, 14))
        tk.Label(path_row, text="Caminho da base de dados no servidor:", bg=PANEL, fg=TEXT, font=("Segoe UI", 13, "normal")).pack(
            anchor="w", pady=(0, 6)
        )
        path_inner = tk.Frame(path_row, bg=PANEL)
        path_inner.pack(fill="x")
        self.caminho_entry = self._entry(path_inner, self.caminho_base_var, font=("Segoe UI", 14, "normal"))
        self.caminho_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self._rounded_button(path_inner, "📁", self._browse_base_path, bg=NEUTRAL_ALT, font=("Segoe UI Symbol", 16, "normal"), padx=14, pady=8).pack(
            side="left", padx=(12, 0)
        )

        row_2 = tk.Frame(form, bg=PANEL)
        row_2.pack(fill="x", pady=(0, 14))
        left = tk.Frame(row_2, bg=PANEL)
        left.pack(side="left", fill="x", expand=True, padx=(0, 16))
        self._label_entry(left, "IP Servidor (/Porta):", self.servidor_var).pack(fill="x")
        right = tk.Frame(row_2, bg=PANEL)
        right.pack(side="left", fill="x", expand=True)
        self._label_entry(right, "Nome do Arquivo B.D.:", self.nome_arquivo_var).pack(fill="x")

        row_3 = tk.Frame(form, bg=PANEL)
        row_3.pack(fill="x", pady=(0, 14))
        left = tk.Frame(row_3, bg=PANEL)
        left.pack(side="left", fill="x", expand=True, padx=(0, 16))
        self._label_entry(left, "Usuário Firebird:", self.usuario_var).pack(fill="x")
        right = tk.Frame(row_3, bg=PANEL)
        right.pack(side="left", fill="x", expand=True)
        password_box = tk.Frame(right, bg=PANEL)
        tk.Label(password_box, text="Senha Firebird:", bg=PANEL, fg=TEXT, font=("Segoe UI", 13, "normal")).pack(anchor="w", pady=(0, 6))
        pass_row = tk.Frame(password_box, bg=PANEL)
        pass_row.pack(fill="x")
        self.password_entry = self._entry(pass_row, self.senha_var, show="•", font=("Segoe UI", 14, "normal"))
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self._rounded_button(pass_row, "👁", self._toggle_password, bg=NEUTRAL_ALT, font=("Segoe UI Symbol", 15, "normal"), padx=12, pady=8).pack(
            side="left", padx=(12, 0)
        )
        password_box.pack(fill="x")

        row_4 = tk.Frame(form, bg=PANEL)
        row_4.pack(fill="x", pady=(4, 10))
        test_box = tk.Frame(row_4, bg=PANEL)
        test_box.pack(side="left", fill="x", expand=True, padx=(0, 16))
        self._rounded_button(
            test_box,
            "⛁  Testar Conexão",
            self.test_form_connection,
            bg=SUCCESS,
            fg="#e8fff0",
            font=("Segoe UI", 16, "normal"),
            padx=16,
            pady=14,
        ).pack(anchor="w")

        protocol_box = self._panel_card(row_4, bg=PANEL)
        protocol_box.pack(side="left", fill="x", expand=True)
        tk.Label(protocol_box, text="Protocolo Comunicação", bg=PANEL, fg=TEXT, font=("Segoe UI", 14, "normal")).pack(
            anchor="n", pady=(10, 6)
        )
        options = tk.Frame(protocol_box, bg=PANEL)
        options.pack(fill="x", padx=16, pady=(0, 14))
        tk.Radiobutton(
            options,
            text="NetBeui",
            value="NetBeui",
            variable=self.protocolo_var,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            selectcolor=PANEL,
            font=("Segoe UI", 12, "normal"),
            bd=0,
            highlightthickness=0,
        ).pack(side="left", padx=(0, 20))
        tk.Radiobutton(
            options,
            text="TCP-IP",
            value="TCP-IP",
            variable=self.protocolo_var,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            selectcolor=PANEL,
            font=("Segoe UI", 12, "normal"),
            bd=0,
            highlightthickness=0,
        ).pack(side="left")

        row_5 = tk.Frame(form, bg=PANEL)
        row_5.pack(fill="x", pady=(10, 0))
        flags = tk.Frame(row_5, bg=PANEL)
        flags.pack(side="left", fill="x", expand=True)
        tk.Checkbutton(
            flags,
            text="Servidor Linux",
            variable=self.servidor_linux_var,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            selectcolor=PANEL,
            font=("Segoe UI", 12, "normal"),
            bd=0,
            highlightthickness=0,
        ).pack(anchor="w", pady=(0, 8))
        tk.Checkbutton(
            flags,
            text="Ativo",
            variable=self.ativo_var,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            selectcolor=PANEL,
            font=("Segoe UI", 12, "normal"),
            bd=0,
            highlightthickness=0,
        ).pack(anchor="w")

        porta_box = tk.Frame(row_5, bg=PANEL, width=160)
        porta_box.pack(side="left", padx=(0, 24))
        porta_box.pack_propagate(False)
        tk.Label(porta_box, text="Porta:", bg=PANEL, fg=TEXT, font=("Segoe UI", 13, "normal")).pack(anchor="w", pady=(0, 6))
        self.porta_entry = self._entry(porta_box, self.porta_var, font=("Segoe UI", 14, "normal"))
        self.porta_entry.pack(fill="x", ipady=6)

        base_padrao_box = tk.Frame(row_5, bg=PANEL)
        base_padrao_box.pack(side="left", fill="x", expand=True)
        tk.Checkbutton(
            base_padrao_box,
            text="Base Padrão",
            variable=self.base_padrao_var,
            bg=PANEL,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            selectcolor=PANEL,
            font=("Segoe UI", 12, "normal"),
            bd=0,
            highlightthickness=0,
        ).pack(anchor="w", pady=(36, 0))

        bottom = tk.Frame(form, bg=PANEL)
        bottom.pack(fill="x", pady=(18, 0))
        self._rounded_button(bottom, "💾  Salvar", self.save_form, bg=ACCENT_STRONG, font=("Segoe UI", 17, "normal"), padx=18, pady=14).pack(
            side="left", padx=(0, 14)
        )
        self._rounded_button(bottom, "×  Cancelar", self.cancel_form, bg=NEUTRAL_ALT, font=("Segoe UI", 17, "normal"), padx=18, pady=14).pack(side="left")

    def _label_title(self, parent: tk.Widget, text: str) -> tk.Label:
        return tk.Label(parent, text=text, bg=parent["bg"], fg=TEXT, font=("Segoe UI", 17, "bold"))

    def _entry(self, parent: tk.Widget, variable: StringVar, *, show: str = "", font: tuple[str, int, str]) -> tk.Entry:
        return tk.Entry(
            parent,
            textvariable=variable,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=INPUT_BORDER,
            highlightcolor=ACCENT,
            font=font,
            show=show,
        )

    def _build_right_panel_list(self) -> None:
        box = tk.Frame(self.right_panel, bg=PANEL)
        box.pack(fill="both", expand=True, padx=14, pady=16)

        self._rounded_button(
            box,
            "✓  Selecionar",
            self.select_base,
            bg=SUCCESS,
            font=("Segoe UI", 16, "normal"),
            padx=18,
            pady=16,
        ).pack(fill="x", pady=(2, 20))

        filler = self._panel_card(box, bg=PANEL_ALT)
        filler.pack(fill="x", pady=(0, 20))
        filler.configure(height=86)
        filler.pack_propagate(False)

        self._rounded_button(
            box,
            "×  Fechar",
            self.minimize_to_tray,
            bg=NEUTRAL,
            font=("Segoe UI", 16, "normal"),
            padx=18,
            pady=16,
        ).pack(fill="x", pady=(0, 18))

        spacer = tk.Frame(box, bg=PANEL)
        spacer.pack(fill="both", expand=True)
        self._rounded_button(
            spacer,
            "⟳  Atualizar",
            self.refresh_and_reload_list,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 15, "normal"),
            padx=14,
            pady=10,
            anchor="w",
        ).pack(side="bottom", anchor="w", pady=(0, 18))

    def _build_right_panel_form(self) -> None:
        box = tk.Frame(self.right_panel, bg=PANEL)
        box.pack(fill="both", expand=True, padx=14, pady=16)

        self._rounded_button(
            box,
            "✓  Selecionar",
            self.select_base,
            bg=SUCCESS,
            font=("Segoe UI", 16, "normal"),
            padx=18,
            pady=16,
        ).pack(fill="x", pady=(2, 20))

        self._rounded_button(
            box,
            "×  Fechar",
            self.minimize_to_tray,
            bg=NEUTRAL,
            font=("Segoe UI", 16, "normal"),
            padx=18,
            pady=16,
        ).pack(fill="x", pady=(0, 18))

        filler = tk.Frame(box, bg=PANEL)
        filler.pack(fill="both", expand=True)

    def _load_tree_data(self) -> None:
        if not hasattr(self, "tree"):
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        for base in self.bases:
            descricao = str(base.get("descricao") or base.get("apelido") or "")
            self.tree.insert("", "end", iid=str(base.get("id")), values=(descricao,))

        focus_id = self._pending_focus_base_id or self.selected_base_id
        self._pending_focus_base_id = None
        if focus_id and self.tree.exists(str(focus_id)):
            self.tree.selection_set(str(focus_id))
            self.tree.focus(str(focus_id))
            self.tree.see(str(focus_id))
        elif self.bases:
            first_id = str(self.bases[0].get("id"))
            if self.tree.exists(first_id):
                self.tree.selection_set(first_id)
                self.tree.focus(first_id)
                self.tree.see(first_id)
                self.selected_base_id = first_id

    def _get_form_base(self) -> dict[str, object]:
        if self.form_mode == "new":
            return {
                "apelido": "",
                "caminho_base": "",
                "nome_arquivo": "",
                "servidor": "localhost",
                "porta": 3050,
                "usuario_firebird": "SYSDBA",
                "senha_firebird": "masterkey",
                "protocolo": "TCP-IP",
                "servidor_linux": False,
                "ativo": True,
                "base_padrao": False,
            }
        if self.form_mode == "edit" and self.form_base_id:
            base = next((item for item in self.bases if str(item.get("id")) == str(self.form_base_id)), None)
            if base is not None:
                return base
        if self.selected_base_id:
            selected = next((item for item in self.bases if str(item.get("id")) == str(self.selected_base_id)), None)
            if selected is not None:
                return selected
        return {}

    def _build_payload_from_form(self) -> dict[str, object]:
        apelido = self.apelido_var.get().strip()
        caminho_base = self.caminho_base_var.get().strip()
        nome_arquivo = self.nome_arquivo_var.get().strip()
        servidor = self.servidor_var.get().strip() or "localhost"
        usuario = self.usuario_var.get().strip() or "SYSDBA"
        senha = self.senha_var.get() or "masterkey"
        protocolo = self.protocolo_var.get().strip() or "TCP-IP"
        porta = format_port(self.porta_var.get())
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
            "servidor_linux": bool(self.servidor_linux_var.get()),
            "ativo": bool(self.ativo_var.get()),
            "base_padrao": bool(self.base_padrao_var.get()),
        }

    def _validate_form(self, payload: dict[str, object]) -> bool:
        required = [
            ("Apelido", payload.get("apelido")),
            ("Caminho da base de dados no servidor", payload.get("caminho_base")),
            ("Nome do Arquivo B.D.", payload.get("nome_arquivo")),
        ]
        missing = [label for label, value in required if not str(value or "").strip()]
        if missing:
            messagebox.showwarning(
                "Cadastro de Base",
                "Preencha os campos obrigatórios:\n- " + "\n- ".join(missing),
                parent=self,
            )
            return False
        return True

    def _on_tree_select(self, _event: object | None = None) -> None:
        selected = self.tree.selection()
        self.selected_base_id = selected[0] if selected else None

    def _toggle_select_on_start(self) -> None:
        self.store.set_select_on_start(bool(self.select_on_start_var.get()))

    def _save_base(self, payload: dict[str, object]) -> dict[str, object]:
        saved = self.store.upsert_base(payload)
        self.refresh_bases()
        self._pending_focus_base_id = str(saved.get("id") or "")
        return saved

    def _edit_selected_or_warn(self) -> dict[str, object] | None:
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Editar Base", "Selecione uma base primeiro.", parent=self)
            return None
        return base

    def _noop_navigation(self) -> None:
        return

    def _refresh_and_reload_list(self) -> None:
        self.refresh_bases()
        self.show_list_view()

    def refresh_and_reload_list(self) -> None:
        self._refresh_and_reload_list()

    def new_base(self) -> None:
        self.show_form_view("new")

    def edit_selected(self) -> None:
        base = self._edit_selected_or_warn()
        if base is None:
            return
        self.show_form_view("edit", str(base.get("id") or ""))

    def delete_selected(self) -> None:
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Excluir Base", "Selecione uma base primeiro.", parent=self)
            return
        descricao = str(base.get("descricao") or base.get("apelido") or "")
        if not messagebox.askyesno("Excluir Base", f"Excluir a base {descricao}?", parent=self):
            return
        self.store.delete_base(str(base.get("id") or ""))
        self.refresh_bases()
        self.show_list_view()

    def select_base(self) -> None:
        if self.mode == "form":
            self.select_and_return_from_form()
            return
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Selecionar Base", "Selecione uma base primeiro.", parent=self)
            return
        self.selected_base_id = str(base.get("id") or "")
        self.tree.selection_set(self.selected_base_id)
        self.tree.focus(self.selected_base_id)
        self.tree.see(self.selected_base_id)

    def select_and_return_from_form(self) -> None:
        payload = self._build_payload_from_form()
        if not self._validate_form(payload):
            return
        payload["base_padrao"] = bool(self.base_padrao_var.get())
        saved = self._save_base(payload)
        self.selected_base_id = str(saved.get("id") or "")
        self.show_list_view()

    def save_form(self) -> None:
        payload = self._build_payload_from_form()
        if not self._validate_form(payload):
            return
        saved = self._save_base(payload)
        self.selected_base_id = str(saved.get("id") or "")
        self.show_list_view()

    def cancel_form(self) -> None:
        self.show_list_view()

    def test_form_connection(self) -> None:
        payload = self._build_payload_from_form()
        if not self._validate_form(payload):
            return

        def worker() -> None:
            result = test_connection(payload)
            message = str(result.get("message", "Resultado indisponível."))
            if result.get("ok"):
                self.after(0, lambda: messagebox.showinfo("Teste de Conexão", message, parent=self))
            else:
                self.after(0, lambda: messagebox.showerror("Teste de Conexão", message, parent=self))

        threading.Thread(target=worker, daemon=True).start()

    def get_selected_base(self) -> dict[str, object] | None:
        selected_id = None
        if hasattr(self, "tree"):
            selected = self.tree.selection()
            if selected:
                selected_id = selected[0]
        if selected_id is None:
            selected_id = self.selected_base_id
        if not selected_id:
            return None
        return next((base for base in self.bases if str(base.get("id")) == str(selected_id)), None)

    def _start_api_async(self) -> None:
        def worker() -> None:
            result = start_api()
            if result.get("ok"):
                self.logger.info("API iniciada")
                self.after(0, self._open_docs_once)
                self.after(0, lambda: self.api_status_var.set("API pronta e Docs abertos"))
            else:
                self.after(0, lambda: self.api_status_var.set("Falha ao iniciar API"))

        threading.Thread(target=worker, daemon=True).start()

    def _open_docs_once(self) -> None:
        if self._docs_opened:
            return
        self._docs_opened = True
        self.logger.info("Docs aberto")
        open_docs()


def run_api_mode() -> None:
    import uvicorn
    from app.main import app as fastapi_app

    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, reload=False)


def main() -> None:
    if "--api" in sys.argv:
        run_api_mode()
        return
    app = LauncherApp()
    app.mainloop()


if __name__ == "__main__":
    main()

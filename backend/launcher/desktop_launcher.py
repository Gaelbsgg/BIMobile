from __future__ import annotations

import sys
import threading
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import BooleanVar, StringVar, Tk, Toplevel, filedialog, messagebox, ttk

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.firebird import test_connection  # noqa: E402
from launcher.api_runner import is_api_running, open_docs, start_api, stop_api, test_health  # noqa: E402
from launcher.config_store import ConfigStore  # noqa: E402


BG = "#030712"
PANEL = "#09111e"
PANEL_ALT = "#0c1525"
CARD = "#0b1322"
TEXT = "#e5eefb"
MUTED = "#8f9bb0"
ACCENT = "#0ea5e9"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER = "#ef4444"
NEUTRAL = "#334155"


def format_port(value: str) -> int:
    try:
        return int(value.strip())
    except Exception:
        return 3050


def build_fdb_path(caminho_base: str, nome_arquivo: str) -> str:
    if not caminho_base or not nome_arquivo:
        return ""
    return str(Path(caminho_base) / nome_arquivo)


@dataclass
class FormResult:
    data: dict[str, object]


class BaseFormDialog(Toplevel):
    def __init__(self, master: Tk, store: ConfigStore, base: dict[str, object] | None = None, on_save=None):
        super().__init__(master)
        self.store = store
        self.base = base or {}
        self.on_save = on_save
        self.result: FormResult | None = None

        self.title("Cadastro de Base")
        self.configure(bg=BG)
        self.geometry("820x620")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.apelido_var = StringVar(value=str(self.base.get("apelido", "")))
        self.caminho_base_var = StringVar(value=str(self.base.get("caminho_base", "")))
        self.nome_arquivo_var = StringVar(value=str(self.base.get("nome_arquivo", "")))
        self.servidor_var = StringVar(value=str(self.base.get("servidor", "localhost")))
        self.login_var = StringVar(value=str(self.base.get("usuario_firebird", "SYSDBA")))
        self.senha_var = StringVar(value=str(self.base.get("senha_firebird", "masterkey")))
        self.porta_var = StringVar(value=str(self.base.get("porta", 3050)))
        self.protocolo_var = StringVar(value=str(self.base.get("protocolo", "TCP-IP")))
        self.linux_var = BooleanVar(value=bool(self.base.get("servidor_linux", False)))
        self.ativo_var = BooleanVar(value=bool(self.base.get("ativo", True)))
        self.base_padrao_var = BooleanVar(value=bool(self.base.get("base_padrao", False)))
        self.show_password_var = BooleanVar(value=False)

        self._configure_styles()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(50, self.apelido_entry.focus_set)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("TButton", padding=(14, 8), font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, insertcolor=TEXT)
        style.configure("TRadiobutton", background=BG, foreground=TEXT, font=("Segoe UI", 9))
        style.configure("TCheckbutton", background=BG, foreground=TEXT, font=("Segoe UI", 9))

    def _entry(self, parent: tk.Widget, attr_name: str, variable: StringVar) -> ttk.Entry:
        entry = ttk.Entry(parent, textvariable=variable)
        setattr(self, attr_name, entry)
        return entry

    def _field(self, parent: tk.Widget, label: str, widget_factory) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=BG)
        tk.Label(wrapper, text=label, bg=BG, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        widget = widget_factory(wrapper)
        widget.pack(fill="x")
        return wrapper

    def _password_widget(self, parent: tk.Widget) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=BG)
        tk.Label(wrapper, text="Senha Firebird", bg=BG, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        row = tk.Frame(wrapper, bg=BG)
        row.pack(fill="x")
        self.senha_entry = ttk.Entry(row, textvariable=self.senha_var, show="•")
        self.senha_entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            row,
            text="👁",
            command=self._toggle_password,
            bg=PANEL_ALT,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            bd=0,
            relief="flat",
            width=4,
        ).pack(side="left", padx=(8, 0))
        return wrapper

    def _path_widget(self, parent: tk.Widget) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=BG)
        tk.Label(wrapper, text="Caminho da base de dados no servidor", bg=BG, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        row = tk.Frame(wrapper, bg=BG)
        row.pack(fill="x")
        entry = ttk.Entry(row, textvariable=self.caminho_base_var)
        entry.pack(side="left", fill="x", expand=True)
        tk.Button(
            row,
            text="...",
            command=self._browse_base_path,
            bg=PANEL_ALT,
            fg=TEXT,
            activebackground=PANEL,
            activeforeground=TEXT,
            bd=0,
            relief="flat",
            width=4,
        ).pack(side="left", padx=(8, 0))
        self.caminho_entry = entry
        return wrapper

    def _protocol_widget(self, parent: tk.Widget) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=BG)
        tk.Label(wrapper, text="Protocolo de comunicação", bg=BG, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        row = tk.Frame(wrapper, bg=BG)
        row.pack(fill="x")
        ttk.Radiobutton(row, text="TCP-IP", value="TCP-IP", variable=self.protocolo_var).pack(side="left", padx=(0, 18))
        ttk.Radiobutton(row, text="NetBeui", value="NetBeui", variable=self.protocolo_var).pack(side="left")
        return wrapper

    def _browse_base_path(self) -> None:
        current = self.caminho_base_var.get().strip() or str(Path.home())
        selected = filedialog.askdirectory(parent=self, initialdir=current, title="Selecionar pasta da base")
        if selected:
            path = selected if selected.endswith(("\\", "/")) else f"{selected}\\"
            self.caminho_base_var.set(path)

    def _toggle_password(self) -> None:
        self.show_password_var.set(not self.show_password_var.get())
        self.senha_entry.configure(show="" if self.show_password_var.get() else "•")

    def _build_ui(self) -> None:
        container = tk.Frame(self, bg=BG)
        container.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(container, text="Gerenciador de Base de Dados - BIMobile API", bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(
            anchor="w", pady=(6, 4)
        )
        tk.Label(container, text="Conexão Firebird com visual corporativo", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 14))

        card = tk.Frame(container, bg=PANEL, highlightbackground="#1f2a3c", highlightthickness=1)
        card.pack(fill="both", expand=True)

        form = tk.Frame(card, bg=PANEL)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        self._field(form, "Apelido", lambda parent: self._entry(parent, "apelido_entry", self.apelido_var)).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=8
        )
        self._path_widget(form).grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)

        left_1 = tk.Frame(form, bg=PANEL)
        right_1 = tk.Frame(form, bg=PANEL)
        self._field(left_1, "Nome do banco de dados", lambda parent: ttk.Entry(parent, textvariable=self.nome_arquivo_var)).pack(fill="x")
        self._field(right_1, "Nome do servidor", lambda parent: ttk.Entry(parent, textvariable=self.servidor_var)).pack(fill="x")
        left_1.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=8)
        right_1.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=8)

        left_2 = tk.Frame(form, bg=PANEL)
        right_2 = tk.Frame(form, bg=PANEL)
        self._field(left_2, "Login Firebird", lambda parent: ttk.Entry(parent, textvariable=self.login_var)).pack(fill="x")
        self._password_widget(right_2).pack(fill="x")
        left_2.grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=8)
        right_2.grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=8)

        left_3 = tk.Frame(form, bg=PANEL)
        right_3 = tk.Frame(form, bg=PANEL)
        self._field(left_3, "Porta", lambda parent: ttk.Entry(parent, textvariable=self.porta_var)).pack(fill="x")
        self._protocol_widget(right_3).pack(fill="x")
        left_3.grid(row=4, column=0, sticky="ew", padx=(0, 8), pady=8)
        right_3.grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=8)

        options = tk.Frame(form, bg=PANEL)
        options.grid(row=5, column=0, columnspan=2, sticky="w", pady=(18, 0))
        ttk.Checkbutton(options, text="Servidor Linux", variable=self.linux_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(options, text="Ativo", variable=self.ativo_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(options, text="Base Padrão", variable=self.base_padrao_var).pack(side="left")

        buttons = tk.Frame(card, bg=PANEL)
        buttons.pack(fill="x", padx=20, pady=(0, 20))
        tk.Button(
            buttons,
            text="Testar Conexão",
            command=self._test_connection,
            bg=SUCCESS,
            fg="#06210f",
            activebackground=SUCCESS,
            activeforeground="#06210f",
            bd=0,
            relief="flat",
            padx=16,
            pady=8,
        ).pack(side="left")
        tk.Button(
            buttons,
            text="Salvar",
            command=self._save,
            bg=ACCENT,
            fg="#ffffff",
            activebackground=ACCENT,
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            padx=18,
            pady=8,
        ).pack(side="right", padx=(10, 0))
        tk.Button(
            buttons,
            text="Cancelar",
            command=self._close,
            bg=NEUTRAL,
            fg="#ffffff",
            activebackground=NEUTRAL,
            activeforeground="#ffffff",
            bd=0,
            relief="flat",
            padx=18,
            pady=8,
        ).pack(side="right")

    def _build_payload(self) -> dict[str, object]:
        apelido = self.apelido_var.get().strip()
        caminho_base = self.caminho_base_var.get().strip()
        nome_arquivo = self.nome_arquivo_var.get().strip()
        return {
            "id": self.base.get("id") or "",
            "apelido": apelido,
            "descricao": apelido,
            "servidor": self.servidor_var.get().strip() or "localhost",
            "porta": format_port(self.porta_var.get()),
            "caminho_base": caminho_base,
            "nome_arquivo": nome_arquivo,
            "caminho_fdb": build_fdb_path(caminho_base, nome_arquivo),
            "usuario_firebird": self.login_var.get().strip() or "SYSDBA",
            "senha_firebird": self.senha_var.get() or "masterkey",
            "protocolo": self.protocolo_var.get().strip() or "TCP-IP",
            "servidor_linux": bool(self.linux_var.get()),
            "ativo": bool(self.ativo_var.get()),
            "base_padrao": bool(self.base_padrao_var.get()),
            "token_empresa": self.base.get("token_empresa", ""),
        }

    def _test_connection(self) -> None:
        payload = self._build_payload()
        result = test_connection(payload)
        message = str(result.get("message", "Resultado indisponível."))
        if result.get("ok"):
            messagebox.showinfo("Teste de Conexão", message, parent=self)
        else:
            messagebox.showerror("Teste de Conexão", message, parent=self)

    def _save(self) -> None:
        payload = self._build_payload()
        if not payload["apelido"] or not payload["caminho_base"] or not payload["nome_arquivo"]:
            messagebox.showwarning("Cadastro de Base", "Preencha Apelido, Caminho e Nome do banco de dados.", parent=self)
            return
        self.result = FormResult(data=payload)
        if callable(self.on_save):
            self.on_save(payload)
        self.destroy()

    def _close(self) -> None:
        self.destroy()


class LauncherApp(Tk):
    def __init__(self):
        super().__init__()
        self.store = ConfigStore()
        self.title("ResultBI - BIMobile API Manager")
        self.geometry("1280x760")
        self.minsize(1180, 700)
        self.configure(bg=BG)

        self.bases: list[dict[str, object]] = []
        self.selected_base_id: str | None = None
        self.select_on_start_var = BooleanVar(value=False)
        self.api_status_var = StringVar(value="Parada")
        self.bank_status_var = StringVar(value="Banco em modo mock")
        self.selected_base_name_var = StringVar(value="Nenhuma base selecionada")
        self.default_base_var = StringVar(value="Nenhuma base padrão")
        self.api_url_var = StringVar(value="http://localhost:8000")
        self.api_port_var = StringVar(value="8000")

        self._configure_styles()
        self._build_ui()
        self._center_window()
        self.refresh_bases()
        self.after(300, self._ensure_api_started)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("TButton", padding=(14, 8), font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, insertcolor=TEXT)
        style.configure("TCombobox", fieldbackground=PANEL, foreground=TEXT, background=PANEL)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", TEXT)])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=34, borderwidth=0)
        style.configure("Treeview.Heading", background=PANEL_ALT, foreground=TEXT, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#12324a")], foreground=[("selected", "#ffffff")])
        style.configure("TCheckbutton", background=BG, foreground=TEXT, font=("Segoe UI", 9))

    def _center_window(self) -> None:
        self.update_idletasks()
        width = 1280
        height = 760
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = max((screen_width - width) // 2, 0)
        y = max((screen_height - height) // 2, 0)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self) -> None:
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)
        self._build_left_sidebar(root)
        self._build_center_area(root)
        self._build_right_panel(root)

    def _build_left_sidebar(self, parent: tk.Widget) -> None:
        sidebar = tk.Frame(parent, bg=PANEL, width=250)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        top = tk.Frame(sidebar, bg=PANEL)
        top.pack(fill="x", padx=24, pady=(28, 18))

        canvas = tk.Canvas(top, width=88, height=88, bg=PANEL, highlightthickness=0)
        canvas.pack()
        canvas.create_oval(12, 12, 76, 76, outline=ACCENT, width=4)
        canvas.create_text(44, 44, text="DB", fill=TEXT, font=("Segoe UI", 18, "bold"))

        tk.Label(top, text="ResultBI", bg=PANEL, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(pady=(14, 2))
        tk.Label(top, text="BIMobile API", bg=PANEL, fg=TEXT, font=("Segoe UI", 15, "bold")).pack()
        tk.Label(top, text="Conexão local segura com Firebird", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(pady=(6, 0))

        status_box = tk.Frame(sidebar, bg=CARD, highlightbackground="#1f2a3c", highlightthickness=1)
        status_box.pack(fill="x", padx=20, pady=(8, 16))
        self._status_line(status_box, "API", self.api_status_var, ACCENT)
        self._status_line(status_box, "Banco", self.bank_status_var, SUCCESS)
        self._status_line(status_box, "Base selecionada", self.selected_base_name_var, TEXT)
        self._status_line(status_box, "Base padrão", self.default_base_var, WARNING)

        bottom = tk.Frame(sidebar, bg=PANEL)
        bottom.pack(side="bottom", fill="x", padx=20, pady=18)
        tk.Label(bottom, text="v0.1.0", bg=PANEL, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.clock_label = tk.Label(bottom, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 9))
        self.clock_label.pack(anchor="w", pady=(6, 0))
        self._tick_clock()

    def _status_line(self, parent: tk.Widget, label: str, value_var: StringVar, accent: str) -> None:
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=12, pady=10)
        dot = tk.Canvas(row, width=12, height=12, bg=CARD, highlightthickness=0)
        dot.pack(side="left", pady=3)
        dot.create_oval(2, 2, 10, 10, fill=accent, outline=accent)
        text = tk.Frame(row, bg=CARD)
        text.pack(side="left", fill="x", expand=True, padx=(10, 0))
        tk.Label(text, text=label, bg=CARD, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        tk.Label(text, textvariable=value_var, bg=CARD, fg=TEXT, font=("Segoe UI", 10, "bold"), wraplength=170, justify="left").pack(anchor="w")

    def _build_center_area(self, parent: tk.Widget) -> None:
        center = tk.Frame(parent, bg=BG)
        center.pack(side="left", fill="both", expand=True, padx=(14, 12), pady=14)

        header = tk.Frame(center, bg=BG)
        header.pack(fill="x", pady=(4, 14))
        tk.Label(header, text="Bases Cadastradas", bg=BG, fg=TEXT, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(
            header,
            text="Selecione uma base para editar, testar conexão ou definir como padrão.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(4, 0))

        table_card = tk.Frame(center, bg=PANEL, highlightbackground="#1f2a3c", highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        table_header = tk.Frame(table_card, bg=PANEL)
        table_header.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(table_header, text="Bases com conexão local e status de operação", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")

        table_wrap = tk.Frame(table_card, bg=PANEL)
        table_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.tree = ttk.Treeview(
            table_wrap,
            columns=("descricao", "servidor", "porta", "arquivo", "padrao", "ativo"),
            show="headings",
            selectmode="browse",
        )
        for column, title, width, anchor in (
            ("descricao", "Descrição", 260, "w"),
            ("servidor", "Servidor", 160, "center"),
            ("porta", "Porta", 90, "center"),
            ("arquivo", "Arquivo", 240, "w"),
            ("padrao", "Padrão", 90, "center"),
            ("ativo", "Ativo", 80, "center"),
        ):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor=anchor, stretch=True)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", lambda _event: self.edit_selected())

        self.empty_label = tk.Label(
            table_wrap,
            text="Nenhuma base cadastrada. Clique em Nova para configurar.",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 11),
        )

        footer = tk.Frame(center, bg=BG)
        footer.pack(fill="x", pady=(12, 0))
        left_buttons = tk.Frame(footer, bg=BG)
        left_buttons.pack(side="left")
        tk.Button(left_buttons, text="Nova", command=self.new_base, bg=ACCENT, fg="#ffffff", activebackground=ACCENT, activeforeground="#ffffff", bd=0, relief="flat", padx=16, pady=8).pack(side="left")
        tk.Button(left_buttons, text="Editar", command=self.edit_selected, bg="#1f2937", fg="#ffffff", activebackground="#1f2937", activeforeground="#ffffff", bd=0, relief="flat", padx=16, pady=8).pack(side="left", padx=8)
        tk.Button(left_buttons, text="Excluir", command=self.delete_selected, bg=DANGER, fg="#ffffff", activebackground=DANGER, activeforeground="#ffffff", bd=0, relief="flat", padx=16, pady=8).pack(side="left")

        right_buttons = tk.Frame(footer, bg=BG)
        right_buttons.pack(side="right")
        ttk.Checkbutton(
            right_buttons,
            text="Selecionar Base ao iniciar o sistema?",
            variable=self.select_on_start_var,
            command=self._toggle_select_on_start,
        ).pack(side="right")

    def _build_right_panel(self, parent: tk.Widget) -> None:
        panel = tk.Frame(parent, bg=BG, width=240)
        panel.pack(side="right", fill="y", padx=(10, 14), pady=14)
        panel.pack_propagate(False)

        tk.Label(panel, text="Ações", bg=BG, fg=TEXT, font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(6, 12))

        action_box = tk.Frame(panel, bg=CARD, highlightbackground="#1f2a3c", highlightthickness=1)
        action_box.pack(fill="x")
        for text, handler, color in (
            ("Selecionar", self.select_base, ACCENT),
            ("Base Padrão", self.set_default_selected, WARNING),
            ("Testar Conexão", self.test_selected_connection, SUCCESS),
            ("Iniciar API", self.start_api_action, "#2563eb"),
            ("Parar API", self.stop_api_action, DANGER),
            ("Testar API", self.test_api_action, "#14b8a6"),
            ("Abrir Docs", self.open_docs_action, "#475569"),
            ("Fechar", self.destroy, NEUTRAL),
        ):
            tk.Button(
                action_box,
                text=text,
                command=handler,
                bg=color,
                fg="#ffffff",
                activebackground=color,
                activeforeground="#ffffff",
                bd=0,
                relief="flat",
                padx=14,
                pady=9,
            ).pack(fill="x", padx=12, pady=(10, 0))

        info_box = tk.Frame(panel, bg=CARD, highlightbackground="#1f2a3c", highlightthickness=1)
        info_box.pack(fill="x", pady=(16, 0))
        tk.Label(info_box, text="Status", bg=CARD, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12, pady=(12, 8))
        self._status_detail(info_box, "API", self.api_status_var)
        self._status_detail(info_box, "Banco", self.bank_status_var)
        self._status_detail(info_box, "Padrão", self.default_base_var)
        self._status_detail(info_box, "Porta API", self.api_port_var)
        self._status_detail(info_box, "URL", self.api_url_var)

    def _status_detail(self, parent: tk.Widget, label: str, value_var: StringVar) -> None:
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill="x", padx=12, pady=4)
        tk.Label(row, text=f"{label}:", bg=CARD, fg=MUTED, font=("Segoe UI", 9, "bold"), width=12, anchor="w").pack(side="left")
        tk.Label(row, textvariable=value_var, bg=CARD, fg=TEXT, font=("Segoe UI", 9), anchor="w", justify="left", wraplength=160).pack(
            side="left", fill="x", expand=True
        )

    def _tick_clock(self) -> None:
        from datetime import datetime

        self.clock_label.configure(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.after(1000, self._tick_clock)

    def _toggle_select_on_start(self) -> None:
        self.store.set_select_on_start(bool(self.select_on_start_var.get()))

    def _ensure_api_started(self) -> None:
        def worker() -> None:
            if not is_api_running():
                self.after(0, lambda: self.api_status_var.set("Inicializando..."))
                start_api()
            self.after(0, self._update_status_panel)

        threading.Thread(target=worker, daemon=True).start()

    def refresh_bases(self) -> None:
        config = self.store.load_bases_config()
        self.bases = list(config.get("bases", []))
        self.select_on_start_var.set(bool(config.get("selecionar_base_ao_iniciar", False)))

        for item in self.tree.get_children():
            self.tree.delete(item)
        for base in self.bases:
            nome_arquivo = str(base.get("nome_arquivo") or "")
            caminho_base = str(base.get("caminho_base") or "")
            arquivo = str(Path(caminho_base) / nome_arquivo) if caminho_base and nome_arquivo else nome_arquivo
            self.tree.insert(
                "",
                "end",
                iid=str(base.get("id")),
                values=(
                    base.get("descricao", ""),
                    base.get("servidor", ""),
                    base.get("porta", ""),
                    arquivo,
                    "Sim" if base.get("base_padrao", False) else "",
                    "Sim" if base.get("ativo", True) else "Não",
                ),
            )

        selected = next((base for base in self.bases if base.get("base_padrao")), None)
        if selected is None and self.bases:
            selected = self.bases[0]
        self.selected_base_id = str(selected.get("id")) if selected else None
        if self.selected_base_id and self.tree.exists(self.selected_base_id):
            self.tree.selection_set(self.selected_base_id)
            self.tree.focus(self.selected_base_id)
            self.tree.see(self.selected_base_id)

        self._sync_empty_state()
        self._update_status_panel()

    def _sync_empty_state(self) -> None:
        if self.bases:
            self.empty_label.place_forget()
        else:
            self.empty_label.place(relx=0.5, rely=0.5, anchor="center")

    def _on_tree_select(self, _event=None) -> None:
        self.selected_base_id = self.get_current_tree_selection()
        self._update_status_panel()

    def get_current_tree_selection(self) -> str | None:
        selection = self.tree.selection()
        return selection[0] if selection else None

    def get_selected_base(self) -> dict[str, object] | None:
        selected_id = self.get_current_tree_selection() or self.selected_base_id
        if not selected_id:
            return None
        return next((base for base in self.bases if str(base.get("id")) == str(selected_id)), None)

    def new_base(self) -> None:
        BaseFormDialog(self, self.store, on_save=self._save_base_from_dialog)

    def edit_selected(self) -> None:
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Editar Base", "Selecione uma base primeiro.", parent=self)
            return
        BaseFormDialog(self, self.store, base=base, on_save=self._save_base_from_dialog)

    def _save_base_from_dialog(self, payload: dict[str, object]) -> None:
        base_id = str(payload.get("id") or "")
        if not base_id:
            existing = self.get_selected_base()
            if existing is not None:
                base_id = str(existing.get("id"))
        if base_id:
            payload["id"] = base_id
        self.store.upsert_base(payload)
        self.refresh_bases()

    def delete_selected(self) -> None:
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Excluir Base", "Selecione uma base primeiro.", parent=self)
            return
        if not messagebox.askyesno("Excluir Base", f"Excluir a base {base.get('descricao', '')}?", parent=self):
            return
        self.store.delete_base(str(base.get("id")))
        self.refresh_bases()

    def select_base(self) -> None:
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Selecionar Base", "Selecione uma base primeiro.", parent=self)
            return
        self.selected_base_id = str(base.get("id"))
        self.tree.selection_set(self.selected_base_id)
        self.tree.focus(self.selected_base_id)
        self.tree.see(self.selected_base_id)
        self._update_status_panel()

    def set_default_selected(self) -> None:
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Base Padrão", "Selecione uma base primeiro.", parent=self)
            return
        self.store.set_default(str(base.get("id")))
        self.refresh_bases()

    def test_selected_connection(self) -> None:
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Testar Conexão", "Selecione uma base primeiro.", parent=self)
            return

        def worker() -> None:
            result = test_connection(base)
            message = str(result.get("message", "Resultado indisponível."))
            if result.get("ok"):
                self.after(0, lambda: self.bank_status_var.set("Banco conectado"))
                self.after(0, lambda: messagebox.showinfo("Teste de Conexão", message, parent=self))
            else:
                self.after(0, lambda: self.bank_status_var.set("Falha de conexão"))
                self.after(0, lambda: messagebox.showerror("Teste de Conexão", message, parent=self))
            self.after(0, self._update_status_panel)

        threading.Thread(target=worker, daemon=True).start()

    def start_api_action(self) -> None:
        def worker() -> None:
            result = start_api()
            self.after(0, self._update_status_panel)
            if result.get("ok"):
                self.after(0, lambda: messagebox.showinfo("Iniciar API", str(result.get("message", "")), parent=self))
            else:
                self.after(0, lambda: messagebox.showerror("Iniciar API", str(result.get("message", "")), parent=self))

        threading.Thread(target=worker, daemon=True).start()

    def stop_api_action(self) -> None:
        def worker() -> None:
            result = stop_api()
            self.after(0, self._update_status_panel)
            if result.get("ok"):
                self.after(0, lambda: messagebox.showinfo("Parar API", str(result.get("message", "")), parent=self))
            else:
                self.after(0, lambda: messagebox.showwarning("Parar API", str(result.get("message", "")), parent=self))

        threading.Thread(target=worker, daemon=True).start()

    def test_api_action(self) -> None:
        def worker() -> None:
            result = test_health()
            self.after(0, self._update_status_panel)
            if result.get("ok"):
                self.after(0, lambda: messagebox.showinfo("Teste da API", str(result.get("message", "")), parent=self))
            else:
                self.after(0, lambda: messagebox.showerror("Teste da API", str(result.get("message", "")), parent=self))

        threading.Thread(target=worker, daemon=True).start()

    def open_docs_action(self) -> None:
        open_docs()

    def _update_status_panel(self) -> None:
        api_running = is_api_running()
        self.api_status_var.set("Rodando" if api_running else "Parada")
        self.api_url_var.set("http://localhost:8000")
        self.api_port_var.set("8000")

        selected = self.get_selected_base()
        if selected is None:
            self.selected_base_name_var.set("Nenhuma base selecionada")
            if self.bank_status_var.get() not in ("Banco conectado", "Falha de conexão"):
                self.bank_status_var.set("Banco em modo mock")
        else:
            self.selected_base_name_var.set(str(selected.get("descricao") or selected.get("apelido") or "Base selecionada"))

        default_base = next((base for base in self.bases if base.get("base_padrao")), None)
        if default_base is None:
            self.default_base_var.set("Nenhuma base padrão")
        else:
            self.default_base_var.set(str(default_base.get("descricao") or default_base.get("apelido") or "Base padrão"))


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

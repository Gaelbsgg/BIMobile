from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import BooleanVar, StringVar, Tk, Toplevel, messagebox, ttk

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.firebird import test_connection  # noqa: E402
from launcher.api_runner import is_api_running, open_docs, start_api, stop_api, test_health  # noqa: E402
from launcher.config_store import ConfigStore  # noqa: E402


BG = "#030712"
PANEL = "#09111e"
PANEL_ALT = "#0c1525"
BORDER = "#1f2a3a"
TEXT = "#e5eefb"
MUTED = "#8f9bb0"
ACCENT = "#0ea5e9"
SUCCESS = "#22c55e"
WARNING = "#f59e0b"
DANGER = "#ef4444"


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
        self.geometry("700x560")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.apelido_var = StringVar(value=str(self.base.get("apelido", "")))
        self.caminho_base_var = StringVar(value=str(self.base.get("caminho_base", "")))
        self.servidor_var = StringVar(value=str(self.base.get("servidor", "localhost")))
        self.nome_arquivo_var = StringVar(value=str(self.base.get("nome_arquivo", "")))
        self.usuario_var = StringVar(value=str(self.base.get("usuario_firebird", "SYSDBA")))
        self.senha_var = StringVar(value=str(self.base.get("senha_firebird", "masterkey")))
        self.porta_var = StringVar(value=str(self.base.get("porta", 3050)))
        self.protocolo_var = StringVar(value=str(self.base.get("protocolo", "TCP-IP")))
        self.linux_var = BooleanVar(value=bool(self.base.get("servidor_linux", False)))
        self.ativo_var = BooleanVar(value=bool(self.base.get("ativo", True)))
        self.default_var = BooleanVar(value=bool(self.base.get("base_padrao", False)))

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(50, self.apelido_entry.focus_set)

    def _field(self, parent: tk.Widget, label: str, widget) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=BG)
        tk.Label(wrapper, text=label, bg=BG, fg=TEXT, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))
        widget.pack(fill="x")
        return wrapper

    def _build_ui(self) -> None:
        container = tk.Frame(self, bg=BG, highlightbackground=BORDER, highlightthickness=1)
        container.pack(fill="both", expand=True, padx=16, pady=16)

        tk.Label(
            container,
            text="Gerenciador de Base de Dados - BIMobile API",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w", padx=18, pady=(18, 6))
        tk.Label(container, text="Cadastro e edição da conexão Firebird", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", padx=18, pady=(0, 14))

        form = tk.Frame(container, bg=BG)
        form.pack(fill="both", expand=True, padx=18, pady=(0, 14))
        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        self.apelido_entry = ttk.Entry(form, textvariable=self.apelido_var)
        self._field(form, "Apelido", self.apelido_entry).grid(row=0, column=0, columnspan=2, sticky="ew", pady=8)

        self.caminho_entry = ttk.Entry(form, textvariable=self.caminho_base_var)
        self._field(form, "Caminho da base de dados no servidor", self.caminho_entry).grid(row=1, column=0, columnspan=2, sticky="ew", pady=8)

        left_pair = tk.Frame(form, bg=BG)
        right_pair = tk.Frame(form, bg=BG)
        left_pair.columnconfigure(0, weight=1)
        right_pair.columnconfigure(0, weight=1)

        self.servidor_entry = ttk.Entry(left_pair, textvariable=self.servidor_var)
        self._field(left_pair, "IP Servidor / Portal", self.servidor_entry).pack(fill="x")

        self.arquivo_entry = ttk.Entry(right_pair, textvariable=self.nome_arquivo_var)
        self._field(right_pair, "Nome do Arquivo B.D.", self.arquivo_entry).pack(fill="x")

        left_pair.grid(row=2, column=0, sticky="ew", padx=(0, 8), pady=8)
        right_pair.grid(row=2, column=1, sticky="ew", padx=(8, 0), pady=8)

        left_pair_2 = tk.Frame(form, bg=BG)
        right_pair_2 = tk.Frame(form, bg=BG)
        left_pair_2.columnconfigure(0, weight=1)
        right_pair_2.columnconfigure(0, weight=1)

        self.usuario_entry = ttk.Entry(left_pair_2, textvariable=self.usuario_var)
        self._field(left_pair_2, "Usuário Firebird", self.usuario_entry).pack(fill="x")

        self.senha_entry = ttk.Entry(right_pair_2, textvariable=self.senha_var, show="•")
        self._field(right_pair_2, "Senha Firebird", self.senha_entry).pack(fill="x")

        left_pair_2.grid(row=3, column=0, sticky="ew", padx=(0, 8), pady=8)
        right_pair_2.grid(row=3, column=1, sticky="ew", padx=(8, 0), pady=8)

        left_pair_3 = tk.Frame(form, bg=BG)
        right_pair_3 = tk.Frame(form, bg=BG)
        left_pair_3.columnconfigure(0, weight=1)
        right_pair_3.columnconfigure(0, weight=1)

        self.porta_entry = ttk.Entry(left_pair_3, textvariable=self.porta_var)
        self._field(left_pair_3, "Porta", self.porta_entry).pack(fill="x")

        self.protocolo_combo = ttk.Combobox(right_pair_3, textvariable=self.protocolo_var, values=["TCP-IP", "NetBeui"], state="readonly")
        self._field(right_pair_3, "Protocolo Comunicação", self.protocolo_combo).pack(fill="x")

        left_pair_3.grid(row=4, column=0, sticky="ew", padx=(0, 8), pady=8)
        right_pair_3.grid(row=4, column=1, sticky="ew", padx=(8, 0), pady=8)

        options = tk.Frame(form, bg=BG)
        options.grid(row=5, column=0, columnspan=2, sticky="w", pady=(18, 0))
        ttk.Checkbutton(options, text="Servidor Linux", variable=self.linux_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(options, text="Ativo", variable=self.ativo_var).pack(side="left", padx=(0, 20))
        ttk.Checkbutton(options, text="Base Padrão", variable=self.default_var).pack(side="left")

        buttons = tk.Frame(container, bg=BG)
        buttons.pack(fill="x", padx=18, pady=(0, 18))
        ttk.Button(buttons, text="Testar Conexão", command=self._test_connection).pack(side="left")
        ttk.Button(buttons, text="Salvar", command=self._save).pack(side="right", padx=(10, 0))
        ttk.Button(buttons, text="Cancelar", command=self._close).pack(side="right")

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
            "usuario_firebird": self.usuario_var.get().strip() or "SYSDBA",
            "senha_firebird": self.senha_var.get(),
            "protocolo": self.protocolo_var.get(),
            "servidor_linux": bool(self.linux_var.get()),
            "ativo": bool(self.ativo_var.get()),
            "base_padrao": bool(self.default_var.get()),
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
            messagebox.showwarning("Cadastro de Base", "Preencha Apelido, Caminho da base e Nome do arquivo.", parent=self)
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
        self.title("Gerenciador de Base de Dados - BIMobile API")
        self.geometry("1220x720")
        self.minsize(1080, 680)
        self.configure(bg=BG)

        self.bases: list[dict[str, object]] = []
        self.selected_base_id: str | None = None
        self.select_on_start_var = BooleanVar(value=False)
        self.auto_refresh_var = BooleanVar(value=False)
        self.api_status_var = StringVar(value="API parada")
        self.connection_status_var = StringVar(value="Banco não testado")
        self.selection_status_var = StringVar(value="Nenhuma base selecionada")

        self._configure_styles()
        self._build_ui()
        self.refresh_bases()
        self._update_api_status()
        self.after(5000, self._auto_refresh_tick)

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
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, rowheight=34)
        style.configure("Treeview.Heading", background=PANEL_ALT, foreground=TEXT, font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", "#12324a")], foreground=[("selected", "#ffffff")])
        style.configure("TCheckbutton", background=BG, foreground=TEXT, font=("Segoe UI", 9))

    def _build_ui(self) -> None:
        root = tk.Frame(self, bg=BG)
        root.pack(fill="both", expand=True)
        self._build_left_rail(root)
        self._build_center_area(root)
        self._build_actions_panel(root)

    def _build_left_rail(self, parent: tk.Widget) -> None:
        left = tk.Frame(parent, bg=PANEL, width=220)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        canvas = tk.Canvas(left, width=88, height=88, bg=PANEL, highlightthickness=0)
        canvas.pack(pady=(28, 14))
        canvas.create_oval(12, 12, 76, 76, outline=ACCENT, width=4)
        canvas.create_text(44, 44, text="DB", fill=TEXT, font=("Segoe UI", 18, "bold"))

        tk.Label(left, text="BIMobile API", bg=PANEL, fg=TEXT, font=("Segoe UI", 16, "bold")).pack()
        tk.Label(left, text="Gerenciador de Base de Dados", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(pady=(4, 14))

        status_box = tk.Frame(left, bg=PANEL_ALT, highlightbackground=BORDER, highlightthickness=1)
        status_box.pack(fill="x", padx=16, pady=10)
        for label_var, color in (
            (self.api_status_var, ACCENT),
            (self.connection_status_var, SUCCESS),
            (self.selection_status_var, MUTED),
        ):
            row = tk.Frame(status_box, bg=PANEL_ALT)
            row.pack(fill="x", padx=12, pady=8)
            dot = tk.Canvas(row, width=10, height=10, bg=PANEL_ALT, highlightthickness=0)
            dot.pack(side="left")
            dot.create_oval(1, 1, 9, 9, fill=color, outline=color)
            tk.Label(row, textvariable=label_var, bg=PANEL_ALT, fg=TEXT, font=("Segoe UI", 9, "bold"), wraplength=150, justify="left").pack(side="left", padx=8)

        self.clock_label = tk.Label(left, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 9))
        self.clock_label.pack(side="bottom", pady=18)
        self._tick_clock()

    def _build_center_area(self, parent: tk.Widget) -> None:
        center = tk.Frame(parent, bg=BG)
        center.pack(side="left", fill="both", expand=True, padx=(14, 10), pady=14)

        header = tk.Frame(center, bg=BG)
        header.pack(fill="x", pady=(6, 14))
        tk.Label(header, text="Bases Cadastradas", bg=BG, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(header, text="Selecione uma base para editar, testar conexão ou definir como padrão.", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

        list_frame = tk.Frame(center, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        list_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("descricao", "servidor", "porta", "padrao", "ativo"), show="headings", selectmode="browse")
        for column, title, width in (
            ("descricao", "Descrição", 260),
            ("servidor", "Servidor", 140),
            ("porta", "Porta", 80),
            ("padrao", "Padrão", 90),
            ("ativo", "Ativo", 80),
        ):
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width, anchor="center" if column != "descricao" else "w")
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", lambda _event: self.edit_selected())

        bottom = tk.Frame(center, bg=BG)
        bottom.pack(fill="x", pady=(12, 0))
        ttk.Button(bottom, text="Nova", command=self.new_base).pack(side="left")
        ttk.Button(bottom, text="Editar", command=self.edit_selected).pack(side="left", padx=8)
        ttk.Button(bottom, text="Excluir", command=self.delete_selected).pack(side="left")

        toggles = tk.Frame(bottom, bg=BG)
        toggles.pack(side="right")
        ttk.Checkbutton(toggles, text="Selecionar Base ao iniciar o sistema?", variable=self.select_on_start_var, command=self._toggle_select_on_start).pack(side="left", padx=12)
        ttk.Checkbutton(toggles, text="Atualizar", variable=self.auto_refresh_var).pack(side="left")

    def _build_actions_panel(self, parent: tk.Widget) -> None:
        panel = tk.Frame(parent, bg=BG, width=190)
        panel.pack(side="right", fill="y", padx=(10, 14), pady=14)
        panel.pack_propagate(False)

        tk.Label(panel, text="Ações", bg=BG, fg=TEXT, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(8, 12))

        for label, callback in (
            ("Selecionar", self.select_base),
            ("Base Padrão", self.set_default_base),
            ("Iniciar API", self.handle_start_api),
            ("Parar API", self.handle_stop_api),
            ("Testar API", self.handle_test_api),
            ("Docs", self.handle_open_docs),
            ("Fechar", self.destroy),
        ):
            ttk.Button(panel, text=label, command=callback).pack(fill="x", pady=7)

        hint = tk.Frame(panel, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        hint.pack(fill="x", pady=(18, 0))
        tk.Label(hint, text="Status", bg=PANEL, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(12, 4))
        tk.Label(hint, text="API: http://localhost:8000", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=2)
        tk.Label(hint, text="Docs: /docs", bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(2, 12))

    def _tick_clock(self) -> None:
        from datetime import datetime

        self.clock_label.configure(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.after(1000, self._tick_clock)

    def _toggle_select_on_start(self) -> None:
        self.store.set_select_on_start(bool(self.select_on_start_var.get()))

    def _auto_refresh_tick(self) -> None:
        if self.auto_refresh_var.get():
            self.refresh_bases()
        self.after(5000, self._auto_refresh_tick)

    def refresh_bases(self) -> None:
        config = self.store.load_bases_config()
        self.bases = list(config.get("bases", []))
        self.select_on_start_var.set(bool(config.get("selecionar_base_ao_iniciar", False)))

        for item in self.tree.get_children():
            self.tree.delete(item)
        for base in self.bases:
            self.tree.insert(
                "",
                "end",
                iid=str(base.get("id")),
                values=(
                    base.get("descricao", ""),
                    base.get("servidor", ""),
                    base.get("porta", ""),
                    "Sim" if base.get("base_padrao") else "Não",
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
        self._refresh_selection_label()

    def _refresh_selection_label(self) -> None:
        base = self.get_selected_base()
        if base is None:
            self.selection_status_var.set("Nenhuma base selecionada")
            self.connection_status_var.set("Banco não testado")
            return
        self.selection_status_var.set(f"{base.get('descricao', '')}{' - padrão' if base.get('base_padrao') else ''}")
        self._sync_connection_status(base)

    def _sync_connection_status(self, base: dict[str, object]) -> None:
        result = test_connection(base)
        if result.get("ok"):
            if result.get("mode") == "mock":
                self.connection_status_var.set("Banco em modo mock")
            else:
                self.connection_status_var.set("Banco conectado")
            return
        self.connection_status_var.set("Falha de conexão")

    def _on_tree_select(self, _event=None) -> None:
        self.selected_base_id = self.get_current_tree_selection()
        self._refresh_selection_label()

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
        if payload.get("base_padrao"):
            self.store.set_default(str(payload["id"]))
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
        self._refresh_selection_label()
        messagebox.showinfo("Selecionar Base", f"Base selecionada: {base.get('descricao', '')}", parent=self)

    def set_default_base(self) -> None:
        base = self.get_selected_base()
        if base is None:
            messagebox.showwarning("Base Padrão", "Selecione uma base primeiro.", parent=self)
            return
        self.store.set_default(str(base.get("id")))
        self.refresh_bases()
        messagebox.showinfo("Base Padrão", f"{base.get('descricao', '')} definida como base padrão.", parent=self)

    def handle_start_api(self) -> None:
        result = start_api()
        self._update_api_status()
        if result.get("ok"):
            messagebox.showinfo("Iniciar API", str(result.get("message", "")), parent=self)
        else:
            messagebox.showerror("Iniciar API", str(result.get("message", "")), parent=self)

    def handle_stop_api(self) -> None:
        result = stop_api()
        self._update_api_status()
        if result.get("ok"):
            messagebox.showinfo("Parar API", str(result.get("message", "")), parent=self)
        else:
            messagebox.showwarning("Parar API", str(result.get("message", "")), parent=self)

    def handle_test_api(self) -> None:
        result = test_health()
        self._update_api_status()
        if result.get("ok"):
            messagebox.showinfo("Testar API", str(result.get("message", "")), parent=self)
        else:
            messagebox.showerror("Testar API", str(result.get("message", "")), parent=self)

    def handle_open_docs(self) -> None:
        open_docs()

    def _update_api_status(self) -> None:
        self.api_status_var.set("API rodando em http://localhost:8000" if is_api_running() else "API parada")


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

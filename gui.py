import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading

class ModernGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("名言佳句管理系統 (Threading 版)")
        self.root.geometry("800x600")
        self.api_url = "http://127.0.0.1:8000/quotes"
        self.selected_id = None  # 追蹤當前選取的資料 ID

        # --- 1. 資料顯示區 (Treeview) ---
        display_frame = ttk.Frame(root)
        display_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(display_frame, columns=("ID", "Author", "Text", "Tags"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=50, anchor="center")
        self.tree.heading("Author", text="作者"); self.tree.column("Author", width=120)
        self.tree.heading("Text", text="名言內容"); self.tree.column("Text", width=400)
        self.tree.heading("Tags", text="標籤"); self.tree.column("Tags", width=150)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # 事件綁定
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # --- 2. 新增/編輯區 ---
        edit_frame = tk.LabelFrame(root, text="新增/編輯區", padx=10, pady=10)
        edit_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(edit_frame, text="名言內容 (Text):").grid(row=0, column=0, sticky="nw")
        self.txt_content = tk.Text(edit_frame, height=5, width=95)
        self.txt_content.grid(row=0, column=1, columnspan=3, pady=5, sticky="we")

        tk.Label(edit_frame, text="作者 (Author):").grid(row=1, column=0, sticky="w")
        self.ent_author = tk.Entry(edit_frame, width=25)
        self.ent_author.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(edit_frame, text="標籤 (Tags):").grid(row=1, column=2, sticky="w", padx=(20, 0))
        self.ent_tags = tk.Entry(edit_frame, width=30)
        self.ent_tags.grid(row=1, column=3, sticky="w", pady=5)

        # --- 3. 操作選項區 ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=10)

        self.btn_refresh = tk.Button(btn_frame, text="重新整理 (Refresh)", bg="#ADD8E6", command=self.refresh_data)
        self.btn_refresh.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_add = tk.Button(btn_frame, text="新增 (Add)", bg="#90EE90", command=self.add_quote)
        self.btn_add.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_update = tk.Button(btn_frame, text="更新 (Update)", bg="#FFA500", state="disabled", command=self.update_quote)
        self.btn_update.pack(side="left", expand=True, fill="x", padx=2)

        self.btn_delete = tk.Button(btn_frame, text="刪除 (Delete)", bg="#F08080", state="disabled", command=self.delete_quote)
        self.btn_delete.pack(side="left", expand=True, fill="x", padx=2)

        # --- 4. 狀態列 ---
        self.status_var = tk.StringVar(value="系統就緒")
        self.status_bar = tk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padx=5)
        self.status_bar.pack(side="bottom", fill="x")

        # 啟動載入
        self.refresh_data()

    # --- 核心邏輯 ---

    def set_status(self, text, auto_clear=True):
        """更新狀態列文字"""
        self.status_var.set(text)
        if auto_clear:
            self.root.after(5000, lambda: self.status_var.set("準備就緒"))

    def on_tree_select(self, event):
        """連動行為：選取 Treeview 項目"""
        selection = self.tree.selection()
        if not selection: return
        
        item_data = self.tree.item(selection[0], "values")
        self.selected_id = item_data[0]
        
        # 填充輸入框
        self.txt_content.delete("1.0", tk.END)
        self.txt_content.insert("1.0", item_data[2])
        self.ent_author.delete(0, tk.END); self.ent_author.insert(0, item_data[1])
        self.ent_tags.delete(0, tk.END); self.ent_tags.insert(0, item_data[3])
        
        # 啟用按鈕
        self.btn_update.config(state="normal")
        self.btn_delete.config(state="normal")
        self.set_status(f"已選取 ID: {self.selected_id}", auto_clear=False)

    def clear_inputs(self):
        """清空所有輸入框並禁用按鈕"""
        self.txt_content.delete("1.0", tk.END)
        self.ent_author.delete(0, tk.END)
        self.ent_tags.delete(0, tk.END)
        self.btn_update.config(state="disabled")
        self.btn_delete.config(state="disabled")
        self.selected_id = None

    # --- 異步 API 請求 ---

    def refresh_data(self):
        self.set_status("連線中，請稍候...")
        def task():
            try:
                res = requests.get(self.api_url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    self.root.after(0, self._update_tree_ui, data)
                else:
                    self.root.after(0, self.set_status, "錯誤：無法獲取資料。")
            except:
                self.root.after(0, self.set_status, "錯誤：無法連線至後端 API。")
        threading.Thread(target=task, daemon=True).start()

    def _update_tree_ui(self, data):
        self.tree.delete(*self.tree.get_children())
        for q in data:
            self.tree.insert("", "end", values=(q['id'], q['author'], q['text'], q['tags']))
        self.set_status("資料載入完成")
        self.clear_inputs()

    def add_quote(self):
        payload = {
            "text": self.txt_content.get("1.0", "end-1c"),
            "author": self.ent_author.get(),
            "tags": self.ent_tags.get()
        }
        self.set_status("正在新增...")
        def task():
            try:
                res = requests.post(self.api_url, json=payload)
                if res.status_code == 200:
                    self.root.after(0, self.refresh_data)
                    self.root.after(0, self.set_status, "新增成功！")
            except: self.root.after(0, self.set_status, "新增失敗")
        threading.Thread(target=task, daemon=True).start()

    def update_quote(self):
        if not self.selected_id: return
        payload = {
            "text": self.txt_content.get("1.0", "end-1c"),
            "author": self.ent_author.get(),
            "tags": self.ent_tags.get()
        }
        self.set_status("正在更新...")
        def task():
            try:
                res = requests.put(f"{self.api_url}/{self.selected_id}", json=payload)
                if res.status_code == 200:
                    self.root.after(0, self.refresh_data)
                    self.root.after(0, self.set_status, "更新成功！")
                elif res.status_code == 404:
                    self.root.after(0, self.set_status, "錯誤：找不到目標資料。")
            except: self.root.after(0, self.set_status, "連線失敗")
        threading.Thread(target=task, daemon=True).start()

    def delete_quote(self):
        if not self.selected_id: return
        if not messagebox.askyesno("確認", f"確定要刪除 ID {self.selected_id} 嗎？"): return
        self.set_status("正在刪除...")
        def task():
            try:
                res = requests.delete(f"{self.api_url}/{self.selected_id}")
                if res.status_code == 200:
                    self.root.after(0, self.refresh_data)
                    self.root.after(0, self.set_status, "刪除成功！")
            except: self.root.after(0, self.set_status, "連線失敗")
        threading.Thread(target=task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernGUI(root)
    root.mainloop()
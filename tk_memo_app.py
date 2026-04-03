import tkinter as tk
from tkinter import messagebox
from datetime import datetime

# 今どのメモを編集中か覚える
editing_index = None

# 色設定
BG_COLOR = "#f4f7fb"
FRAME_COLOR = "#e9eef5"
BUTTON_COLOR = "#dbe7f5"
BUTTON_ACTIVE = "#c8daef"
ENTRY_COLOR = "#ffffff"
LISTBOX_COLOR = "#ffffff"
TEXT_COLOR = "#1f2937"
STATUS_COLOR = "#4b5563"


# 現在日時を文字列で返す
def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 表示用のメモ文字列を作る
def make_memo_text(content, status="未完了"):
    return f"[{status}] [{get_now()}] {content}"


# memo.txt からメモを全部読む
def get_all_memos():
    try:
        with open("memo.txt", "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []


# Listbox を指定した内容で更新する
def refresh_listbox(items):
    listbox.delete(0, tk.END)
    for item in items:
        listbox.insert(tk.END, item)


# 今の Listbox の内容を memo.txt に保存する
def save_memos():
    items = listbox.get(0, tk.END)

    with open("memo.txt", "w", encoding="utf-8") as file:
        for item in items:
            file.write(item + "\n")


# 起動時に memo.txt から読み込む
def load_memos():
    refresh_listbox(get_all_memos())


# 下に一瞬だけメッセージを表示する
def show_status(message):
    status_label.config(text=message)
    root.after(2000, lambda: status_label.config(text=""))


# 追加
def add_memo():
    memo = entry.get().strip()

    if memo == "":
        messagebox.showwarning("注意", "空のメモは追加できません。")
        return

    new_text = make_memo_text(memo, "未完了")
    listbox.insert(tk.END, new_text)
    entry.delete(0, tk.END)
    save_memos()
    show_status("メモを追加しました。")


# 削除
def delete_memo():
    selected = listbox.curselection()

    if not selected:
        messagebox.showwarning("注意", "削除するメモを選んでください。")
        return

    index = selected[0]
    text = listbox.get(index)

    result = messagebox.askyesno("確認", f"このメモを削除しますか？\n\n{text}")

    if not result:
        return

    listbox.delete(index)
    save_memos()
    show_status("メモを削除しました。")


# 編集するために入力欄へ入れる
def edit_memo():
    global editing_index

    selected = listbox.curselection()

    if not selected:
        messagebox.showwarning("注意", "編集するメモを選んでください。")
        return

    editing_index = selected[0]
    selected_text = listbox.get(editing_index)

    # [状態] [日時] 本文 から本文だけ抜き出す
    parts = selected_text.split("] ", 2)
    if len(parts) >= 3:
        content = parts[2]
    else:
        content = selected_text

    entry.delete(0, tk.END)
    entry.insert(0, content)


# 更新
def update_memo():
    global editing_index

    if editing_index is None:
        messagebox.showwarning("注意", "先に編集するメモを選んでください。")
        return

    new_content = entry.get().strip()

    if new_content == "":
        messagebox.showwarning("注意", "空の内容には更新できません。")
        return

    old_text = listbox.get(editing_index)

    # 元の状態を引き継ぐ
    if old_text.startswith("[完了]"):
        status = "完了"
    else:
        status = "未完了"

    new_text = make_memo_text(new_content, status)

    listbox.delete(editing_index)
    listbox.insert(editing_index, new_text)

    entry.delete(0, tk.END)
    editing_index = None
    save_memos()
    show_status("メモを更新しました。")


# 完了 / 未完了 を切り替える
def toggle_status():
    selected = listbox.curselection()

    if not selected:
        messagebox.showwarning("注意", "状態を変更するメモを選んでください。")
        return

    index = selected[0]
    current_text = listbox.get(index)

    # 本文を取り出す
    parts = current_text.split("] ", 2)
    if len(parts) >= 3:
        content = parts[2]
    else:
        content = current_text

    # 状態を切り替える
    if current_text.startswith("[完了]"):
        new_status = "未完了"
    else:
        new_status = "完了"

    new_text = make_memo_text(content, new_status)

    listbox.delete(index)
    listbox.insert(index, new_text)
    save_memos()
    show_status("状態を切り替えました。")


# 検索
def search_memo():
    keyword = search_entry.get().strip()
    all_items = get_all_memos()

    if keyword == "":
        refresh_listbox(all_items)
        return

    filtered = []

    for item in all_items:
        if keyword.lower() in item.lower():
            filtered.append(item)

    refresh_listbox(filtered)

    if not filtered:
        messagebox.showinfo("検索結果", "該当するメモがありません。")


# 一覧に戻す
def reset_search():
    refresh_listbox(get_all_memos())
    search_entry.delete(0, tk.END)


# マウスホイールでスクロール
def on_mousewheel(event):
    listbox.yview_scroll(int(-1 * (event.delta / 120)), "units")


# ----------------------------
# 画面づくり
# ----------------------------

root = tk.Tk()
root.title("メモアプリ")
root.geometry("760x590")
root.configure(bg=BG_COLOR)

# タイトル
title_label = tk.Label(
    root,
    text="メモアプリ",
    font=("Meiryo", 20, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
title_label.pack(pady=15)

# 上の入力欄
entry = tk.Entry(
    root,
    width=48,
    font=("Meiryo", 12),
    bg=ENTRY_COLOR,
    fg=TEXT_COLOR,
    relief="solid",
    bd=1
)
entry.pack(pady=8)

# 上のボタンたち
top_button_frame = tk.Frame(root, bg=BG_COLOR)
top_button_frame.pack(pady=8)


def make_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Meiryo", 11),
        width=9,
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        activebackground=BUTTON_ACTIVE,
        activeforeground=TEXT_COLOR,
        relief="flat",
        bd=0
    )


add_button = make_button(top_button_frame, "追加", add_memo)
add_button.pack(side=tk.LEFT, padx=4)

delete_button = make_button(top_button_frame, "削除", delete_memo)
delete_button.pack(side=tk.LEFT, padx=4)

edit_button = make_button(top_button_frame, "編集", edit_memo)
edit_button.pack(side=tk.LEFT, padx=4)

update_button = make_button(top_button_frame, "更新", update_memo)
update_button.pack(side=tk.LEFT, padx=4)

toggle_button = make_button(top_button_frame, "完了切替", toggle_status)
toggle_button.pack(side=tk.LEFT, padx=4)

# 検索欄
search_frame = tk.Frame(root, bg=BG_COLOR)
search_frame.pack(pady=10)

search_entry = tk.Entry(
    search_frame,
    width=32,
    font=("Meiryo", 11),
    bg=ENTRY_COLOR,
    fg=TEXT_COLOR,
    relief="solid",
    bd=1
)
search_entry.pack(side=tk.LEFT, padx=5)

search_button = make_button(search_frame, "検索", search_memo)
search_button.pack(side=tk.LEFT, padx=5)

reset_button = make_button(search_frame, "一覧に戻す", reset_search)
reset_button.pack(side=tk.LEFT, padx=5)

# 一覧表示エリアの枠
list_frame = tk.Frame(root, bg=FRAME_COLOR, bd=1, relief="solid")
list_frame.pack(padx=20, pady=15, fill="both", expand=True)

# スクロールバー
scrollbar = tk.Scrollbar(list_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 一覧表示
listbox = tk.Listbox(
    list_frame,
    width=80,
    height=16,
    font=("Meiryo", 11),
    bg=LISTBOX_COLOR,
    fg=TEXT_COLOR,
    selectbackground="#b7d3f2",
    selectforeground=TEXT_COLOR,
    relief="flat",
    bd=0,
    yscrollcommand=scrollbar.set
)
listbox.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)

scrollbar.config(command=listbox.yview)
listbox.bind("<MouseWheel>", on_mousewheel)

# ステータスメッセージ表示欄
status_label = tk.Label(
    root,
    text="",
    font=("Meiryo", 10),
    bg=BG_COLOR,
    fg=STATUS_COLOR
)
status_label.pack(pady=(0, 10))

# 起動時に読み込む
load_memos()

# 画面を表示し続ける
root.mainloop()
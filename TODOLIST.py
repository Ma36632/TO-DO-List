import flet as ft
import sqlite3

def main(page: ft.Page):
    page.window.always_on_top = True
    page.window.width = 370
    page.auto_scroll = True
    page.bgcolor = "#f7c6df"
    page.horizontal_alignment = "center"

    conn = sqlite3.connect("TODO.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, 
            date TEXT DEFAULT '', 
            status BOOL
        )
    """)

    cursor.execute("PRAGMA table_info(tasks)")
    columns = [column[1] for column in cursor.fetchall()]
    if "date" not in columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN date TEXT DEFAULT ''")
        conn.commit()

    conn.close()

    def add(task, date_field):
        task_value = task.value.strip()
        date_value = date_field.value.strip()
        
        if not task_value:
            task.helper_text = "Error: Task cannot be empty"
            task.update()
            return
        
        if not date_value:
            date_field.helper_text = "Error: Date required"
            date_field.update()
            return
        
        conn = sqlite3.connect("TODO.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (name, date, status) VALUES (?, ?, ?)", (task_value, date_value, False))
        conn.commit()
        conn.close()

        task.value = ""
        date_field.value = ""
        task.helper_text = ""
        date_field.helper_text = ""
        task.update()
        date_field.update()
        
        fetch()
        page.update()

    def fetch():
        selected_tab = tabs.selected_index
        conn = sqlite3.connect("TODO.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, date, status FROM tasks")
        data = cursor.fetchall()
        box1.controls.clear()
        colors = ["#853161", "#c793b1", "#853161", "#c793b1"]

        for idx, row in enumerate(data):
            task_id, task_name, task_date, task_status = row
            task_row = ft.Container(
                content=ft.Row([
                    ft.Checkbox(
                        value=bool(task_status),
                        on_change=lambda e, task_id=task_id: toggle_status(task_id, e.control.value),
                        fill_color=ft.colors.WHITE,
                        check_color="#853161"
                    ),
                    ft.Column([
                        ft.Text(value=task_name, size=16, weight="bold", color="#e8e8e8"),
                        ft.Text(value=f"📅 {task_date}", size=12, color="#f7f0f4")  
                    ]),
                    ft.IconButton(icon=ft.icons.DELETE, icon_color="#f7f0f4", on_click=lambda e, task_id=task_id: delete(task_id))
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=colors[idx % len(colors)],
                border_radius=20,
                padding=10,
                margin=5,
                width=320
            )
            box1.controls.append(task_row)

        conn.close()
        page.update()

    def delete(task_id):
        conn = sqlite3.connect("TODO.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        fetch()
        page.update()

    def toggle_status(task_id, new_status):
        conn = sqlite3.connect("TODO.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
        conn.commit()
        conn.close()
        fetch()
        page.update()

    def on_tab_change(e):
        fetch()

    text = ft.Text(value="TO-DO LIST", size=24, weight="bold", color="#853161")

    task = ft.TextField(
        hint_text="ADD TASK",
        helper_text="",
        border_width=2,
        border_color="#1D3557",
        border_radius=10,
        focused_border_color="#853161",
        border=ft.InputBorder.NONE,
        autofocus=True
    )

    date_field = ft.TextField(
        hint_text="DATE",
        border_width=2,
        border_color="#1D3557",
        border_radius=10,
        border=ft.InputBorder.NONE,
        focused_border_color="#853161",
        read_only=True,
        autofocus=True
    )

    # Update handle_change to format the date as "1 Feb 2025" (compatible with Windows)
    def handle_change(e):
        # Remove leading zero from the day manually
        day = e.control.value.day
        formatted_date = e.control.value.strftime(f'{day} %b %Y')
        date_field.value = formatted_date
        date_field.update()

    date_picker = ft.DatePicker(on_change=handle_change)
    date_field.on_click = lambda _: page.open(date_picker)

    btn = ft.Container(
        content=ft.ElevatedButton(
            text="Add ",on_click=lambda _: add(task, date_field),
            width=300,bgcolor="#853161",color="white"
        ),
        border_radius=30,
    )

    box1 = ft.Column([])

    input_box = ft.Container(
        content=ft.Column([
            task,
            date_field,
            btn
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),  
        padding=20,
        border_radius=15,
        bgcolor="#F6E8EA",
        width=500,
        shadow=ft.BoxShadow(blur_radius=8, spread_radius=2, color="#BFC0C0")
    )

    tabs = ft.Tabs(
        selected_index=0,
        on_change=on_tab_change,
        tabs=[
            ft.Tab(text=" All "),
            ft.Tab(text=" Active "),
            ft.Tab(text=" Complete ")
        ],
        indicator_color="#853161",
        label_color="#853161",
        padding=40  
    )

    task_box = ft.Container(content=box1, padding=10)

    page.add(text, input_box, tabs, task_box)
    fetch()

ft.app(target=main)

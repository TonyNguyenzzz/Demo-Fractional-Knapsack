# knapsack_demo.py

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

# Nhập khẩu các thành phần từ fractional_knapsack.py
from fractional_knapsack import fractional_knapsack, Item

class KnapsackDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Fractional Knapsack Demo")
        self.root.geometry("1600x900")  # Tăng kích thước cửa sổ để phù hợp với thay đổi

        # Khởi tạo danh sách các vật phẩm
        self.items = [
            Item("Laptop", 2000, 2.5),
            Item("First Aid Kit", 300, 0.5),
            Item("Water Bottle", 100, 1),
            Item("Tent", 800, 4),
            Item("Food Pack", 400, 2),
            Item("Camera", 1000, 1.5),
            Item("Sleeping Bag", 500, 3)
        ]
        self.capacity = 10
        self.current_step = -1
        self.is_running = False
        self.steps = []
        self.items_sorted = []
        self.images = {}
        self.backpack_image = None
        self.item_labels = []
        self.load_images()
        self.setup_ui()

    def load_images(self):
        self.images = {}
        # Tạo thư mục 'images' chứa các file hình ảnh vật phẩm và balo
        images_dir = "images"
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            print(f"Folder '{images_dir}' created. Please add item images and backpack.png.")

        image_files = {
            "Laptop": "laptop.png",
            "First Aid Kit": "firstaid.png",
            "Water Bottle": "water.png",
            "Tent": "tent.png",
            "Food Pack": "food.png",
            "Camera": "camera.png",
            "Sleeping Bag": "sleepingbag.png",
            "Backpack": "backpack.png"
        }

        for item in self.items + [Item("Backpack", 0, 0)]:
            image_path = os.path.join(images_dir, image_files.get(item.name, ""))
            if os.path.exists(image_path):
                try:
                    # Đối với Pillow >= 10.0.0, sử dụng Image.Resampling.LANCZOS
                    # Đối với Pillow < 10.0.0, sử dụng Image.LANCZOS
                    try:
                        resample_mode = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample_mode = Image.LANCZOS

                    if item.name == "Backpack":
                        img = Image.open(image_path).resize((500, 600), resample_mode)
                    else:
                        img = Image.open(image_path).resize((50, 50), resample_mode)
                    self.images[item.name] = ImageTk.PhotoImage(img)
                    if item.name == "Backpack":
                        self.backpack_image = self.images[item.name]
                except Exception as e:
                    print(f"Cannot load image for {item.name}: {e}")
                    if item.name == "Backpack":
                        img = Image.new("RGB", (500, 600), color="lightgray")
                        self.backpack_image = ImageTk.PhotoImage(img)
                    else:
                        img = Image.new("RGB", (50, 50), color="lightgray")
                        self.images[item.name] = ImageTk.PhotoImage(img)
            else:
                if item.name == "Backpack":
                    img = Image.new("RGB", (500, 600), color="lightgray")
                    self.backpack_image = ImageTk.PhotoImage(img)
                else:
                    img = Image.new("RGB", (50, 50), color="lightgray")
                    self.images[item.name] = ImageTk.PhotoImage(img)

    def setup_ui(self):
        main_container = ttk.Frame(self.root, padding="5")
        main_container.pack(fill="both", expand=True)

        main_container.columnconfigure(0, weight=1, minsize=200)
        main_container.columnconfigure(1, weight=4)
        main_container.rowconfigure(0, weight=1)

        # Left panel - Controls và Status
        left_panel = ttk.Frame(main_container, padding="5")
        left_panel.grid(row=0, column=0, sticky="ns")

        # Controls
        controls = ttk.LabelFrame(left_panel, text="Controls", padding="5")
        controls.pack(fill="x", pady=2)

        ttk.Label(controls, text="Backpack Capacity (kg):").grid(row=0, column=0, padx=2, pady=2, sticky=tk.W)
        self.capacity_var = tk.StringVar(value=str(self.capacity))
        ttk.Entry(controls, textvariable=self.capacity_var, width=8).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(controls, text="Start Demo", command=self.start_demo).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(controls, text="Reset", command=self.reset_demo).grid(row=1, column=1, padx=2, pady=2)

        # Status
        status = ttk.LabelFrame(left_panel, text="Status Overview", padding="5")
        status.pack(fill="x", pady=2)

        ttk.Label(status, text="Status:", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3, sticky="w", padx=2, pady=2)

        icon_label = ttk.Label(status, text="🔋", font=("Arial", 10))
        icon_label.grid(row=1, column=0, sticky="w", padx=2, pady=2)
        ttk.Label(status, text="Remaining Capacity:", font=("Arial", 10)).grid(row=1, column=1, sticky="w", padx=2, pady=2)
        self.remaining_var = tk.StringVar(value=str(self.capacity))
        ttk.Label(status, textvariable=self.remaining_var, font=("Arial", 10, "bold")).grid(row=1, column=2, sticky="e", padx=2, pady=2)

        icon_label = ttk.Label(status, text="💰", font=("Arial", 10))
        icon_label.grid(row=2, column=0, sticky="w", padx=2, pady=2)
        ttk.Label(status, text="Total Value:", font=("Arial", 10)).grid(row=2, column=1, sticky="w", padx=2, pady=2)
        self.total_value_var = tk.StringVar(value="0.0")
        ttk.Label(status, textvariable=self.total_value_var, font=("Arial", 10, "bold")).grid(row=2, column=2, sticky="e", padx=2, pady=2)

        ttk.Label(status, text="Progress:", font=("Arial", 10)).grid(row=3, column=0, columnspan=2, sticky="w", padx=2, pady=2)
        self.progress = ttk.Progressbar(status, length=150, mode='determinate')
        self.progress.grid(row=3, column=2, sticky="e", padx=2, pady=2)

        # Explanation
        explanation = ttk.LabelFrame(left_panel, text="Explanation", padding="5")
        explanation.pack(fill="both", expand=True, pady=2)

        # Sử dụng Treeview với columns mới
        columns = (
            "Step", 
            "Item", 
            "Value/Weight Ratio",
            "Selection Reason",
            "Fraction (%)", 
            "Value Added ($)", 
            "Total Value ($)", 
            "Remaining Capacity (kg)"
        )
        
        self.explanation_tree = ttk.Treeview(explanation, columns=columns, show='headings', height=15)
        
        # Cấu hình các cột
        for col in columns:
            self.explanation_tree.heading(col, text=col)
            if col == "Step":
                self.explanation_tree.column(col, anchor="center", width=50)
            elif col == "Item":
                self.explanation_tree.column(col, anchor="center", width=100)
            elif col == "Value/Weight Ratio":
                self.explanation_tree.column(col, anchor="center", width=120)
            elif col == "Selection Reason":
                self.explanation_tree.column(col, anchor="center", width=200)
            elif col == "Fraction (%)":
                self.explanation_tree.column(col, anchor="center", width=100)
            elif col == "Value Added ($)":
                self.explanation_tree.column(col, anchor="center", width=120)
            elif col == "Total Value ($)":
                self.explanation_tree.column(col, anchor="center", width=120)
            elif col == "Remaining Capacity (kg)":
                self.explanation_tree.column(col, anchor="center", width=150)

        self.explanation_tree.pack(fill="both", expand=True)

        # Right panel - Available Items và Backpack Visualization
        right_panel = ttk.Frame(main_container, padding="5")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(1, weight=1)  # Backpack Visualization

        # Available Items Frame - chỉ 1 hàng
        items_frame = ttk.LabelFrame(right_panel, text="Available Items", padding="5")
        items_frame.grid(row=0, column=0, sticky="ew", pady=5)
        items_frame.columnconfigure(tuple(range(len(self.items))), weight=1)

        # Hiển thị items trong một hàng với icon nhỏ
        for idx, item in enumerate(self.items):
            frame = ttk.Frame(items_frame, padding=3, borderwidth=1, relief="groove")
            frame.grid(row=0, column=idx, padx=2, pady=2, sticky="nsew")
            if self.images[item.name]:
                img_label = ttk.Label(frame, image=self.images[item.name])
                img_label.image = self.images[item.name]
                img_label.pack(padx=1, pady=1)
            ratio = item.value / item.weight
            ttk.Label(frame, text=f"{item.name}\n${item.value}\n{item.weight}kg\nRatio: {ratio:.2f}", 
                     justify="center", font=("Arial", 8)).pack()
            self.item_labels.append({
                'item': item,
                'frame': frame,
                'image_label': img_label if self.images[item.name] else None,
                'selected': False,
                'fraction': 0
            })

        # Backpack Visualization Frame - diện tích lớn hơn
        backpack_frame = ttk.LabelFrame(right_panel, text="Backpack", padding="5")
        backpack_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        backpack_frame.columnconfigure(0, weight=1)
        backpack_frame.rowconfigure(0, weight=1)

        self.backpack_canvas = tk.Canvas(backpack_frame, width=500, height=600, bg="white")
        self.backpack_canvas.pack(fill="both", expand=True)

        if self.backpack_image:
            self.backpack_canvas.create_image(250, 300, image=self.backpack_image)

        self.backpack_items = []

    def get_selection_reason(self, item, ratio, fraction, remaining_cap):
        """Tạo giải thích chi tiết về lý do chọn item."""
        if self.current_step == 0:
            return f"Highest value/weight ratio ({ratio:.2f})"
        elif fraction == 1.0:
            return f"Next best ratio ({ratio:.2f}), fits completely"
        else:
            return f"Partial fit ({fraction*100:.1f}%) with ratio {ratio:.2f}"

    def reset_demo(self):
        self.is_running = False
        self.current_step = -1
        try:
            self.capacity = float(self.capacity_var.get())
        except ValueError:
            self.capacity = 10
            self.capacity_var.set("10")
        self.remaining_var.set(f"{self.capacity:.1f}")
        self.total_value_var.set("0.0")
        self.progress['value'] = 0
        self.explanation_tree.delete(*self.explanation_tree.get_children())

        for label in self.item_labels:
            label['selected'] = False
            label['fraction'] = 0
            for widget in label['frame'].winfo_children():
                if isinstance(widget, ttk.Label) and "Selected:" in widget.cget("text"):
                    widget.destroy()
            label['frame'].configure(style="TFrame")

        self.backpack_canvas.delete("selected_item")
        self.backpack_items = []

    def run_step(self):
        if not self.is_running:
            return

        if self.current_step >= len(self.steps) - 1:
            self.is_running = False
            self.show_final_summary()
            return

        self.current_step += 1
        item, fraction, total_val, remaining_cap = self.steps[self.current_step]

        # Cập nhật trạng thái
        self.remaining_var.set(f"{remaining_cap:.1f}")
        self.total_value_var.set(f"{total_val:.1f}")
        self.progress['value'] = ((self.capacity - remaining_cap) / self.capacity) * 100

        # Tính tỷ lệ giá trị trên trọng lượng và lý do chọn
        ratio = item.value / item.weight
        selection_reason = self.get_selection_reason(item, ratio, fraction, remaining_cap)

        # Cập nhật giải thích trong Treeview
        step_number = self.current_step + 1
        fraction_percent = fraction * 100
        value_added = item.value * fraction
        
        self.explanation_tree.insert("", "end", values=(
            step_number,
            item.name,
            f"{ratio:.2f}",
            selection_reason,
            f"{fraction_percent:.1f}%",
            f"{value_added:.1f}",
            f"{total_val:.1f}",
            f"{remaining_cap:.1f}"
        ))

        # Cập nhật giao diện
        self.update_interface(item, fraction)
        self.root.after(2000, self.run_step)

    def show_final_summary(self):
        """Hiển thị tổng kết chi tiết khi demo kết thúc."""
        summary = "Fractional Knapsack Solution Summary:\n\n"
        
        # Giải thích về thuật toán
        summary += "Algorithm Steps:\n"
        summary += "1. Items were sorted by value/weight ratio (higher is better).\n"
        summary += "2. Selected items in order of decreasing ratio.\n"
        summary += "3. Used fractions when needed to maximize value.\n\n"
        
        # Thống kê về items đã chọn
        summary += "Selected Items:\n"
        item_fractions = {}
        for step in self.steps:
            item, fraction, _, _ = step
            if item.name in item_fractions:
                item_fractions[item.name] += fraction
            else:
                item_fractions[item.name] = fraction
        for item in self.items_sorted:
            frac = item_fractions.get(item.name, 0)
            summary += f"- {item.name}: {frac * item.weight:.2f}kg ({frac * 100:.1f}%)\n"
        summary += f"\nTotal Value: ${self.total_value_var.get()}"

        messagebox.showinfo("Demo Completed", summary)

    def update_interface(self, item, fraction):
        """Cập nhật giao diện khi một vật phẩm được chọn."""
        # Làm nổi bật vật phẩm đã chọn
        for label in self.item_labels:
            if label['item'].name == item.name:
                label['selected'] = True
                label['fraction'] = fraction
                # Thêm nhãn "Selected" nếu chưa có
                existing_labels = [w for w in label['frame'].winfo_children() if isinstance(w, ttk.Label) and "Selected:" in w.cget("text")]
                if not existing_labels:
                    selection_label = ttk.Label(label['frame'], text=f"Selected: {fraction*100:.1f}%", foreground="green", font=("Arial", 8))
                    selection_label.pack(side="left", padx=2)
                # Thay đổi style frame
                label['frame'].configure(style="Selected.TFrame")
                break

        # Thêm vật phẩm vào balo
        self.add_to_backpack(item, fraction)

    def add_to_backpack(self, item: Item, fraction: float):
        # Tính vị trí dựa trên số lượng vật phẩm đã thêm
        y_offset = 50 + len(self.backpack_items) * 60  # Vị trí bắt đầu từ trên xuống dưới
        # Tính kích thước dựa trên trọng lượng và tỷ lệ
        width = (item.weight * fraction) * 40  # Điều chỉnh tỉ lệ phù hợp
        # Vẽ hình chữ nhật đại diện cho vật phẩm trên balo
        rect = self.backpack_canvas.create_rectangle(250 - width/2, y_offset - 20, 250 + width/2, y_offset + 20, fill="lightgreen", outline="black", tags="selected_item")
        # Thêm văn bản
        self.backpack_canvas.create_text(250, y_offset, text=f"{item.name}\n({fraction*100:.1f}%)", tags="selected_item")
        self.backpack_items.append(rect)

    def start_demo(self):
        self.reset_demo()
        self.is_running = True
        try:
            capacity = float(self.capacity_var.get())
        except ValueError:
            capacity = self.capacity
            self.capacity_var.set("10")
        self.capacity = capacity
        self.remaining_var.set(f"{self.capacity:.1f}")
        self.total_value_var.set("0.0")
        self.progress['value'] = 0

        # Thực hiện thuật toán Fractional Knapsack
        total_value, self.steps, self.items_sorted = fractional_knapsack(self.items, self.capacity)
        self.run_step()

if __name__ == "__main__":
    root = tk.Tk()

    # Định nghĩa style để làm nổi bật các frame đã được chọn
    style = ttk.Style()
    style.configure("Selected.TFrame", background="lightyellow")

    app = KnapsackDemo(root)
    root.mainloop()

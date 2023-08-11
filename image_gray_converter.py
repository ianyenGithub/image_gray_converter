import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import threading

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("圖片轉換Tool")
        
        視窗寬度 = 400  # 視窗寬度
        視窗高度 = 400  # 視窗高度
        x = self.root.winfo_screenwidth() / 3
        y = self.root.winfo_screenheight() / 3
        self.root.geometry(f"{視窗寬度}x{視窗高度}+{int(x)}+{int(y)}")
        
        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        self.input_image_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.num_levels = tk.IntVar()
        self.num_levels.set(8)

        self.create_widgets()

        self.frame.update_idletasks()

        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def create_widgets(self):
        input_frame = tk.Frame(self.frame)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

        tk.Label(input_frame, text="輸入圖片路徑:").grid(row=0, column=0, sticky='w')
        tk.Entry(input_frame, textvariable=self.input_image_path).grid(row=0, column=1, columnspan=2, sticky='we')
        tk.Button(input_frame, text="瀏覽", command=self.browse_input_image).grid(row=0, column=3, sticky='e')

        tk.Label(input_frame, text="輸出資料夾:").grid(row=1, column=0, sticky='w')
        tk.Entry(input_frame, textvariable=self.output_folder).grid(row=1, column=1, columnspan=2, sticky='we')
        tk.Button(input_frame, text="瀏覽", command=self.browse_output_folder).grid(row=1, column=3, sticky='e')

        tk.Label(input_frame, text="灰階等級數量(1-256):").grid(row=2, column=0, sticky='w')
        tk.Entry(input_frame, textvariable=self.num_levels).grid(row=2, column=1, columnspan=2, sticky='we')

        tk.Button(input_frame, text="轉換", command=self.convert_image).grid(row=3, column=0, columnspan=4, sticky='we')

        self.status_label = tk.Label(self.frame, text="", fg="green")
        self.status_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky='w')

        self.image_label = tk.Label(self.frame, highlightthickness=0)
        self.image_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')


    def browse_input_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("圖片檔案", "*.jpg *.jpeg *.png")])
        self.input_image_path.set(file_path)

    def browse_output_folder(self):
        folder = filedialog.askdirectory()
        self.output_folder.set(folder)

    def convert_image(self):
        input_path = self.input_image_path.get()
        output_folder = self.output_folder.get()
        num_levels = self.num_levels.get()

        if not input_path or not output_folder:
            self.status_label.config(text="請選擇輸入圖片和輸出資料夾。", fg="red")
            self.root.update_idletasks()  # 立即更新GUI
            return
    
        try:
            num_levels = int(num_levels)
            if not (1 <= num_levels <= 256):
                raise ValueError
        except ValueError:
            self.status_label.config(text="無效的灰階等級數量。請輸入1到256之間的數字。", fg="red")
            self.root.update_idletasks()  # 立即更新GUI
            return
    
        os.makedirs(output_folder, exist_ok=True)

        self.status_label.config(text="正在轉換...", fg="black")

        # 在單獨的線程中執行轉換
        threading.Thread(target=self.process_images_thread, args=(input_path, output_folder, num_levels)).start()

    def process_images_thread(self, input_path, output_folder, num_levels):
        image = Image.open(input_path)
        gray_image = image.convert("L")
        gray_levels = list(range(0, 256, 256 // num_levels))

        for level in gray_levels:
            self.process_image(level, gray_image, output_folder, num_levels)

        self.status_label.config(text="轉換完成！", fg="green")

    def process_image(self, level, gray_image, output_folder, num_levels):
        new_image = Image.new("RGBA", gray_image.size, (255, 255, 255, 0))
        mapped_image = gray_image.point(lambda p: level if abs(level - p) < (256 // num_levels) else p)

        for x in range(mapped_image.width):
            for y in range(mapped_image.height):
                pixel = mapped_image.getpixel((x, y))
                if pixel != level:
                    new_image.putpixel((x, y), (255, 255, 255, 0))
                else:
                    new_image.putpixel((x, y), (pixel, pixel, pixel, 255))

        output_path = os.path.join(output_folder, f"gray_{level}.png")
        new_image.save(output_path, "PNG")

        self.status_label.config(text=f"處理圖片 {level}...", fg="black")

        self.update_image(output_path)
        
    def update_image(self, image_path):
        img = Image.open(image_path)
        
        # 計算在視窗可見區域內最大縮略圖大小
        screen_width = 800
        screen_height = 600/2

        max_thumbnail_size = min(screen_width, screen_height) - 20  # 減去一些間距

        img.thumbnail((max_thumbnail_size, max_thumbnail_size))
        
        img = ImageTk.PhotoImage(img)
        self.image_label.config(image=img)
        self.image_label.image = img

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()

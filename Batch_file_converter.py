from tkinter import *
from tkinter import ttk                     # подключаем пакет ttk, улучшенные виджеты
from tkinter import filedialog              # графический интерфейс выбора папок
import os                                   # работа с файлами
import subprocess                           # запуск внешних программ/утилит
from tkinter.ttk import Progressbar         # визуализация прогрес-бара
from exif import Image                      # доступ к EXIF данным
import rawpy                                # конвертация RAW в JPG
import imageio                              # конвертация RAW в JPG


class Window:
    def __init__(self, width, height, title="MyWindow", resizable=(True, True)) -> None:
        self.root = Tk()                                # Инициалиция окна
        self.root.title(title)                          # название окна
        self.root.geometry(f"{width}x{height}+100+100") # "Ширина x Высота + Смещение по X + Смещение по Y"
        self.root.minsize(530,300)                      # минимальные размеры: ширина - 200, высота - 150
        self.root.resizable(resizable[0], resizable[1]) # изменение окна по осям              

        self.list_jpg_files = []
        self.list_heic_files = []
        self.list_raw_files = []
        
        self.col_width = 15

        self.from_folder = Entry()
        self.to_folder = Entry()

        self.file_type_jpg = BooleanVar(value=True)
        self.file_type_jpg_text = StringVar(value='JPG')
        self.file_type_heic = BooleanVar(value=False)
        self.file_type_heic_text = StringVar(value='HEIC')
        self.file_type_raw = BooleanVar(value=False)
        self.file_type_raw_text = StringVar(value='RAW')

        self.name_set_date = BooleanVar(value=True)
        self.name_set_camera = BooleanVar(value=True)
        self.name_set_version = BooleanVar(value=False)

        self.set_exif = StringVar(value='original')

        self.current_info_var = StringVar(value='')
        self.current_info = Label(self.root, textvariable=self.current_info_var)
        self.current_file_var = StringVar(value='')
        self.current_file = Label(self.root, textvariable=self.current_file_var)

        self.progressbar_var = IntVar(value=0)
        self.progressbar = Progressbar(self.root, orient=HORIZONTAL, mode="determinate", length=500)
 
        self.cur_progress = 0
        
        Label(self.root, height=1, text="Batch processing of Photos", font="Arial 16 bold roman", fg='blue').grid(row=0, column=0, pady=6, columnspan=5, sticky=E+W)
        
        Label(self.root, width=self.col_width, height=1, text="From folder:").grid(row=1, column=0, sticky=W)
        
        self.from_folder.grid(row=1, column=1, columnspan=3, sticky=E+W)
        from_folder_btn = ttk.Button(text="Open", command=self.set_from_folder) # Выводим кнопку и отслеживаем её нажатие
        from_folder_btn.grid(row=1, column=4, sticky=NW)

        Label(self.root, width=self.col_width, height=1, text="To folder:").grid(row=2, column=0, sticky=W)

        self.to_folder.grid(row=2, column=1, columnspan=3, sticky=E+W)
        to_folder_btn = ttk.Button(text="Open", command=self.set_to_folder) # Выводим кнопку и отслеживаем её нажатие
        to_folder_btn.grid(row=2, column=4, sticky=NW)
        
        Label(self.root, width=self.col_width, height=1, text="File types:").grid(row=4, column=0, pady=6, sticky=W)
        
        file_type_jpg_check = ttk.Checkbutton(textvariable=self.file_type_jpg_text, variable=self.file_type_jpg, width=self.col_width)
        file_type_jpg_check.grid(row=4, column=1, sticky=W)
        file_type_heic_check = ttk.Checkbutton(textvariable=self.file_type_heic_text, variable=self.file_type_heic, width=self.col_width)
        file_type_heic_check.grid(row=4, column=2, sticky=W)
        file_type_raw_check = ttk.Checkbutton(textvariable=self.file_type_raw_text, variable=self.file_type_raw, width=self.col_width)
        file_type_raw_check.grid(row=4, column=3, sticky=W)

        Label(self.root, width=self.col_width, height=1, text="EXIF info:").grid(row=5, column=0, pady=6, sticky=W)
       
        file_type_jpg_check = ttk.Radiobutton(text="Original", width=self.col_width, value='original', variable=self.set_exif)
        file_type_jpg_check.grid(row=5, column=1, sticky=W)
        file_type_heic_check = ttk.Radiobutton(text="Delete GPS", width=self.col_width, value='del_gps', variable=self.set_exif)
        file_type_heic_check.grid(row=5, column=2, sticky=W)
        file_type_raw_check = ttk.Radiobutton(text="Delete all", width=self.col_width, value='del_all', variable=self.set_exif)
        file_type_raw_check.grid(row=5, column=3, sticky=W)

        Label(self.root, width=self.col_width, height=1, text="Rename files:").grid(row=6, column=0, pady=6, sticky=W)
        
        file_type_jpg_check = ttk.Checkbutton(text="Date&Time", width=self.col_width, variable=self.name_set_date)
        file_type_jpg_check.grid(row=6, column=1, sticky=W)
        file_type_heic_check = ttk.Checkbutton(text="Camera", width=self.col_width, variable=self.name_set_camera)
        file_type_heic_check.grid(row=6, column=2, sticky=W)
        file_type_raw_check = ttk.Checkbutton(text="Version", width=self.col_width, variable=self.name_set_version)
        file_type_raw_check.grid(row=6, column=3, sticky=W)

        start_btn = ttk.Button(text="SATRT", command=self.start_process) # Выводим кнопку и отслеживаем её нажатие
        start_btn.grid(row=7, column=1, columnspan=3, sticky=E+W)

        self.progressbar.grid(row=8, column=0, columnspan=5, sticky=E+W, pady=6)
        self.current_info.grid(row=9, column=0, columnspan=5, sticky=E+W)
        self.current_file.grid(row=10, column=0, columnspan=5, sticky=E+W)


    def change_progressbar(self):
        self.progressbar.configure(value=self.progressbar_var.get())
        self.progressbar.update()


    def get_file_list(self, path_from, file_type):  # получаем список файлов, удовлетворяющих критерию
        with os.scandir(path_from) as files:
            files = [file.name for file in files if file.is_file() and file.name.lower().endswith(file_type)]
        return files    
    
    
    def create_folder(self, new_folder):            # создаём папку, если её нет
        if not os.path.exists(new_folder):
            try:
                os.mkdir(new_folder)
            except IOError as error:
                print(error)

    def refresh_quantity(self):                     # получаем количество файлов в указанной папке
        self.list_jpg_files = []
        self.list_jpg_files += self.get_file_list(self.from_folder.get(), 'jpg')
        self.list_jpg_files += self.get_file_list(self.from_folder.get(), 'jpeg')
        self.file_type_jpg_text.set(value=f'JPG (+{len(self.list_jpg_files)})')

        self.list_heic_files = self.get_file_list(self.from_folder.get(), 'heic')
        self.file_type_heic_text.set(value=f'HEIC (+{len(self.list_heic_files)})')

        self.list_raw_files = []
        self.list_raw_files += self.get_file_list(self.from_folder.get(), 'cr2')    # Canon
        self.list_raw_files += self.get_file_list(self.from_folder.get(), 'cr3')    # Canon
        self.list_raw_files += self.get_file_list(self.from_folder.get(), 'nef')    # Nikon
        self.file_type_raw_text.set(value=f'RAW (+{len(self.list_raw_files)})')


    def set_from_folder(self):                      # получаем папку исходников 
        filepath = filedialog.askdirectory()
        self.from_folder.delete(0, END)
        self.from_folder.insert(0, filepath)
        if self.to_folder.get() == "":
            self.to_folder.insert(0, f'{filepath}/JPG')
        self.refresh_quantity()


    def set_to_folder(self):                        # получаем папку назначение
        filepath = filedialog.askdirectory()
        self.to_folder.delete(0, END)
        self.to_folder.insert(0, filepath)

    
    def exif_process(self, from_folder, to_folder, file, filename):
        with_error = False
        new_filename = filename
        with open(f'{from_folder}/{file}', 'rb') as img_file:
            image = Image(img_file)

            if image.has_exif:
                new_filename = self.create_new_filename(to_folder, image, filename)
                
                # удаление геолокации
                if self.set_exif.get() == 'del_gps':
                    exif_tags = dir(image)
                    gps_keys = []
                    for i in range(len(exif_tags)):
                        if exif_tags[i].lower().startswith('gps'):
                            gps_keys.append(exif_tags[i])

                    # print(f'gps_keys = {gps_keys}')
                    for i in range(len(gps_keys)):
                        image.delete(gps_keys[i])
                        # print(f'In File {file} Tag {gps_keys[i]} was deleted.')


                # удаление EXIF информации
                if self.set_exif.get() == 'del_all':
                    orientation = image.get('orientation', False)
                    try:
                        image.delete_all()
                    except IOError as error:
                        print(error)
                        with_error = True
                    except RuntimeError as error:
                        print(error)

                    # if with_error:
                    #     exif_tags = dir(image)
                    #     with_error = False
                    #     for i in range(len(exif_tags)):
                    #         try:
                    #             image.delete(exif_tags[i])
                    #         except IOError as error:
                    #             print(error)
                    #             with_error = True

                    if orientation:
                        try:
                            image.orientation = orientation
                        except IOError as error:
                            print(error)
                        except RuntimeError as error:
                            print(error)
            # else:
            #     print(f"File {file} does not contain any EXIF information.")

            if not with_error:
                # print(f'new_filename = {new_filename}')
                with open(f'{to_folder}/{new_filename}', 'wb') as new_file:
                    new_file.write(image.get_file())


    # определяем суммарное количество файлов для обработки, для визуализации процесса
    def get_sum_files(self):
        sum_quantity = 0
        if self.file_type_jpg.get():
            sum_quantity += len(self.list_jpg_files)
        if self.file_type_heic.get():
            sum_quantity += len(self.list_heic_files)
        if self.file_type_raw.get():
            sum_quantity += len(self.list_raw_files)
        return sum_quantity


    def jpg_process(self, from_folder, to_folder, file, new_filename):
        # print(f'{from_folder}/{file}')
        self.exif_process(from_folder, to_folder, file, new_filename)


    def heic_process(self, from_folder, to_folder, file):
        # print(f'{from_folder}/{file}')
        temp_file = 'temp.jpg'
        new_file = file[0:-5] + '.jpg'
        subprocess.run(["magick", f"{from_folder}/{file}", f"{to_folder}/{temp_file}"])
        self.jpg_process(to_folder, to_folder, temp_file, new_file)
        
        if os.path.exists(to_folder + '/' + temp_file):
            os.remove(to_folder + '/' + temp_file)
        else:
            print("The file does not exist")
    

    def raw_to_jpg(self, from_folder, to_folder, file, temp_file):
        filepath_from = from_folder + '/' + file
        filepath_to = to_folder + '/' + temp_file

        with rawpy.imread(filepath_from) as raw_file:
            # raises rawpy.LibRawNoThumbnailError if thumbnail missing
            # raises rawpy.LibRawUnsupportedThumbnailError if unsupported format
            thumb = raw_file.extract_thumb()
        if thumb.format == rawpy.ThumbFormat.JPEG:
            # thumb.data is already in JPEG format, save as-is
            with open(filepath_to, 'wb') as f:
                f.write(thumb.data)
        elif thumb.format == rawpy.ThumbFormat.BITMAP:
            # thumb.data is an RGB numpy array, convert with imageio
            imageio.imsave(filepath_to, thumb.data)


    def raw_process(self, from_folder, to_folder, file):
        # print(f'{from_folder}/{file}')
        temp_file = 'temp.jpg'
        new_file = file[0:-4] + '.jpg'
        self.raw_to_jpg(from_folder, to_folder, file, temp_file)
        self.jpg_process(to_folder, to_folder, temp_file, new_file)
        
        if os.path.exists(to_folder + '/' + temp_file):
            os.remove(to_folder + '/' + temp_file)

        
    def view_current_progress(self, file):
        self.progressbar_var.set(self.cur_progress)
        self.cur_progress += 1

        progress = int(self.cur_progress / self.get_sum_files() * 100)
        self.progressbar_var.set(progress)
        self.current_info_var.set(f'Progress:  file {self.cur_progress} from {self.get_sum_files()} ({progress}%)')
        self.current_file_var.set(f'Converting: {file}')
        self.change_progressbar()


    def create_new_filename(self, to_folder, image, filename):
        if self.name_set_date.get() == self.name_set_camera.get() == self.name_set_version.get() == 0 or \
            image.get('datetime', False) == image.get('make', False) == image.get('model', False):
            new_file_name = filename
        else:
            new_file_name = ''
            if self.name_set_date.get():
                if image.get('datetime', False):
                    for char in str(image.datetime):
                        if char != ":":
                            if char == ' ':
                                new_file_name += '_'
                            else:
                                new_file_name += char
                
                if image.get('subsec_time_original', False):
                    new_file_name += '.' + image.subsec_time_original 
            
            if self.name_set_camera.get():
                if self.name_set_date.get():
                    new_file_name += '_'
                if image.get('make', False):  
                    new_file_name += image.make 
                
            if self.name_set_version.get():
                if self.name_set_camera.get():
                    new_file_name += '_'
                if image.get('model', False):  
                    for char in str(image.model):
                        if char == ' ':
                            new_file_name += "_"
                        else:
                            new_file_name += char

            new_file_name += '.jpg'
        
        if os.path.exists(to_folder + '/' + new_file_name):
            filename_verification = True
            count = 0
            # new_file_name += '_'
            new_file_name = new_file_name[0:-4] + '_'
            while filename_verification:
                count += 1
                if not os.path.exists(to_folder + '/' + new_file_name + str(count) + '.jpg'):
                    new_file_name += str(count) + '.jpg'
                    filename_verification = False

        return new_file_name

    def start_process(self):
        from_folder = self.from_folder.get()
        to_folder = self.to_folder.get()
        self.cur_progress = 0

        if len(self.list_jpg_files) + len(self.list_heic_files) + len(self.list_raw_files) == 0:
            return
        
        # определяем суммарное количество файлов для обработки, для визуализации процесса
        self.sum_files = self.get_sum_files()
        self.progressbar_var.set(0)

        # создаём папку назначение
        self.create_folder(to_folder)

        # преобразуем jpg (из оригинальной папки)
        if self.file_type_jpg.get() and len(self.list_jpg_files) > 0:
            for file in self.list_jpg_files:
                self.view_current_progress(file)
                self.jpg_process(from_folder, to_folder, file, file)

        # преобразуем heic в jpg
        if self.file_type_heic.get() and len(self.list_heic_files) > 0:
            for file in self.list_heic_files:
                self.view_current_progress(file)
                self.heic_process(from_folder, to_folder, file)
                continue

        # преобразуем raw в jpg
        if self.file_type_raw.get() and len(self.list_raw_files) > 0:
            for file in self.list_raw_files:
                self.view_current_progress(file)
                self.raw_process(from_folder, to_folder, file)
        
        self.current_file_var.set('')


    def run(self):
        # self.draw_widgets()
        self.root.mainloop()

if __name__ == "__main__":
    window = Window(530, 300, "Batch file converter")
    window.run()
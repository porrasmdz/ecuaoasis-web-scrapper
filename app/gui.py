import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import sys
from config import settings
sys.path.append(settings.ROOT_ABSOLUTE_PATH)
from shopify_robot import publishProductsToShopify
from scrapper import scrap_product_info
from core.driver_factory import WebDriverFactory
from logging_instance import customLogger
import pandas as pd
import logging
import threading
import os
import sv_ttk

# theme_dir = "forest-dark/"
# theme_file = "forest-dark.tcl"
iconfile = "favicon-alt.ico"
if not hasattr(sys, "frozen"):
    iconfile = os.path.join(os.path.dirname(__file__), iconfile)
    # theme_file = os.path.join(os.path.dirname(__file__), theme_file)
    # theme_dir = os.path.join(os.path.dirname(__file__), theme_dir)
    
else:
    iconfile = os.path.join(sys.prefix, iconfile)
    # theme_file = os.path.join(sys.prefix, theme_file)
    # theme_dir = os.path.join(sys.prefix, theme_dir)
class Application(tk.Tk):
    def __init__(self,version):
        super().__init__()
        self.title(f"Integrador Universal Ecuaoasis v{version}")
        self.option_add("*tearOff", False)

        # Configuración de columnas y filas de la ventana principal
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        for i in range(2):
            self.rowconfigure(i, weight=1)

        
        sv_ttk.set_theme("dark")

        #version and icon
        self.app_id =f"ecuaoasis.web_scrapper.gui.{version}"
        self.iconbitmap(default=iconfile)
    
        # Variables de control
    
        self.progress = tk.DoubleVar(value=0)
        self.links = []
        self.products = []
        self.tabdict = {}

        # Inicializar logging
        self.logger = customLogger(logging.DEBUG, filename="logs/robot_results.log")

        # Configurar UI
        self.setup_ui()

    def setup_ui(self):
        # Frame para los links
        self.frame_links = ttk.LabelFrame(self, text="Listado de Origen", padding=(10, 5))
        self.frame_links.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Botones y entrada para los links
        self.setup_link_widgets()

        # Tabla de links
        self.setup_links_table()

        # Frame para el estado y barra de progreso
        self.setup_status_frame()

        # Frame para los resultados
        self.setup_results_frame()

        # Notebook para los logs
        self.setup_log_notebook()
        self.state("zoomed")
        # self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        # self.attributes('-fullscreen', True)
        self.resizable(False, False)
    
    def close(self):
        self.destroy()

    def mostrar_alerta_actualizacion(self):
        messagebox.showinfo("Control de versiones", "Se va a realizar una actualización. Por favor vuelva abrir la aplicación.")
        self.close()
        
    def mostrar_alerta_generica(self, message):
        messagebox.showinfo("Control de versiones",message)
      

    def setup_link_widgets(self):
        # Botón para subir archivo
        btn_subir = ttk.Button(self.frame_links, text="Suba Archivo", command=self.subir_archivo, style="Accent.TButton")
        btn_subir.grid(row=0, column=0, padx=5, pady=5, columnspan=2, sticky="ew")

        # Entrada para añadir links
        self.entry_link = ttk.Entry(self.frame_links)
        self.entry_link.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.entry_link.insert(0, "...O pegue aqui un link y oprima ENTER")
        self.entry_link.bind('<Return>', lambda event: self.agregar_link(self.entry_link))

    def setup_links_table(self):
        # Tabla (Treeview) para los links
        self.tree = ttk.Treeview(self.frame_links, columns=("link",), show="headings")
        self.tree.heading("link", text=f"Links ({len(self.links)})")
        self.tree.grid(row=2, column=0, columnspan=2, sticky="nsew")

        # Scrollbar para la tabla de links
        scrollbar_links = ttk.Scrollbar(self.frame_links, orient="vertical", command=self.tree.yview)
        scrollbar_links.grid(row=2, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar_links.set)

        self.frame_links.rowconfigure(2, weight=1)
        self.frame_links.columnconfigure(0, weight=1)

        # Menú contextual para eliminar links
        self.menu_contextual = tk.Menu(self.tree, tearoff=0)
        self.menu_contextual.add_command(label="Eliminar", command=self.eliminar_link)
        self.tree.bind("<Button-3>", self.mostrar_menu_contextual)

    def setup_status_frame(self):
        # Frame para mostrar el estado y la barra de progreso
        self.frame_estado = ttk.Frame(self.frame_links, padding=(10, 5))
        self.frame_estado.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        self.label_estado = ttk.Label(self.frame_estado, text="Estado: ")
        self.label_estado.grid(row=0, padx=5, pady=5)

        self.progress_bar = ttk.Progressbar(self.frame_estado, orient="horizontal", mode="determinate", variable=self.progress)
        self.progress_bar.grid(row=1, padx=5, pady=5, sticky="ew")
        self.actualizar_estado("Declarando los links", 0)

        # Botón para iniciar la extracción
        btn_iniciar = ttk.Button(self.frame_estado, text="Iniciar Extracción", command=self.iniciar_extraccion,  style="Accent.TButton")
        btn_iniciar.grid(row=0, column=1, padx=5, pady=5)

    def setup_results_frame(self):
        # Frame para los resultados
        self.frame_tabla = ttk.LabelFrame(self, text="Resultados de Extracción", padding=(10, 5))
        self.frame_tabla.grid(row=0, column=1,sticky="nsew", padx=5, pady=5)

        # Treeview para los resultados
        self.results_tree = ttk.Treeview(self.frame_tabla, columns=("col1", "col2", "col3"), show="headings")
        self.results_tree.heading("col1", text="Productos")
        self.results_tree.heading("col2", text="Precio")
        self.results_tree.heading("col3", text="Núm. de variantes")
        self.results_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar para la tabla de resultados
        scrollbar = ttk.Scrollbar(self.frame_tabla, orient="vertical", command=self.results_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.results_tree.configure(yscrollcommand=scrollbar.set)

        self.frame_tabla.rowconfigure(0, weight=1)
        self.frame_tabla.columnconfigure(0, weight=1)

        self.actualizar_resultados()

    def setup_log_notebook(self):
        # Notebook para los logs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        log_types = ['Ejecución General', 'Shopify']
        for log_type in log_types:
            tab = ttk.Frame(self.notebook, height=40)
            self.notebook.add(tab, text=log_type)
            text_widget = ScrolledText(tab, wrap=tk.WORD, bg="black", fg="white", font=("Consolas", 11))  # Ajustes de color
            text_widget.pack(fill=tk.BOTH)
            self.tabdict[log_type] = text_widget
            self.mostrar_logs(text_widget, "logs/robot_results.log")

            # Ajuste opcional para mostrar logs específicos en cada pestaña
            if log_type == 'Ejecución General':
                filename = "logs/robot_results.log"
                self.mostrar_logs(text_widget, filename=filename)
            if log_type == 'Shopify':
                filename = "logs/shopify.log"
                self.mostrar_logs(text_widget, filename=filename)

    def agregar_link(self, entry):
        link = entry.get()
        if link and link not in self.links:
            self.links.append(link)
            entry.delete(0, tk.END)
            self.actualizar_tabla()

    def subir_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if archivo:
            df = pd.read_excel(archivo)
            for link in df.iloc[:, 0]:
                if link not in self.links:
                    self.links.append(link)
            self.actualizar_tabla()

    def mostrar_menu_contextual(self, event):
        seleccion = self.tree.identify_row(event.y)
        if seleccion:
            self.tree.selection_set(seleccion)
            self.menu_contextual.post(event.x_root, event.y_root)

    def eliminar_link(self):
        seleccion = self.tree.selection()
        if seleccion:
            for item in seleccion:
                link = self.tree.item(item, "values")[0]
                self.links.remove(link)
                self.tree.delete(item)
            self.actualizar_tabla()

    def actualizar_tabla(self):
        self.tree.heading("link", text=f"Links ({len(self.links)})")

        for i in self.tree.get_children():
            self.tree.delete(i)
        for link in self.links:
            self.tree.insert("", tk.END, values=(link,))

    def actualizar_resultados(self):
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)
        for product in self.products:
            if product is not None:
                summary = product.summary()
                self.results_tree.insert("", tk.END, values=(summary['title'], summary['price'], summary['num_variants']))

        self.results_tree.heading("col1", text=f"Productos ({len(self.products)})")

    def actualizar_estado(self, estado, valor_progreso):
        self.label_estado.config(text=f"Estado: {estado}")
        self.progress.set(valor_progreso)
        self.update_idletasks()

    def mostrar_logs(self, text_widget:ScrolledText, filename):
        try:
            with open(filename, 'r') as log_file:
                logs = log_file.readlines()
                text_widget.config(state=tk.NORMAL)
                text_widget.delete('1.0', tk.END)
                for log in logs:
                    text_widget.insert(tk.END, log)
                text_widget.see(tk.END)
                text_widget.config(state=tk.DISABLED)
        except FileNotFoundError:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete('1.0', tk.END)
            text_widget.insert(tk.END, "Archivo de logs no encontrado.")
            text_widget.config(state=tk.DISABLED)

    def center_window(self):
        # Centrar la ventana en la pantalla
        self.update()
        x_cordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        y_cordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        self.geometry("+{}+{}".format(x_cordinate, y_cordinate))

    def update_logs_cb(self):
        self.mostrar_logs(self.tabdict["Ejecución General"], "logs/robot_results.log")
        self.mostrar_logs(self.tabdict["Shopify"], "logs/shopify.log")

    def iniciar_extraccion(self):
        def extraccion_en_hilo():
            self.logger.info("Enmascarando IP con Proxy...")
            self.actualizar_estado("Enmascarando IP con Proxy...", 10)
            self.update_logs_cb()
            wdf = WebDriverFactory("chrome")
            driver = wdf.getWebDriverInstance(logger_cb=self.update_logs_cb)
            self.update_logs_cb()
            self.logger.info("Iniciando extracción de productos...")
            self.actualizar_estado("Extrayendo productos...", 40)
            self.update_logs_cb()
            # Simulación de extracción de productos
            for link in self.links:
                try:
                    product = scrap_product_info(link, driver, logger_cb=self.update_logs_cb)
            
                    self.products.append(product)
                    
                    # Actualizar la interfaz en el hilo principal después de cada producto extraído
                    self.after(0, self.actualizar_resultados)
                    self.after(0, self.update_logs_cb)
                except Exception as e:
                    self.logger.info(f"Error al extraer producto {link} {str(e)}")
                
            self.logger.info("Productos extraídos correctamente.")
            self.update_logs_cb()
            self.actualizar_estado("Extracción completada", 60)
            driver.quit()
            self.actualizar_estado("Subiendo a Shopify", 80)
            self.logger.info("Conexión al navegador finalizada.")
            self.logger.info("Subiendo productos a la tienda...")
            self.update_logs_cb()
            
            publishProductsToShopify(self.products, self.update_logs_cb)
            self.logger.info("Proceso de carga finalizado.")
            
            self.actualizar_estado("Completado", 100)
            self.update_logs_cb()
        # Crear y comenzar el hilo para la extracción
        self.extraccion_thread = threading.Thread(target=extraccion_en_hilo)
        self.extraccion_thread.start()
        
        self.logger.info("Esto puede tomar unos minutos. Por favor, espere...")
        self.update_logs_cb()
        # Lógica para iniciar la extracción de productos
        
       
       
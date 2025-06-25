import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from sqlalchemy.orm import Session
from database import init_db, get_session
from models import Ingrediente, Menu, Cliente, Pedido
from crud.ingrediente_crud import (
    crear_ingrediente, listar_ingredientes, actualizar_ingrediente, eliminar_ingrediente
)
from crud.menu_crud import (
    crear_menu, listar_menus, actualizar_menu, eliminar_menu, obtener_ingredientes_menu
)
from crud.cliente_crud import (
    crear_cliente, listar_clientes, actualizar_cliente, eliminar_cliente
)
from crud.pedido_crud import (
    crear_pedido, listar_pedidos, listar_pedidos_por_cliente, eliminar_pedido
)
from graficos import GraficoFactory
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

# Configuración de customtkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class RestauranteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.title("Sistema de Gestión de Restaurante")
        self.geometry("1200x800")
        
        # Inicializar la base de datos
        self.engine = init_db()
        self.session = get_session(self.engine)
        
        # Crear pestañas
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Añadir pestañas
        self.tabview.add("Ingredientes")
        self.tabview.add("Menús")
        self.tabview.add("Clientes")
        self.tabview.add("Pedidos")
        self.tabview.add("Panel de Compra")
        self.tabview.add("Estadísticas")
        
        # Configurar cada pestaña
        self.setup_ingredientes_tab()
        self.setup_menus_tab()
        self.setup_clientes_tab()
        self.setup_pedidos_tab()
        self.setup_compra_tab()
        self.setup_estadisticas_tab()
        
        # Cargar datos iniciales
        self.cargar_ingredientes()
        self.cargar_menus()
        self.cargar_clientes()
        self.cargar_pedidos()
    
    # ========== Configuración de pestañas ==========
    
    def setup_ingredientes_tab(self):
        tab = self.tabview.tab("Ingredientes")
        
        # Frame para formulario
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # Campos del formulario
        ctk.CTkLabel(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ing_nombre = ctk.CTkEntry(form_frame)
        self.ing_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Tipo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ing_tipo = ctk.CTkComboBox(form_frame, values=["Vegetal", "Proteína", "Lácteo", "Cereal", "Condimento", "Otro"])
        self.ing_tipo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Cantidad:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.ing_cantidad = ctk.CTkEntry(form_frame)
        self.ing_cantidad.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Unidad de Medida:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.ing_unidad = ctk.CTkComboBox(form_frame, values=["kg", "g", "l", "ml", "unidades"])
        self.ing_unidad.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Botones
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ctk.CTkButton(button_frame, text="Agregar", command=self.agregar_ingrediente).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Actualizar", command=self.actualizar_ingrediente).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Eliminar", command=self.eliminar_ingrediente).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Limpiar", command=self.limpiar_formulario_ingrediente).pack(side="left", padx=5)
        
        # Treeview para mostrar ingredientes
        self.ing_tree = ttk.Treeview(tab, columns=("ID", "Nombre", "Tipo", "Cantidad", "Unidad"), show="headings")
        self.ing_tree.heading("ID", text="ID")
        self.ing_tree.heading("Nombre", text="Nombre")
        self.ing_tree.heading("Tipo", text="Tipo")
        self.ing_tree.heading("Cantidad", text="Cantidad")
        self.ing_tree.heading("Unidad", text="Unidad")
        
        self.ing_tree.column("ID", width=50)
        self.ing_tree.column("Nombre", width=150)
        self.ing_tree.column("Tipo", width=100)
        self.ing_tree.column("Cantidad", width=80)
        self.ing_tree.column("Unidad", width=80)
        
        self.ing_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar evento de selección
        self.ing_tree.bind("<<TreeviewSelect>>", self.seleccionar_ingrediente)
    
    def setup_menus_tab(self):
        tab = self.tabview.tab("Menús")
        
        # Frame principal dividido en dos
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para formulario y lista de ingredientes
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Formulario de menú
        menu_form_frame = ctk.CTkFrame(left_frame)
        menu_form_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(menu_form_frame, text="Nombre del Menú:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.menu_nombre = ctk.CTkEntry(menu_form_frame)
        self.menu_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(menu_form_frame, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.menu_descripcion = ctk.CTkEntry(menu_form_frame)
        self.menu_descripcion.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(menu_form_frame, text="Precio:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.menu_precio = ctk.CTkEntry(menu_form_frame)
        self.menu_precio.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Botones para menú
        menu_button_frame = ctk.CTkFrame(menu_form_frame)
        menu_button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ctk.CTkButton(menu_button_frame, text="Agregar Menú", command=self.agregar_menu).pack(side="left", padx=5)
        ctk.CTkButton(menu_button_frame, text="Actualizar Menú", command=self.actualizar_menu).pack(side="left", padx=5)
        ctk.CTkButton(menu_button_frame, text="Eliminar Menú", command=self.eliminar_menu).pack(side="left", padx=5)
        ctk.CTkButton(menu_button_frame, text="Limpiar", command=self.limpiar_formulario_menu).pack(side="left", padx=5)
        
        # Frame para ingredientes del menú
        ingredientes_frame = ctk.CTkFrame(left_frame)
        ingredientes_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(ingredientes_frame, text="Ingredientes del Menú").pack()
        
        # Treeview para ingredientes del menú
        self.menu_ing_tree = ttk.Treeview(ingredientes_frame, columns=("ID", "Nombre", "Cantidad", "Unidad"), show="headings")
        self.menu_ing_tree.heading("ID", text="ID")
        self.menu_ing_tree.heading("Nombre", text="Nombre")
        self.menu_ing_tree.heading("Cantidad", text="Cantidad")
        self.menu_ing_tree.heading("Unidad", text="Unidad")
        
        self.menu_ing_tree.column("ID", width=50)
        self.menu_ing_tree.column("Nombre", width=150)
        self.menu_ing_tree.column("Cantidad", width=80)
        self.menu_ing_tree.column("Unidad", width=80)
        
        self.menu_ing_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para agregar ingredientes al menú
        add_ing_frame = ctk.CTkFrame(ingredientes_frame)
        add_ing_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(add_ing_frame, text="Agregar Ingrediente:").pack(side="left", padx=5)
        
        self.menu_ing_combo = ctk.CTkComboBox(add_ing_frame, state="readonly")
        self.menu_ing_combo.pack(side="left", padx=5, expand=True, fill="x")
        
        ctk.CTkLabel(add_ing_frame, text="Cantidad:").pack(side="left", padx=5)
        self.menu_ing_cantidad = ctk.CTkEntry(add_ing_frame, width=60)
        self.menu_ing_cantidad.pack(side="left", padx=5)
        
        ctk.CTkButton(add_ing_frame, text="+", width=30, command=self.agregar_ingrediente_a_menu).pack(side="left", padx=5)
        ctk.CTkButton(add_ing_frame, text="-", width=30, command=self.remover_ingrediente_de_menu).pack(side="left", padx=5)
        
        # Frame para lista de menús
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(right_frame, text="Menús Disponibles").pack()
        
        # Treeview para menús
        self.menu_tree = ttk.Treeview(right_frame, columns=("ID", "Nombre", "Descripción", "Precio"), show="headings")
        self.menu_tree.heading("ID", text="ID")
        self.menu_tree.heading("Nombre", text="Nombre")
        self.menu_tree.heading("Descripción", text="Descripción")
        self.menu_tree.heading("Precio", text="Precio")
        
        self.menu_tree.column("ID", width=50)
        self.menu_tree.column("Nombre", width=150)
        self.menu_tree.column("Descripción", width=200)
        self.menu_tree.column("Precio", width=80)
        
        self.menu_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar evento de selección
        self.menu_tree.bind("<<TreeviewSelect>>", self.seleccionar_menu)
        
        # Actualizar combo de ingredientes
        self.actualizar_combo_ingredientes()
    
    def setup_clientes_tab(self):
        tab = self.tabview.tab("Clientes")
        
        # Frame para formulario
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # Campos del formulario
        ctk.CTkLabel(form_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.cli_nombre = ctk.CTkEntry(form_frame)
        self.cli_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.cli_email = ctk.CTkEntry(form_frame)
        self.cli_email.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Botones
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ctk.CTkButton(button_frame, text="Agregar", command=self.agregar_cliente).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Actualizar", command=self.actualizar_cliente).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Eliminar", command=self.eliminar_cliente).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Limpiar", command=self.limpiar_formulario_cliente).pack(side="left", padx=5)
        
        # Treeview para mostrar clientes
        self.cli_tree = ttk.Treeview(tab, columns=("ID", "Nombre", "Email"), show="headings")
        self.cli_tree.heading("ID", text="ID")
        self.cli_tree.heading("Nombre", text="Nombre")
        self.cli_tree.heading("Email", text="Email")
        
        self.cli_tree.column("ID", width=50)
        self.cli_tree.column("Nombre", width=150)
        self.cli_tree.column("Email", width=200)
        
        self.cli_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar evento de selección
        self.cli_tree.bind("<<TreeviewSelect>>", self.seleccionar_cliente)
    
    def setup_pedidos_tab(self):
        tab = self.tabview.tab("Pedidos")
        
        # Frame para filtros
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(filter_frame, text="Filtrar por Cliente:").pack(side="left", padx=5)
        self.pedido_cliente_filter = ctk.CTkComboBox(filter_frame, state="readonly")
        self.pedido_cliente_filter.pack(side="left", padx=5, expand=True, fill="x")
        self.pedido_cliente_filter.set("Todos")
        
        ctk.CTkButton(filter_frame, text="Aplicar Filtro", command=self.filtrar_pedidos).pack(side="left", padx=5)
        ctk.CTkButton(filter_frame, text="Mostrar Todos", command=self.mostrar_todos_pedidos).pack(side="left", padx=5)
        
        # Treeview para mostrar pedidos
        self.ped_tree = ttk.Treeview(tab, columns=("ID", "Cliente", "Menú", "Cantidad", "Total", "Fecha"), show="headings")
        self.ped_tree.heading("ID", text="ID")
        self.ped_tree.heading("Cliente", text="Cliente")
        self.ped_tree.heading("Menú", text="Menú")
        self.ped_tree.heading("Cantidad", text="Cantidad")
        self.ped_tree.heading("Total", text="Total")
        self.ped_tree.heading("Fecha", text="Fecha")
        
        self.ped_tree.column("ID", width=50)
        self.ped_tree.column("Cliente", width=150)
        self.ped_tree.column("Menú", width=150)
        self.ped_tree.column("Cantidad", width=80)
        self.ped_tree.column("Total", width=80)
        self.ped_tree.column("Fecha", width=120)
        
        self.ped_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Botón para eliminar pedido
        button_frame = ctk.CTkFrame(tab)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(button_frame, text="Eliminar Pedido Seleccionado", command=self.eliminar_pedido).pack(side="left", padx=5)
        
        # Actualizar combo de clientes
        self.actualizar_combo_clientes_pedidos()
    
    def setup_compra_tab(self):
        tab = self.tabview.tab("Panel de Compra")
        
        # Frame principal dividido en dos
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para selección de cliente y menú
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Selección de cliente
        cliente_frame = ctk.CTkFrame(left_frame)
        cliente_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(cliente_frame, text="Cliente:").pack(side="left", padx=5)
        self.compra_cliente_combo = ctk.CTkComboBox(cliente_frame, state="readonly")
        self.compra_cliente_combo.pack(side="left", padx=5, expand=True, fill="x")
        
        # Selección de menú
        menu_frame = ctk.CTkFrame(left_frame)
        menu_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(menu_frame, text="Menú:").pack(side="left", padx=5)
        self.compra_menu_combo = ctk.CTkComboBox(menu_frame, state="readonly")
        self.compra_menu_combo.pack(side="left", padx=5, expand=True, fill="x")
        
        ctk.CTkLabel(menu_frame, text="Cantidad:").pack(side="left", padx=5)
        self.compra_cantidad = ctk.CTkEntry(menu_frame, width=60)
        self.compra_cantidad.pack(side="left", padx=5)
        self.compra_cantidad.insert(0, "1")
        
        ctk.CTkButton(menu_frame, text="Agregar", command=self.agregar_a_carrito).pack(side="left", padx=5)
        
        # Detalles del menú seleccionado
        detalles_frame = ctk.CTkFrame(left_frame)
        detalles_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(detalles_frame, text="Detalles del Menú").pack()
        
        self.menu_detalles_text = ctk.CTkTextbox(detalles_frame, state="disabled")
        self.menu_detalles_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar evento de selección de menú
        self.compra_menu_combo.bind("<<ComboboxSelected>>", self.mostrar_detalles_menu)
        
        # Frame para el carrito de compra
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(right_frame, text="Carrito de Compra").pack()
        
        # Treeview para el carrito
        self.carrito_tree = ttk.Treeview(right_frame, columns=("Menú", "Cantidad", "Precio Unitario", "Subtotal"), show="headings")
        self.carrito_tree.heading("Menú", text="Menú")
        self.carrito_tree.heading("Cantidad", text="Cantidad")
        self.carrito_tree.heading("Precio Unitario", text="Precio Unitario")
        self.carrito_tree.heading("Subtotal", text="Subtotal")
        
        self.carrito_tree.column("Menú", width=150)
        self.carrito_tree.column("Cantidad", width=80)
        self.carrito_tree.column("Precio Unitario", width=120)
        self.carrito_tree.column("Subtotal", width=120)
        
        self.carrito_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para total y botones
        total_frame = ctk.CTkFrame(right_frame)
        total_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(total_frame, text="Total:").pack(side="left", padx=5)
        self.compra_total = ctk.CTkLabel(total_frame, text="$0.00", font=("Arial", 14, "bold"))
        self.compra_total.pack(side="left", padx=5)
        
        button_frame = ctk.CTkFrame(right_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(button_frame, text="Eliminar del Carrito", command=self.eliminar_del_carrito).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Limpiar Carrito", command=self.limpiar_carrito).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Realizar Pedido", command=self.realizar_pedido).pack(side="right", padx=5)
        
        # Inicializar carrito
        self.carrito = []
        
        # Actualizar combos
        self.actualizar_combo_clientes_compra()
        self.actualizar_combo_menus_compra()
    
    def setup_estadisticas_tab(self):
        tab = self.tabview.tab("Estadísticas")
        
        # Frame para controles
        control_frame = ctk.CTkFrame(tab)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(control_frame, text="Tipo de Gráfico:").pack(side="left", padx=5)
        self.grafico_tipo = ctk.CTkComboBox(control_frame, values=[
            "Ventas por Fecha", 
            "Menús Populares", 
            "Uso de Ingredientes"
        ])
        self.grafico_tipo.pack(side="left", padx=5)
        self.grafico_tipo.set("Ventas por Fecha")
        
        # Opciones adicionales para ventas por fecha
        self.grafico_opciones_frame = ctk.CTkFrame(control_frame)
        self.grafico_opciones_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.grafico_opciones_frame, text="Período:").pack(side="left", padx=5)
        self.grafico_periodo = ctk.CTkComboBox(self.grafico_opciones_frame, values=[
            "diario", "semanal", "mensual", "anual"
        ])
        self.grafico_periodo.pack(side="left", padx=5)
        self.grafico_periodo.set("diario")
        
        ctk.CTkButton(control_frame, text="Generar Gráfico", command=self.generar_grafico).pack(side="left", padx=5)
        
        # Frame para el gráfico
        self.grafico_frame = ctk.CTkFrame(tab)
        self.grafico_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar evento de cambio de tipo de gráfico
        self.grafico_tipo.bind("<<ComboboxSelected>>", self.actualizar_opciones_grafico)
        self.actualizar_opciones_grafico()
    
    # ========== Métodos para la pestaña de Ingredientes ==========
    
    def cargar_ingredientes(self):
        # Limpiar treeview
        for item in self.ing_tree.get_children():
            self.ing_tree.delete(item)
        
        # Obtener ingredientes de la base de datos
        ingredientes = listar_ingredientes(self.session)
        
        # Agregar al treeview
        for ingrediente in ingredientes:
            self.ing_tree.insert("", "end", values=(
                ingrediente.id,
                ingrediente.nombre,
                ingrediente.tipo,
                f"{ingrediente.cantidad}",
                ingrediente.unidad_medida
            ))
    
    def limpiar_formulario_ingrediente(self):
        self.ing_nombre.delete(0, "end")
        self.ing_tipo.set("")
        self.ing_cantidad.delete(0, "end")
        self.ing_unidad.set("")
    
    def seleccionar_ingrediente(self, event):
        selected = self.ing_tree.focus()
        if not selected:
            return
        
        values = self.ing_tree.item(selected, "values")
        if not values:
            return
        
        self.limpiar_formulario_ingrediente()
        
        self.ing_nombre.insert(0, values[1])
        self.ing_tipo.set(values[2])
        self.ing_cantidad.insert(0, values[3])
        self.ing_unidad.set(values[4])
    
    def agregar_ingrediente(self):
        nombre = self.ing_nombre.get().strip()
        tipo = self.ing_tipo.get().strip()
        cantidad = self.ing_cantidad.get().strip()
        unidad = self.ing_unidad.get().strip()
        
        if not nombre or not tipo or not cantidad or not unidad:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                raise ValueError("La cantidad debe ser mayor que cero")
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido mayor que cero")
            return
        
        try:
            ingrediente = crear_ingrediente(
                self.session,
                nombre=nombre,
                tipo=tipo,
                cantidad=cantidad_float,
                unidad_medida=unidad
            )
            messagebox.showinfo("Éxito", f"Ingrediente '{ingrediente.nombre}' creado correctamente")
            self.cargar_ingredientes()
            self.limpiar_formulario_ingrediente()
            self.actualizar_combo_ingredientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el ingrediente: {str(e)}")
    
    def actualizar_ingrediente(self):
        selected = self.ing_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un ingrediente para actualizar")
            return
        
        ingrediente_id = self.ing_tree.item(selected, "values")[0]
        nombre = self.ing_nombre.get().strip()
        tipo = self.ing_tipo.get().strip()
        cantidad = self.ing_cantidad.get().strip()
        unidad = self.ing_unidad.get().strip()
        
        if not nombre or not tipo or not cantidad or not unidad:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                raise ValueError("La cantidad debe ser mayor que cero")
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido mayor que cero")
            return
        
        try:
            ingrediente = actualizar_ingrediente(
                self.session,
                ingrediente_id=int(ingrediente_id),
                nombre=nombre,
                tipo=tipo,
                cantidad=cantidad_float,
                unidad_medida=unidad
            )
            messagebox.showinfo("Éxito", f"Ingrediente '{ingrediente.nombre}' actualizado correctamente")
            self.cargar_ingredientes()
            self.limpiar_formulario_ingrediente()
            self.actualizar_combo_ingredientes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el ingrediente: {str(e)}")
    
    def eliminar_ingrediente(self):
        selected = self.ing_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un ingrediente para eliminar")
            return
        
        ingrediente_id = self.ing_tree.item(selected, "values")[0]
        nombre = self.ing_tree.item(selected, "values")[1]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el ingrediente '{nombre}'?"):
            try:
                if eliminar_ingrediente(self.session, int(ingrediente_id)):
                    messagebox.showinfo("Éxito", f"Ingrediente '{nombre}' eliminado correctamente")
                    self.cargar_ingredientes()
                    self.limpiar_formulario_ingrediente()
                    self.actualizar_combo_ingredientes()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el ingrediente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el ingrediente: {str(e)}")
    
    # ========== Métodos para la pestaña de Menús ==========
    
    def cargar_menus(self):
        # Limpiar treeview
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
        
        # Obtener menús de la base de datos
        menus = listar_menus(self.session)
        
        # Agregar al treeview
        for menu in menus:
            self.menu_tree.insert("", "end", values=(
                menu.id,
                menu.nombre,
                menu.descripcion,
                f"${menu.precio:.2f}"
            ))
    
    def limpiar_formulario_menu(self):
        self.menu_nombre.delete(0, "end")
        self.menu_descripcion.delete(0, "end")
        self.menu_precio.delete(0, "end")
        
        # Limpiar ingredientes del menú
        for item in self.menu_ing_tree.get_children():
            self.menu_ing_tree.delete(item)
    
    def seleccionar_menu(self, event):
        selected = self.menu_tree.focus()
        if not selected:
            return
        
        values = self.menu_tree.item(selected, "values")
        if not values:
            return
        
        self.limpiar_formulario_menu()
        
        self.menu_nombre.insert(0, values[1])
        self.menu_descripcion.insert(0, values[2])
        self.menu_precio.insert(0, values[3].replace("$", ""))
        
        # Cargar ingredientes del menú
        menu_id = int(values[0])
        ingredientes = obtener_ingredientes_menu(self.session, menu_id)
        
        for ing in ingredientes:
            self.menu_ing_tree.insert("", "end", values=(
                ing['id'],
                ing['nombre'],
                ing['cantidad'],
                ing['unidad_medida']
            ))
    
    def agregar_menu(self):
        nombre = self.menu_nombre.get().strip()
        descripcion = self.menu_descripcion.get().strip()
        precio = self.menu_precio.get().strip()
        
        if not nombre or not precio:
            messagebox.showerror("Error", "Nombre y precio son obligatorios")
            return
        
        try:
            precio_float = float(precio)
            if precio_float <= 0:
                raise ValueError("El precio debe ser mayor que cero")
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido mayor que cero")
            return
        
        # Obtener ingredientes del menú
        ingredientes = {}
        for item in self.menu_ing_tree.get_children():
            values = self.menu_ing_tree.item(item, "values")
            ingrediente_id = int(values[0])
            cantidad = float(values[2])
            ingredientes[ingrediente_id] = cantidad
        
        if not ingredientes:
            messagebox.showerror("Error", "Debe agregar al menos un ingrediente al menú")
            return
        
        try:
            menu = crear_menu(
                self.session,
                nombre=nombre,
                descripcion=descripcion,
                precio=precio_float,
                ingredientes=ingredientes
            )
            messagebox.showinfo("Éxito", f"Menú '{menu.nombre}' creado correctamente")
            self.cargar_menus()
            self.limpiar_formulario_menu()
            self.actualizar_combo_menus_compra()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el menú: {str(e)}")
    
    def actualizar_menu(self):
        selected = self.menu_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un menú para actualizar")
            return
        
        menu_id = self.menu_tree.item(selected, "values")[0]
        nombre = self.menu_nombre.get().strip()
        descripcion = self.menu_descripcion.get().strip()
        precio = self.menu_precio.get().strip()
        
        if not nombre or not precio:
            messagebox.showerror("Error", "Nombre y precio son obligatorios")
            return
        
        try:
            precio_float = float(precio)
            if precio_float <= 0:
                raise ValueError("El precio debe ser mayor que cero")
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número válido mayor que cero")
            return
        
        # Obtener ingredientes del menú
        ingredientes = {}
        for item in self.menu_ing_tree.get_children():
            values = self.menu_ing_tree.item(item, "values")
            ingrediente_id = int(values[0])
            cantidad = float(values[2])
            ingredientes[ingrediente_id] = cantidad
        
        if not ingredientes:
            messagebox.showerror("Error", "Debe agregar al menos un ingrediente al menú")
            return
        
        try:
            menu = actualizar_menu(
                self.session,
                menu_id=int(menu_id),
                nombre=nombre,
                descripcion=descripcion,
                precio=precio_float,
                ingredientes=ingredientes
            )
            messagebox.showinfo("Éxito", f"Menú '{menu.nombre}' actualizado correctamente")
            self.cargar_menus()
            self.limpiar_formulario_menu()
            self.actualizar_combo_menus_compra()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el menú: {str(e)}")
    
    def eliminar_menu(self):
        selected = self.menu_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un menú para eliminar")
            return
        
        menu_id = self.menu_tree.item(selected, "values")[0]
        nombre = self.menu_tree.item(selected, "values")[1]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el menú '{nombre}'?"):
            try:
                if eliminar_menu(self.session, int(menu_id)):
                    messagebox.showinfo("Éxito", f"Menú '{nombre}' eliminado correctamente")
                    self.cargar_menus()
                    self.limpiar_formulario_menu()
                    self.actualizar_combo_menus_compra()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el menú")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el menú: {str(e)}")
    
    def actualizar_combo_ingredientes(self):
        ingredientes = listar_ingredientes(self.session)
        opciones = [f"{ing.id}: {ing.nombre} ({ing.tipo})" for ing in ingredientes]
        self.menu_ing_combo.configure(values=opciones)
        if opciones:
            self.menu_ing_combo.set(opciones[0])
        else:
            self.menu_ing_combo.set("")
    
    def agregar_ingrediente_a_menu(self):
        seleccion = self.menu_ing_combo.get()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione un ingrediente")
            return
        
        cantidad = self.menu_ing_cantidad.get().strip()
        if not cantidad:
            messagebox.showerror("Error", "Ingrese una cantidad")
            return
        
        try:
            cantidad_float = float(cantidad)
            if cantidad_float <= 0:
                raise ValueError("La cantidad debe ser mayor que cero")
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número válido mayor que cero")
            return
        
        # Obtener ID del ingrediente
        ingrediente_id = int(seleccion.split(":")[0])
        
        # Verificar si el ingrediente ya está en el menú
        for item in self.menu_ing_tree.get_children():
            values = self.menu_ing_tree.item(item, "values")
            if int(values[0]) == ingrediente_id:
                messagebox.showerror("Error", "Este ingrediente ya está en el menú")
                return
        
        # Obtener información del ingrediente
        ingrediente = obtener_ingrediente(self.session, ingrediente_id)
        if not ingrediente:
            messagebox.showerror("Error", "Ingrediente no encontrado")
            return
        
        # Agregar al treeview
        self.menu_ing_tree.insert("", "end", values=(
            ingrediente.id,
            ingrediente.nombre,
            cantidad_float,
            ingrediente.unidad_medida
        ))
    
    def remover_ingrediente_de_menu(self):
        selected = self.menu_ing_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un ingrediente para remover")
            return
        
        self.menu_ing_tree.delete(selected)
    
    # ========== Métodos para la pestaña de Clientes ==========
    
    def cargar_clientes(self):
        # Limpiar treeview
        for item in self.cli_tree.get_children():
            self.cli_tree.delete(item)
        
        # Obtener clientes de la base de datos
        clientes = listar_clientes(self.session)
        
        # Agregar al treeview
        for cliente in clientes:
            self.cli_tree.insert("", "end", values=(
                cliente.id,
                cliente.nombre,
                cliente.email
            ))
    
    def limpiar_formulario_cliente(self):
        self.cli_nombre.delete(0, "end")
        self.cli_email.delete(0, "end")
    
    def seleccionar_cliente(self, event):
        selected = self.cli_tree.focus()
        if not selected:
            return
        
        values = self.cli_tree.item(selected, "values")
        if not values:
            return
        
        self.limpiar_formulario_cliente()
        
        self.cli_nombre.insert(0, values[1])
        self.cli_email.insert(0, values[2])
    
    def agregar_cliente(self):
        nombre = self.cli_nombre.get().strip()
        email = self.cli_email.get().strip()
        
        if not nombre or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            cliente = crear_cliente(
                self.session,
                nombre=nombre,
                email=email
            )
            messagebox.showinfo("Éxito", f"Cliente '{cliente.nombre}' creado correctamente")
            self.cargar_clientes()
            self.limpiar_formulario_cliente()
            self.actualizar_combo_clientes_pedidos()
            self.actualizar_combo_clientes_compra()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el cliente: {str(e)}")
    
    def actualizar_cliente(self):
        selected = self.cli_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un cliente para actualizar")
            return
        
        cliente_id = self.cli_tree.item(selected, "values")[0]
        nombre = self.cli_nombre.get().strip()
        email = self.cli_email.get().strip()
        
        if not nombre or not email:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        try:
            cliente = actualizar_cliente(
                self.session,
                cliente_id=int(cliente_id),
                nombre=nombre,
                email=email
            )
            messagebox.showinfo("Éxito", f"Cliente '{cliente.nombre}' actualizado correctamente")
            self.cargar_clientes()
            self.limpiar_formulario_cliente()
            self.actualizar_combo_clientes_pedidos()
            self.actualizar_combo_clientes_compra()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el cliente: {str(e)}")
    
    def eliminar_cliente(self):
        selected = self.cli_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un cliente para eliminar")
            return
        
        cliente_id = self.cli_tree.item(selected, "values")[0]
        nombre = self.cli_tree.item(selected, "values")[1]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el cliente '{nombre}'?"):
            try:
                if eliminar_cliente(self.session, int(cliente_id)):
                    messagebox.showinfo("Éxito", f"Cliente '{nombre}' eliminado correctamente")
                    self.cargar_clientes()
                    self.limpiar_formulario_cliente()
                    self.actualizar_combo_clientes_pedidos()
                    self.actualizar_combo_clientes_compra()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el cliente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el cliente: {str(e)}")
    
    # ========== Métodos para la pestaña de Pedidos ==========
    
    def cargar_pedidos(self, cliente_id=None):
        # Limpiar treeview
        for item in self.ped_tree.get_children():
            self.ped_tree.delete(item)
        
        # Obtener pedidos de la base de datos
        if cliente_id:
            pedidos = listar_pedidos_por_cliente(self.session, cliente_id)
        else:
            pedidos = listar_pedidos(self.session)
        
        # Agregar al treeview
        for pedido in pedidos:
            self.ped_tree.insert("", "end", values=(
                pedido.id,
                pedido.cliente.nombre,
                pedido.menu.nombre,
                pedido.cantidad,
                f"${pedido.total:.2f}",
                pedido.fecha.strftime("%Y-%m-%d %H:%M")
            ))
    
    def actualizar_combo_clientes_pedidos(self):
        clientes = listar_clientes(self.session)
        opciones = ["Todos"] + [f"{cli.id}: {cli.nombre}" for cli in clientes]
        self.pedido_cliente_filter.configure(values=opciones)
        self.pedido_cliente_filter.set("Todos")
    
    def filtrar_pedidos(self):
        seleccion = self.pedido_cliente_filter.get()
        if seleccion == "Todos":
            self.cargar_pedidos()
        else:
            cliente_id = int(seleccion.split(":")[0])
            self.cargar_pedidos(cliente_id)
    
    def mostrar_todos_pedidos(self):
        self.pedido_cliente_filter.set("Todos")
        self.cargar_pedidos()
    
    def eliminar_pedido(self):
        selected = self.ped_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un pedido para eliminar")
            return
        
        pedido_id = self.ped_tree.item(selected, "values")[0]
        cliente = self.ped_tree.item(selected, "values")[1]
        menu = self.ped_tree.item(selected, "values")[2]
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el pedido de {menu} para {cliente}?"):
            try:
                if eliminar_pedido(self.session, int(pedido_id)):
                    messagebox.showinfo("Éxito", "Pedido eliminado correctamente")
                    self.filtrar_pedidos()  # Mantener el filtro actual
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el pedido")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el pedido: {str(e)}")
    
    # ========== Métodos para la pestaña de Panel de Compra ==========
    
    def actualizar_combo_clientes_compra(self):
        clientes = listar_clientes(self.session)
        opciones = [f"{cli.id}: {cli.nombre}" for cli in clientes]
        self.compra_cliente_combo.configure(values=opciones)
        if opciones:
            self.compra_cliente_combo.set(opciones[0])
        else:
            self.compra_cliente_combo.set("")
    
    def actualizar_combo_menus_compra(self):
        menus = listar_menus(self.session)
        opciones = [f"{menu.id}: {menu.nombre} (${menu.precio:.2f})" for menu in menus]
        self.compra_menu_combo.configure(values=opciones)
        if opciones:
            self.compra_menu_combo.set(opciones[0])
        else:
            self.compra_menu_combo.set("")
    
    def mostrar_detalles_menu(self, event=None):
        seleccion = self.compra_menu_combo.get()
        if not seleccion:
            return
        
        menu_id = int(seleccion.split(":")[0])
        menu = obtener_menu(self.session, menu_id)
        if not menu:
            return
        
        ingredientes = obtener_ingredientes_menu(self.session, menu_id)
        
        detalles = f"Nombre: {menu.nombre}\n"
        detalles += f"Descripción: {menu.descripcion}\n"
        detalles += f"Precio: ${menu.precio:.2f}\n\n"
        detalles += "Ingredientes:\n"
        
        for ing in ingredientes:
            detalles += f"- {ing['nombre']}: {ing['cantidad']} {ing['unidad_medida']}\n"
        
        self.menu_detalles_text.configure(state="normal")
        self.menu_detalles_text.delete("1.0", "end")
        self.menu_detalles_text.insert("1.0", detalles)
        self.menu_detalles_text.configure(state="disabled")
    
    def agregar_a_carrito(self):
        seleccion_menu = self.compra_menu_combo.get()
        if not seleccion_menu:
            messagebox.showerror("Error", "Seleccione un menú")
            return
        
        cantidad = self.compra_cantidad.get().strip()
        if not cantidad:
            messagebox.showerror("Error", "Ingrese una cantidad")
            return
        
        try:
            cantidad_int = int(cantidad)
            if cantidad_int <= 0:
                raise ValueError("La cantidad debe ser mayor que cero")
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero válido mayor que cero")
            return
        
        # Obtener información del menú
        menu_id = int(seleccion_menu.split(":")[0])
        menu = obtener_menu(self.session, menu_id)
        if not menu:
            messagebox.showerror("Error", "Menú no encontrado")
            return
        
        # Agregar al carrito
        self.carrito.append({
            "menu_id": menu.id,
            "nombre": menu.nombre,
            "precio": menu.precio,
            "cantidad": cantidad_int,
            "subtotal": menu.precio * cantidad_int
        })
        
        # Actualizar treeview del carrito
        self.actualizar_carrito()
    
    def actualizar_carrito(self):
        # Limpiar treeview
        for item in self.carrito_tree.get_children():
            self.carrito_tree.delete(item)
        
        # Agregar items del carrito
        total = 0.0
        for item in self.carrito:
            self.carrito_tree.insert("", "end", values=(
                item["nombre"],
                item["cantidad"],
                f"${item['precio']:.2f}",
                f"${item['subtotal']:.2f}"
            ))
            total += item["subtotal"]
        
        # Actualizar total
        self.compra_total.configure(text=f"${total:.2f}")
    
    def eliminar_del_carrito(self):
        selected = self.carrito_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Seleccione un item para eliminar")
            return
        
        index = int(self.carrito_tree.index(selected))
        if 0 <= index < len(self.carrito):
            del self.carrito[index]
            self.actualizar_carrito()
    
    def limpiar_carrito(self):
        self.carrito = []
        self.actualizar_carrito()
    
    def realizar_pedido(self):
        seleccion_cliente = self.compra_cliente_combo.get()
        if not seleccion_cliente:
            messagebox.showerror("Error", "Seleccione un cliente")
            return
        
        if not self.carrito:
            messagebox.showerror("Error", "El carrito está vacío")
            return
        
        cliente_id = int(seleccion_cliente.split(":")[0])
        
        try:
            # Crear un pedido por cada item en el carrito
            for item in self.carrito:
                crear_pedido(
                    self.session,
                    cliente_id=cliente_id,
                    menu_id=item["menu_id"],
                    cantidad=item["cantidad"],
                    descripcion=f"{item['cantidad']} x {item['nombre']}"
                )
            
            messagebox.showinfo("Éxito", "Pedido realizado correctamente")
            self.limpiar_carrito()
            self.cargar_pedidos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar el pedido: {str(e)}")
    
    # ========== Métodos para la pestaña de Estadísticas ==========
    
    def actualizar_opciones_grafico(self, event=None):
        tipo = self.grafico_tipo.get()
        if tipo == "Ventas por Fecha":
            self.grafico_opciones_frame.pack(side="left", padx=5)
        else:
            self.grafico_opciones_frame.pack_forget()
    
    def generar_grafico(self):
        # Limpiar frame del gráfico
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()
        
        tipo = self.grafico_tipo.get()
        
        try:
            if tipo == "Ventas por Fecha":
                periodo = self.grafico_periodo.get()
                grafico = GraficoFactory.crear_grafico("ventas_fecha", self.session, periodo=periodo)
            elif tipo == "Menús Populares":
                grafico = GraficoFactory.crear_grafico("menus_populares", self.session)
            elif tipo == "Uso de Ingredientes":
                grafico = GraficoFactory.crear_grafico("uso_ingredientes", self.session)
            else:
                messagebox.showerror("Error", "Tipo de gráfico no válido")
                return
            
            grafico.generar()
            figura = grafico.obtener_figura()
            
            # Integrar el gráfico en la interfaz
            canvas = FigureCanvasTkAgg(figura, master=self.grafico_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
            # Ajustar diseño
            plt.tight_layout()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el gráfico: {str(e)}")

# Script para inicializar la aplicación
if __name__ == "__main__":
    app = RestauranteApp()
    app.mainloop()
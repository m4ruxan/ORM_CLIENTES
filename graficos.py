import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy.orm import Session
from models import Pedido, Menu
from datetime import datetime, timedelta
from typing import List, Dict
import numpy as np

class GraficoFactory:
    @staticmethod
    def crear_grafico(tipo: str, session: Session, **kwargs):
        if tipo == "ventas_fecha":
            return GraficoVentasPorFecha(session, **kwargs)
        elif tipo == "menus_populares":
            return GraficoMenusPopulares(session, **kwargs)
        elif tipo == "uso_ingredientes":
            return GraficoUsoIngredientes(session, **kwargs)
        else:
            raise ValueError(f"Tipo de gráfico no válido: {tipo}")

class GraficoBase:
    def __init__(self, session: Session):
        self.session = session
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
    
    def generar(self):
        raise NotImplementedError("Método 'generar' debe ser implementado por subclases")
    
    def obtener_figura(self):
        return self.fig

class GraficoVentasPorFecha(GraficoBase):
    def __init__(self, session: Session, periodo: str = 'diario'):
        super().__init__(session)
        self.periodo = periodo
    
    def generar(self):
        pedidos = self.session.query(Pedido).order_by(Pedido.fecha).all()
        
        if not pedidos:
            self.ax.text(0.5, 0.5, 'No hay datos de pedidos', ha='center', va='center')
            self.ax.set_title('Ventas por Fecha - Sin Datos')
            return
        
        fechas = [p.fecha for p in pedidos]
        montos = [p.total for p in pedidos]
        
        if self.periodo == 'diario':
            fechas_str = [fecha.strftime('%Y-%m-%d') for fecha in fechas]
            self.ax.bar(fechas_str, montos)
            self.ax.set_title('Ventas Diarias')
            self.ax.set_xlabel('Fecha')
            self.ax.set_ylabel('Total Ventas ($)')
            plt.xticks(rotation=45)
        
        elif self.periodo == 'semanal':
            # Agrupar por semana
            semanas = {}
            for fecha, monto in zip(fechas, montos):
                semana = fecha.strftime('%Y-%U')
                if semana not in semanas:
                    semanas[semana] = 0.0
                semanas[semana] += monto
            
            semanas_ordenadas = sorted(semanas.items())
            self.ax.bar([s[0] for s in semanas_ordenadas], [s[1] for s in semanas_ordenadas])
            self.ax.set_title('Ventas Semanales')
            self.ax.set_xlabel('Semana (Año-Número)')
            self.ax.set_ylabel('Total Ventas ($)')
            plt.xticks(rotation=45)
        
        elif self.periodo == 'mensual':
            # Agrupar por mes
            meses = {}
            for fecha, monto in zip(fechas, montos):
                mes = fecha.strftime('%Y-%m')
                if mes not in meses:
                    meses[mes] = 0.0
                meses[mes] += monto
            
            meses_ordenados = sorted(meses.items())
            self.ax.bar([m[0] for m in meses_ordenados], [m[1] for m in meses_ordenados])
            self.ax.set_title('Ventas Mensuales')
            self.ax.set_xlabel('Mes')
            self.ax.set_ylabel('Total Ventas ($)')
            plt.xticks(rotation=45)
        
        elif self.periodo == 'anual':
            # Agrupar por año
            años = {}
            for fecha, monto in zip(fechas, montos):
                año = fecha.strftime('%Y')
                if año not in años:
                    años[año] = 0.0
                años[año] += monto
            
            años_ordenados = sorted(años.items())
            self.ax.bar([a[0] for a in años_ordenados], [a[1] for a in años_ordenados])
            self.ax.set_title('Ventas Anuales')
            self.ax.set_xlabel('Año')
            self.ax.set_ylabel('Total Ventas ($)')
        
        else:
            raise ValueError(f"Período no válido: {self.periodo}")

class GraficoMenusPopulares(GraficoBase):
    def generar(self):
        # Obtener todos los menús con la cantidad de pedidos
        menus = self.session.query(Menu).all()
        if not menus:
            self.ax.text(0.5, 0.5, 'No hay menús registrados', ha='center', va='center')
            self.ax.set_title('Menús Populares - Sin Datos')
            return
        
        menu_data = []
        for menu in menus:
            cantidad_pedidos = self.session.query(Pedido).filter_by(menu_id=menu.id).count()
            menu_data.append((menu.nombre, cantidad_pedidos))
        
        # Ordenar por cantidad de pedidos
        menu_data.sort(key=lambda x: x[1], reverse=True)
        
        nombres = [m[0] for m in menu_data]
        cantidades = [m[1] for m in menu_data]
        
        self.ax.barh(nombres, cantidades)
        self.ax.set_title('Menús Más Comprados')
        self.ax.set_xlabel('Cantidad de Pedidos')
        self.ax.set_ylabel('Menú')
        
        # Ajustar diseño para nombres largos
        plt.tight_layout()

class GraficoUsoIngredientes(GraficoBase):
    def generar(self):
        from models import Ingrediente, menu_ingrediente, Pedido
        
        # Obtener todos los ingredientes
        ingredientes = self.session.query(Ingrediente).all()
        if not ingredientes:
            self.ax.text(0.5, 0.5, 'No hay ingredientes registrados', ha='center', va='center')
            self.ax.set_title('Uso de Ingredientes - Sin Datos')
            return
        
        # Calcular el uso total de cada ingrediente
        uso_ingredientes = {}
        for ingrediente in ingredientes:
            # Obtener todos los menús que usan este ingrediente
            menus_con_ingrediente = self.session.query(Menu).join(
                menu_ingrediente, Menu.id == menu_ingrediente.c.menu_id
            ).filter(menu_ingrediente.c.ingrediente_id == ingrediente.id).all()
            
            total_uso = 0.0
            for menu in menus_con_ingrediente:
                # Obtener cantidad de este ingrediente en el menú
                stmt = menu_ingrediente.select().where(
                    (menu_ingrediente.c.menu_id == menu.id) & 
                    (menu_ingrediente.c.ingrediente_id == ingrediente.id)
                )
                result = self.session.execute(stmt).first()
                cantidad_por_menu = result.cantidad if result else 0.0
                
                # Obtener cantidad de pedidos de este menú
                cantidad_pedidos = self.session.query(Pedido).filter_by(menu_id=menu.id).count()
                
                total_uso += cantidad_por_menu * cantidad_pedidos
            
            uso_ingredientes[ingrediente.nombre] = total_uso
        
        # Ordenar ingredientes por uso
        ingredientes_ordenados = sorted(uso_ingredientes.items(), key=lambda x: x[1], reverse=True)
        nombres = [i[0] for i in ingredientes_ordenados]
        usos = [i[1] for i in ingredientes_ordenados]
        
        # Crear gráfico de torta
        self.ax.pie(usos, labels=nombres, autopct='%1.1f%%', startangle=90)
        self.ax.set_title('Distribución de Uso de Ingredientes')
        self.ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
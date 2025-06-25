from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# Tabla de asociación para Menú-Ingredientes
menu_ingrediente = Table(
    'menu_ingrediente', 
    Base.metadata,
    Column('menu_id', Integer, ForeignKey('menus.id')),
    Column('ingrediente_id', Integer, ForeignKey('ingredientes.id')),
    Column('cantidad', Float)
)

class Ingrediente(Base):
    __tablename__ = 'ingredientes'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    tipo = Column(String(50), nullable=False)
    cantidad = Column(Float, nullable=False)
    unidad_medida = Column(String(20), nullable=False)
    
    menus = relationship('Menu', secondary=menu_ingrediente, back_populates='ingredientes')
    
    def __repr__(self):
        return f"Ingrediente(nombre='{self.nombre}', tipo='{self.tipo}')"

class Menu(Base):
    __tablename__ = 'menus'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(String(255))
    precio = Column(Float, nullable=False)
    
    ingredientes = relationship('Ingrediente', secondary=menu_ingrediente, back_populates='menus')
    pedidos = relationship('Pedido', back_populates='menu')
    
    def __repr__(self):
        return f"Menu(nombre='{self.nombre}', precio={self.precio})"

class Cliente(Base):
    __tablename__ = 'clientes'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    pedidos = relationship('Pedido', back_populates='cliente')
    
    def __repr__(self):
        return f"Cliente(nombre='{self.nombre}', email='{self.email}')"

class Pedido(Base):
    __tablename__ = 'pedidos'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(255))
    total = Column(Float, nullable=False)
    fecha = Column(Date, default=datetime.now)
    cantidad = Column(Integer, nullable=False)
    
    cliente_id = Column(Integer, ForeignKey('clientes.id'))
    menu_id = Column(Integer, ForeignKey('menus.id'))
    
    cliente = relationship('Cliente', back_populates='pedidos')
    menu = relationship('Menu', back_populates='pedidos')
    
    def __repr__(self):
        return f"Pedido(total={self.total}, fecha='{self.fecha}')"
from sqlalchemy.orm import Session
from models import Menu, Ingrediente, menu_ingrediente  # Importa menu_ingrediente desde models
from typing import List, Optional, Dict


def crear_menu(
    session: Session, 
    nombre: str, 
    descripcion: str, 
    precio: float, 
    ingredientes: Dict[int, float]
) -> Menu:
    # Verificar si el menú ya existe
    existente = session.query(Menu).filter_by(nombre=nombre).first()
    if existente:
        raise ValueError(f"Ya existe un menú con el nombre '{nombre}'")
    
    # Verificar que todos los ingredientes existan
    ingredientes_obj = []
    for ingrediente_id, cantidad in ingredientes.items():
        ingrediente = session.query(Ingrediente).filter_by(id=ingrediente_id).first()
        if not ingrediente:
            raise ValueError(f"No se encontró el ingrediente con ID {ingrediente_id}")
        ingredientes_obj.append((ingrediente, cantidad))
    
    menu = Menu(nombre=nombre, descripcion=descripcion, precio=precio)
    session.add(menu)
    session.commit()
    
    # Asociar ingredientes al menú
    for ingrediente, cantidad in ingredientes_obj:
        menu.ingredientes.append(ingrediente)
        # Actualizar la cantidad en la tabla de asociación
        stmt = menu_ingrediente.update().where(
            (menu_ingrediente.c.menu_id == menu.id) & 
            (menu_ingrediente.c.ingrediente_id == ingrediente.id)
        ).values(cantidad=cantidad)
        session.execute(stmt)
    
    session.commit()
    return menu

def obtener_menu(session: Session, menu_id: int) -> Optional[Menu]:
    return session.query(Menu).filter_by(id=menu_id).first()

def listar_menus(session: Session) -> List[Menu]:
    return session.query(Menu).all()

def actualizar_menu(
    session: Session, 
    menu_id: int, 
    nombre: str = None, 
    descripcion: str = None, 
    precio: float = None, 
    ingredientes: Dict[int, float] = None
) -> Menu:
    menu = obtener_menu(session, menu_id)
    if not menu:
        raise ValueError(f"No se encontró el menú con ID {menu_id}")
    
    if nombre is not None:
        # Verificar si el nuevo nombre ya existe
        if nombre != menu.nombre and session.query(Menu).filter_by(nombre=nombre).first():
            raise ValueError(f"Ya existe un menú con el nombre '{nombre}'")
        menu.nombre = nombre
    
    if descripcion is not None:
        menu.descripcion = descripcion
    if precio is not None:
        menu.precio = precio
    
    if ingredientes is not None:
        # Actualizar ingredientes
        menu.ingredientes.clear()
        for ingrediente_id, cantidad in ingredientes.items():
            ingrediente = session.query(Ingrediente).filter_by(id=ingrediente_id).first()
            if not ingrediente:
                raise ValueError(f"No se encontró el ingrediente con ID {ingrediente_id}")
            menu.ingredientes.append(ingrediente)
            # Actualizar la cantidad en la tabla de asociación
            stmt = menu_ingrediente.update().where(
                (menu_ingrediente.c.menu_id == menu.id) & 
                (menu_ingrediente.c.ingrediente_id == ingrediente.id)
            ).values(cantidad=cantidad)
            session.execute(stmt)
    
    session.commit()
    return menu

def eliminar_menu(session: Session, menu_id: int) -> bool:
    menu = obtener_menu(session, menu_id)
    if not menu:
        return False
    
    session.delete(menu)
    session.commit()
    return True

def obtener_ingredientes_menu(session: Session, menu_id: int) -> List[Dict]:
    menu = obtener_menu(session, menu_id)
    if not menu:
        return []
    
    ingredientes = []
    for ingrediente in menu.ingredientes:
        stmt = menu_ingrediente.select().where(
            (menu_ingrediente.c.menu_id == menu.id) & 
            (menu_ingrediente.c.ingrediente_id == ingrediente.id)
        )
        result = session.execute(stmt).first()
        cantidad = result.cantidad if result else 0.0
        
        ingredientes.append({
            'id': ingrediente.id,
            'nombre': ingrediente.nombre,
            'tipo': ingrediente.tipo,
            'cantidad': cantidad,
            'unidad_medida': ingrediente.unidad_medida
        })
    
    return ingredientes
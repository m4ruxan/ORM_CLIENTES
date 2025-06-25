from sqlalchemy.orm import Session
from models import Ingrediente
from typing import List, Optional

def crear_ingrediente(session: Session, nombre: str, tipo: str, cantidad: float, unidad_medida: str) -> Ingrediente:
    # Verificar si el ingrediente ya existe
    existente = session.query(Ingrediente).filter_by(nombre=nombre).first()
    if existente:
        raise ValueError(f"Ya existe un ingrediente con el nombre '{nombre}'")
    
    ingrediente = Ingrediente(
        nombre=nombre,
        tipo=tipo,
        cantidad=cantidad,
        unidad_medida=unidad_medida
    )
    session.add(ingrediente)
    session.commit()
    return ingrediente

def obtener_ingrediente(session: Session, ingrediente_id: int) -> Optional[Ingrediente]:
    return session.query(Ingrediente).filter_by(id=ingrediente_id).first()

def listar_ingredientes(session: Session) -> List[Ingrediente]:
    return session.query(Ingrediente).all()

def actualizar_ingrediente(
    session: Session, 
    ingrediente_id: int, 
    nombre: str = None, 
    tipo: str = None, 
    cantidad: float = None, 
    unidad_medida: str = None
) -> Ingrediente:
    ingrediente = obtener_ingrediente(session, ingrediente_id)
    if not ingrediente:
        raise ValueError(f"No se encontró el ingrediente con ID {ingrediente_id}")
    
    if nombre is not None:
        # Verificar si el nuevo nombre ya existe
        if nombre != ingrediente.nombre and session.query(Ingrediente).filter_by(nombre=nombre).first():
            raise ValueError(f"Ya existe un ingrediente con el nombre '{nombre}'")
        ingrediente.nombre = nombre
    
    if tipo is not None:
        ingrediente.tipo = tipo
    if cantidad is not None:
        ingrediente.cantidad = cantidad
    if unidad_medida is not None:
        ingrediente.unidad_medida = unidad_medida
    
    session.commit()
    return ingrediente

def eliminar_ingrediente(session: Session, ingrediente_id: int) -> bool:
    ingrediente = obtener_ingrediente(session, ingrediente_id)
    if not ingrediente:
        return False
    
    session.delete(ingrediente)
    session.commit()
    return True
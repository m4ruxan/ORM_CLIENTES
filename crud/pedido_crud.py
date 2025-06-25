from sqlalchemy.orm import Session
from models import Pedido
from datetime import datetime
from typing import List, Optional

def crear_pedido(
    session: Session, 
    cliente_id: int, 
    menu_id: int, 
    cantidad: int, 
    descripcion: str = None
) -> Pedido:
    from models import Cliente, Menu  # Importación local para evitar circularidad
    
    cliente = session.query(Cliente).filter_by(id=cliente_id).first()
    if not cliente:
        raise ValueError(f"No se encontró el cliente con ID {cliente_id}")
    
    menu = session.query(Menu).filter_by(id=menu_id).first()
    if not menu:
        raise ValueError(f"No se encontró el menú con ID {menu_id}")
    
    total = menu.precio * cantidad
    
    pedido = Pedido(
        descripcion=descripcion or f"{cantidad} x {menu.nombre}",
        total=total,
        cantidad=cantidad,
        cliente_id=cliente_id,
        menu_id=menu_id
    )
    
    session.add(pedido)
    session.commit()
    return pedido

def obtener_pedido(session: Session, pedido_id: int) -> Optional[Pedido]:
    return session.query(Pedido).filter_by(id=pedido_id).first()

def listar_pedidos(session: Session) -> List[Pedido]:
    return session.query(Pedido).order_by(Pedido.fecha.desc()).all()

def listar_pedidos_por_cliente(session: Session, cliente_id: int) -> List[Pedido]:
    return session.query(Pedido).filter_by(cliente_id=cliente_id).order_by(Pedido.fecha.desc()).all()

def eliminar_pedido(session: Session, pedido_id: int) -> bool:
    pedido = obtener_pedido(session, pedido_id)
    if not pedido:
        return False
    
    session.delete(pedido)
    session.commit()
    return True
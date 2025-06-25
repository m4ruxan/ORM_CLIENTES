from sqlalchemy.orm import Session
from models import Cliente
from typing import List, Optional

def crear_cliente(session: Session, nombre: str, email: str) -> Cliente:
    # Verificar si el cliente ya existe
    existente = session.query(Cliente).filter_by(email=email).first()
    if existente:
        raise ValueError(f"Ya existe un cliente con el email '{email}'")
    
    cliente = Cliente(nombre=nombre, email=email)
    session.add(cliente)
    session.commit()
    return cliente

def obtener_cliente(session: Session, cliente_id: int) -> Optional[Cliente]:
    return session.query(Cliente).filter_by(id=cliente_id).first()

def listar_clientes(session: Session) -> List[Cliente]:
    return session.query(Cliente).all()

def actualizar_cliente(
    session: Session, 
    cliente_id: int, 
    nombre: str = None, 
    email: str = None
) -> Cliente:
    cliente = obtener_cliente(session, cliente_id)
    if not cliente:
        raise ValueError(f"No se encontró el cliente con ID {cliente_id}")
    
    if nombre is not None:
        cliente.nombre = nombre
    
    if email is not None:
        # Verificar si el nuevo email ya existe
        if email != cliente.email and session.query(Cliente).filter_by(email=email).first():
            raise ValueError(f"Ya existe un cliente con el email '{email}'")
        cliente.email = email
    
    session.commit()
    return cliente

def eliminar_cliente(session: Session, cliente_id: int) -> bool:
    cliente = obtener_cliente(session, cliente_id)
    if not cliente:
        return False
    
    session.delete(cliente)
    session.commit()
    return True
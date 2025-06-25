from database import init_db

def main():
    print("Inicializando base de datos...")
    engine = init_db()
    print("Base de datos creada exitosamente en 'restaurante.db'")

if __name__ == "__main__":
    main()
# README para Migraciones con Alembic

Este proyecto ya cuenta con el entorno de **Alembic** configurado para trabajar de forma asíncrona con *SQLAlchemy* y *PostgreSQL*.

Al realizar cualquier cambio en los modelos dentro de `app/models/`, debes seguir estos pasos para actualizar tu base de datos y mantener el historial de cambios (migraciones).

## 1. Generar la migración automáticamente

Usa el siguiente comando cuando hayas editado algún de modelo de base de datos o hayas bajado el proyecto por primera vez y desees generar el SQL de creación formal:

```bash
alembic revision --autogenerate -m "Descripción de los cambios, ej: init_tablas"
```

Esto generará automáticamente un script bajo la carpeta `alembic/versions/`.

## 2. Aplicar la migración a la base de datos

Dile a PostgreSQL que ejecute esos archivos:

```bash
alembic upgrade head
```

¡Listo! Tu base de datos tiene ahora la estructura más reciente.

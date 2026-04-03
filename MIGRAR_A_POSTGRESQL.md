# Migracion de SQLite a PostgreSQL (Django)

Este proyecto ya usa PostgreSQL en `web_project/settings.py`.

## 1) Pre requisitos

- PostgreSQL instalado y en ejecucion.
- Base de datos creada (ejemplo: `marisqueria_db`).
- Usuario con permisos sobre esa base de datos.
- Dependencias instaladas:

```bash
pip install -r requirements.txt
```

## 2) Configurar variables de entorno

Crea un archivo `.env` en la raiz del proyecto con este formato:

```env
DB_NAME=marisqueria_db
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

## 3) Exportar datos desde SQLite actual

Genera un respaldo JSON desde SQLite usando el settings auxiliar:

```bash
python manage.py dumpdata --settings=web_project.settings_sqlite --exclude contenttypes --exclude auth.permission --indent 2 > respaldo_sqlite.json
```

## 4) Crear estructura en PostgreSQL

Con el `.env` configurado, aplica migraciones en PostgreSQL:

```bash
python manage.py migrate
```

## 5) Importar datos en PostgreSQL

```bash
python manage.py loaddata respaldo_sqlite.json
```

## 6) Verificacion

```bash
python manage.py check
python manage.py createsuperuser
python manage.py runserver
```

## Notas

- El archivo `web_project/settings_sqlite.py` es solo para exportacion temporal desde `db.sqlite3`.
- Si ya no necesitas SQLite, puedes conservar `db.sqlite3` solo como respaldo historico.

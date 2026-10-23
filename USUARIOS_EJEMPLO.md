# Usuarios de ejemplo

Se crearon estos usuarios de prueba en la base de datos local del proyecto:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `AdminPass123!` | `administrator` |
| `requester` | `RequesterPass123!` | `requester` |
| `root` | `RootPass123!` | `administrator` (superusuario) |

## Comandos para recrear los roles

```bash
cd /media/disk/Dev/SistemaGestionReservasAcademico
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python - <<'PY'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.contrib.auth import get_user_model

User = get_user_model()

users = [
    ('admin', 'AdminPass123!', 'administrator'),
    ('requester', 'RequesterPass123!', 'requester'),
]

for username, password, role in users:
    user, _ = User.objects.get_or_create(username=username, defaults={'role': role})
    user.set_password(password)
    user.role = role
    user.save()

root, _ = User.objects.get_or_create(username='root', defaults={'email': 'root@example.com'})
root.set_password('RootPass123!')
root.role = 'administrator'
root.is_staff = True
root.is_superuser = True
root.save()
PY
```

## Notas

- `admin` y `root` tienen permisos de administrador.
- `requester` es un usuario normal para pruebas de solicitud de reservas.
- Para desarrollo local, se recomienda usar un archivo `.env` basado en `.example.env`.

# Sistema de Gestión de Reservas de Espacios Académicos

Aplicación monolítica Django para gestionar espacios académicos y sus reservas. Usa Django REST Framework para la API, SQLite para desarrollo local y sesiones para autenticación. El estado actual del desarrollo se describe en [PLAN_INGENIERIA.md](./PLAN_INGENIERIA.md) y las reglas funcionales en [OpenSpec](./openspec/changes/define-reservas-espacios-academicos/).

## Requisitos

- Python 3.12
- Git

## Instalación y ejecución local

Desde la raíz del repositorio:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

El servidor de desarrollo escucha en <http://127.0.0.1:8000/> y el administrador Django está en <http://127.0.0.1:8000/admin/>. `createsuperuser` crea la cuenta inicial con rol de administrador. Las migraciones crean la base SQLite local (`db.sqlite3`), que no se debe subir al repositorio.

En Windows, activa el entorno con `.venv\Scripts\Activate.ps1` y ejecuta los mismos comandos Python desde PowerShell.

## Autenticación de la API

La API usa sesiones Django. Antes de iniciar sesión, solicita un token CSRF; conserva la cookie recibida y envía el token en `X-CSRFToken` al hacer `POST`:

1. `GET /api/auth/csrf/` devuelve `csrfToken` y establece la cookie CSRF.
2. `POST /api/auth/login/` acepta `username` y `password`, conserva la cookie de sesión y devuelve el rol del usuario.
3. `POST /api/auth/logout/` cierra la sesión autenticada.

La administración de cuentas está disponible en `/api/users/` y requiere rol de administrador. Las contraseñas solo se aceptan al crear o cambiar una cuenta y nunca se devuelven en las respuestas. El registro público no está habilitado.

## Espacios

La API de espacios está disponible en `/api/spaces/`. Un solicitante autenticado puede listar los espacios activos y consultar sus detalles; solo un administrador puede crear, editar o desactivar espacios. Los campos son `name`, `space_type`, `capacity` (entero mayor que cero) e `is_active`. `DELETE` desactiva el espacio en lugar de eliminarlo, para conservar referencias históricas.

## Solicitudes y disponibilidad

- `GET /api/spaces/{id}/availability/?start_at=<fecha>&end_at=<fecha>` consulta si el espacio acepta el intervalo.
- `POST /api/reservations/` recibe `space`, `purpose`, `start_at` y `end_at`; el propietario se toma de la sesión, no del cuerpo de la solicitud.
- `GET /api/reservations/` y `GET /api/reservations/{id}/` muestran las solicitudes propias; un administrador puede consultar todas.

Las fechas usan valores con zona horaria y los intervalos son semiabiertos `[inicio, fin)`: un intervalo que termina justo cuando empieza otro no se solapa. Las solicitudes pendientes y las reservas aprobadas bloquean el horario; las rechazadas y canceladas no. Si el horario ya está ocupado, la creación devuelve HTTP `409 Conflict` y no persiste otra solicitud. Los estados posibles son `pending`, `approved`, `rejected` y `cancelled`.

Ningún usuario, incluidos los administradores, puede reservar el mismo espacio durante más de cuatro horas consecutivas. La regla suma intervalos directamente contiguos del mismo usuario y espacio que estén `pending` o `approved`; reservas de otro usuario, con un intervalo libre, o en estado `rejected` o `cancelled` no se suman. Exactamente cuatro horas está permitido. Crear una solicitud que exceda el límite devuelve HTTP `400 Bad Request` con el motivo y no crea una reserva. Al aprobar, el sistema vuelve a validar el límite; si no se cumple, responde HTTP 400 y la solicitud conserva el estado pendiente. Las reservas existentes no se modifican por esta regla.

Un administrador puede consultar `GET /api/reservations/pending/` y decidir una solicitud con `POST /api/reservations/{id}/approve/` o `/reject/`. La aprobación vuelve a comprobar que el espacio siga activo, que no exista otro conflicto y que se cumpla el límite de cuatro horas, excluyendo la solicitud revisada de la búsqueda de reservas contiguas. El propietario puede cancelar sus solicitudes pendientes o aprobadas con `POST /api/reservations/{id}/cancel/`. La historia está disponible en `GET /api/reservations/{id}/history/` para el propietario o un administrador; sus entradas incluyen estado, actor y fecha, en orden cronológico. Las transiciones no permitidas o que perdieron disponibilidad responden con HTTP `409 Conflict`.

La zona por defecto es UTC; para desarrollo local se puede indicar, por ejemplo, `TIME_ZONE=America/Bogota`.

## Interfaz web

Abre <http://127.0.0.1:8000/> e inicia sesión con una cuenta existente. Los periodos se muestran en la zona horaria del navegador.

### Recorrido de solicitante

1. En **Espacios académicos**, consulta los espacios activos disponibles.
2. En **Solicitar un espacio**, selecciona el espacio, escribe el motivo y define el inicio y el fin.
3. Pulsa **Consultar disponibilidad** para revisar el periodo y luego **Enviar solicitud**. La solicitud aparecerá como pendiente en **Reservas**.
4. En la tarjeta de la reserva, pulsa **Ver historial** para consultar los cambios de estado, quién los realizó y cuándo. Puedes pulsar **Ocultar historial** para cerrar el detalle.
5. Mientras la reserva propia esté pendiente o aprobada, usa **Cancelar** para liberar el periodo.

### Recorrido de administrador

1. En **Crear espacio**, completa nombre, tipo y capacidad para añadir un espacio al catálogo.
2. En **Solicitudes pendientes**, revisa los datos de cada solicitud y pulsa **Aprobar** o **Rechazar**. La disponibilidad se vuelve a validar al aprobar.
3. En la tarjeta de un espacio activo, pulsa **Desactivar espacio** para retirarlo del catálogo sin borrar su historial.

Los controles administrativos no se muestran a solicitantes. Las cuentas solicitantes deben ser creadas por un administrador; el registro público no está habilitado.

## Pruebas y verificaciones

Con el entorno virtual activado:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

La matriz de trazabilidad entre los escenarios OpenSpec y las pruebas previstas está en [docs/TRACEABILITY.md](./docs/TRACEABILITY.md).

## Configuración de despliegue

La clave incluida por defecto solo sirve para desarrollo local. Para ejecutar con `DJANGO_DEBUG=0`, configura `DJANGO_SECRET_KEY` y `DJANGO_ALLOWED_HOSTS`; el proyecto rechaza arrancar en modo no-debug con la clave de desarrollo. SQLite está previsto para la escala demostrativa descrita en el plan, no para alta concurrencia ni despliegue de producción.

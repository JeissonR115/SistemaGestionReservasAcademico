# PLAN DE INGENIERÍA — Sistema de Gestión de Reservas de Espacios Académicos

**Autor:** Jeison Felipe Rodriguez
**Estado:** Etapa 1 — previa a OpenSpec y a cualquier implementación.

---

## 1. Análisis del problema

### 1.1 Problemática

Las reservas de laboratorios, auditorios y salas de cómputo se gestionan por correo y hojas de cálculo. Esto genera:

- Solicitudes duplicadas.
- Conflictos de horario (dos reservas sobre el mismo espacio y hora).
- Dificultad para consultar disponibilidad.
- Falta de trazabilidad (quién reservó, quién aprobó, qué pasó).

### 1.2 Necesidades de la institución

- Un único punto centralizado de reservas.
- Garantía de que no existan reservas solapadas.
- Flujo de aprobación/rechazo controlado.
- Consulta de disponibilidad e historial.
- Control de acceso según el rol del usuario.

### 1.3 Actores

| Actor                            | Responsabilidad                                             |
| -------------------------------- | ----------------------------------------------------------- |
| Solicitante (docente/estudiante) | Consulta disponibilidad, crea y cancela sus reservas        |
| Administrador                    | Gestiona espacios y usuarios, aprueba o rechaza solicitudes |

### 1.4 Alcance

**Incluye:** gestión de espacios, usuarios y roles, solicitudes de reserva, validación de disponibilidad, prevención de solapamientos, aprobación/rechazo, cancelación, historial, API REST e interfaz web básica.

**No incluye (limitaciones):** notificaciones por correo, integración con sistemas institucionales (SSO), reservas recurrentes, despliegue en producción, app móvil, pagos.

---

## 2. Propuesta de solución

### 2.1 Descripción general

Aplicación web monolítica en Django que expone una **API REST** y una **interfaz gráfica ligera** (plantillas Django + JavaScript que consume la API) para mostrar disponibilidad y gestionar reservas. Pensada para ejecutarse con pocos comandos y sin servicios externos.

### 2.2 Funcionalidades prioritarias

1. **Alta:** espacios, usuarios/roles, crear solicitud, validación de disponibilidad, prevención de solapamientos.
2. **Media:** aprobación/rechazo, cancelación, historial.
3. **Baja:** estilos visuales, filtros adicionales.

### 2.3 Módulos

| Módulo (app Django) | Contenido                                             |
| ------------------- | ----------------------------------------------------- |
| `accounts`          | Usuarios, roles, permisos, autenticación              |
| `spaces`            | CRUD de espacios académicos (tipo, capacidad, estado) |
| `reservations`      | Solicitudes, estados, reglas de negocio, historial    |
| `web`               | Plantillas e interfaz gráfica que consume la API      |

### 2.4 Estrategia progresiva

Desarrollo incremental por módulos, cada uno con su especificación, código y pruebas antes de pasar al siguiente (ver sección 4).

---

## 3. Decisiones de arquitectura y tecnología

### 3.1 Arquitectura

**Monolito modular en capas** (modelos → servicios → API/vistas).

- Justificación: el sistema es pequeño, lo desarrolla una persona y debe ser fácil de ejecutar; un monolito minimiza complejidad operativa.
- Las **reglas de negocio** viven en una capa de servicios (`reservations/services.py`), no en las vistas, para que sean verificables y fáciles de modificar sin tocar la API.

### 3.2 Stack

| Componente           | Tecnología                               |
| -------------------- | ---------------------------------------- |
| Lenguaje             | Python 3.12                              |
| Framework            | Django 5                                 |
| API                  | Django REST Framework                    |
| Base de datos        | SQLite                                   |
| Interfaz             | Plantillas Django + JavaScript (`fetch`) |
| Pruebas              | `django.test` / `APITestCase`            |
| Control de versiones | Git                                      |

### 3.3 Persistencia

SQLite con el ORM de Django y migraciones versionadas. Entidades: `User` (con rol), `Space`, `Reservation` (espacio, usuario, inicio, fin, estado, motivo) y `ReservationLog` (historial de cambios de estado).

### 3.4 Organización de componentes

```
proyecto/
├── PLAN_INGENIERIA.md
├── INFORME_FINAL.md
├── README.md
├── openspec/
├── manage.py
├── config/            # settings, urls
├── accounts/
├── spaces/
├── reservations/      # models, services, serializers, views, tests
└── web/               # templates, static
```

### 3.5 Decisiones técnicas y alternativas descartadas

| #   | Decisión                    | Alternativas descartadas                     | Motivo                                                                                                 |
| --- | --------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| 1   | Monolito Django             | Microservicios; backend separado + SPA React | Sobredimensionado para el alcance; más puntos de fallo y más difícil de ejecutar                       |
| 2   | SQLite                      | PostgreSQL; MySQL                            | Cero configuración; suficiente para demostración. Se asume la limitación de concurrencia (ver riesgos) |
| 3   | Django REST Framework       | Vistas Django puras; FastAPI                 | Serializadores, permisos y pruebas de API listos; integra con el ORM y el admin                        |
| 4   | Autenticación por sesión    | JWT                                          | Más simple y segura por defecto con la UI en el mismo origen                                           |
| 5   | UI con plantillas + `fetch` | React/Vue                                    | Evita un segundo proyecto y herramientas de build; se puede estilizar después                          |

---

## 4. Estrategia de desarrollo

### 4.1 Metodología

**SDD (Spec-Driven Development)** con OpenSpec, con ciclos cortos e incrementales. Una rama/commit por cambio; commits atómicos con mensajes convencionales (`feat:`, `docs:`, `test:`).

### 4.2 Etapas, orden y criterios de terminado

| Etapa | Contenido                                  | Se considera terminada cuando                                                                         |
| ----- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| 0     | Plan de ingeniería                         | Documento completo y en commit independiente                                                          |
| 1     | Especificaciones y revisión                | Todas las capacidades con requisitos y escenarios verificables; sin contradicciones; tareas definidas |
| 2     | Base del proyecto + `accounts`             | Login y roles funcionando; pruebas pasan                                                              |
| 3     | `spaces`                                   | CRUD con permisos por rol; pruebas pasan                                                              |
| 4     | `reservations` núcleo                      | Crear solicitud, validar disponibilidad, impedir solapamientos; pruebas pasan                         |
| 5     | Aprobación/rechazo, cancelación, historial | Transiciones de estado válidas y registradas; pruebas pasan                                           |
| 6     | Interfaz gráfica                           | Se pueden consultar disponibilidad y gestionar reservas desde el navegador                            |
| 7     | Gestión de cambios                         | Nueva regla aplicada vía OpenSpec, con pruebas y sin regresiones                                      |
| 8     | Cierre                                     | Pruebas verdes, README e INFORME_FINAL completos                                                      |

### 4.3 Dependencias

`accounts` → `spaces` → `reservations` → `web`. Las reservas dependen de usuarios y espacios; la interfaz depende de la API completa.

---

## 5. Estrategia de calidad

### 5.1 Tipos de pruebas

- **Unitarias:** reglas de negocio en la capa de servicios (solapamiento, transiciones de estado).
- **De integración/API:** endpoints, códigos HTTP, permisos por rol.
- **De regresión:** suite completa ejecutada tras cada cambio.
- **Manuales:** recorrido de la interfaz gráfica.

### 5.2 Riesgos y mitigación

| #   | Riesgo                                                                     | Mitigación                                                                                              |
| --- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 1   | Reservas simultáneas que burlen la validación (condición de carrera)       | Validación dentro de `transaction.atomic`, pruebas de solapamiento y restricción en la capa de servicio |
| 2   | Especificaciones ambiguas o contradictorias                                | Fase de revisión obligatoria antes de implementar                                                       |
| 3   | Código generado por IA que no cumple la especificación                     | Revisión manual, pruebas por escenario, trazabilidad requisito ↔ prueba                                 |
| 4   | Cambios de reglas que rompan funcionalidad existente                       | Suite de regresión y análisis de impacto previo                                                         |
| 5   | Acceso indebido a funciones de administrador                               | Permisos por rol en la API y pruebas de acceso denegado                                                 |
| 6   | Errores con zonas horarias y fronteras de intervalo (fin = inicio de otra) | Definir intervalos semiabiertos `[inicio, fin)` en la especificación y probar casos límite              |
| 7   | Limitaciones de SQLite con alta concurrencia                               | Aceptado por el alcance; documentado en el informe final                                                |

### 5.3 Verificación de requisitos

- Cada requisito tiene escenarios de aceptación (Dado/Cuando/Entonces) en OpenSpec.
- Cada escenario se corresponde con al menos una prueba automatizada.
- Matriz de trazabilidad: requisito → escenario → prueba → código.
- Verificación del historial de Git para comprobar la secuencia plan → specs → código.

---

## 6. Uso de SDD e inteligencia artificial

### 6.1 Uso de OpenSpec

Inicializar OpenSpec en el repositorio, definir una capacidad (_spec_) por cada funcionalidad mínima requerida y usar propuestas de cambio (_changes_) con sus tareas para cada incremento, incluyendo el cambio de regla de negocio posterior.

### 6.2 Del plan a las especificaciones

Cada módulo y funcionalidad de la sección 2 se convierte en una capacidad con requisitos (con restricciones) y escenarios de aceptación verificables; las decisiones de la sección 3 definen las restricciones técnicas, y los criterios de la sección 4, las tareas.

### 6.3 Actividades delegadas a la IA

- Redacción de borradores de especificaciones.
- Generación de código siguiendo la especificación y la arquitectura definida.
- Generación de borradores de pruebas.
- Apoyo en la documentación.

### 6.4 Verificación del código generado

- Revisión manual de cada cambio antes del commit.
- Ejecución de la suite de pruebas.
- Comparación con los escenarios de la especificación.
- Rechazo o corrección de lo que se desvíe de la arquitectura.

### 6.5 Decisiones de responsabilidad del estudiante

- Arquitectura, stack y alternativas descartadas.
- Aprobación de las especificaciones y resolución de ambigüedades.
- Análisis de impacto de los cambios.
- Aceptación o rechazo del código generado.
- Sustentación final del sistema y del proceso.

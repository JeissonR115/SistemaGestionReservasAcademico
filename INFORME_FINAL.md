# Informe final

> **Nota sobre las fuentes:** este informe se limita a `PLAN_INGENIERIA.md` y a los artefactos OpenSpec del repositorio. No se encontraron `resultados_pruebas.txt` ni `historial_git.txt`. Por ello, no se atribuyen resultados detallados ni commits que no estén documentados en esas fuentes. Los campos `[COMPLETAR]` identifican información que debe aportar o verificar el estudiante.

## 1. Resumen del proyecto

El plan describe una aplicación web monolítica en Django para centralizar la gestión de reservas de espacios académicos. Su alcance contempla gestión de espacios, cuentas y roles, solicitudes, disponibilidad, prevención de solapamientos, revisión administrativa, cancelación e historial, con API REST e interfaz web básica. Excluye notificaciones por correo, integración institucional/SSO, reservas recurrentes, despliegue productivo, aplicación móvil y pagos.

La arquitectura prevista separa modelos, servicios y vistas/API en aplicaciones Django. El plan selecciona Python 3.12, Django, Django REST Framework, SQLite, autenticación por sesión y una interfaz de plantillas Django con JavaScript. Las reglas de negocio de reservas deben residir en una capa de servicios. OpenSpec define escenarios verificables para las ocho capacidades iniciales y posteriormente agrega una capacidad de límite de duración.

Fuentes: [PLAN_INGENIERIA.md](./PLAN_INGENIERIA.md), [propuesta de capacidades](./openspec/changes/define-reservas-espacios-academicos/proposal.md), [diseño inicial](./openspec/changes/define-reservas-espacios-academicos/design.md) y [propuesta del límite de duración](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/proposal.md).

## 2. Análisis de resultados

### Requisitos y pruebas

Los documentos de tareas marcan como completadas las etapas de capacidades, implementación, pruebas y gestión del cambio. En particular, las tareas iniciales dicen que se creó una matriz requisito–escenario–prueba, y las tareas del cambio archivado registran casos de duración y regresión como completados.

Sin embargo, el archivo `resultados_pruebas.txt` no está presente en las fuentes del repositorio consultadas. Por tanto, no es posible confirmar desde ese registro qué comando se ejecutó, cuántas pruebas se ejecutaron, su resultado ni si hubo fallos. Las marcas `[x]` de los archivos `tasks.md` documentan el estado declarado de las tareas, pero no sustituyen una salida de pruebas reproducible.

### Matriz requisito → escenario/prueba

La columna de escenarios recoge los escenarios Dado/Cuando/Entonces definidos por OpenSpec. Se indican como cobertura especificada, no como resultado de ejecución. El resultado de cada prueba debe completarse desde `resultados_pruebas.txt`, archivo que no se encontró.

| Requisito/capacidad | Escenario o prueba especificada | Resultado de ejecución |
|---|---|---|
| Gestión de espacios | Administrador crea un espacio válido; capacidad no positiva; catálogo muestra espacio activo; espacio inactivo excluido. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |
| Usuarios | Cuenta creada por administrador; desactivación impide iniciar sesión; usuario activo inicia sesión; usuario inactivo no; usuario autenticado cierra sesión. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |
| Roles y permisos | Cuenta recibe rol válido; rol ausente o inválido se rechaza; solicitante no puede ejecutar acciones administrativas ni ver solicitud ajena; administrador ejecuta operaciones protegidas; usuario sin sesión es denegado. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |
| Solicitud de reserva | Solicitante crea una solicitud pendiente propia; faltan datos obligatorios; periodo vacío o invertido; espacio inactivo o inexistente; propietario consulta sus datos. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |
| Validación de disponibilidad | Pendiente bloquea; rechazadas/canceladas no bloquean; intervalos adyacentes con fin = inicio no se solapan; intervalos intersectados sí; espacio inactivo no disponible. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |
| Prevención de simultáneas | Dos solicitudes solapadas concurrentes aceptan como máximo una; una solicitud posterior a una pendiente conflictiva no crea una segunda reserva. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |
| Aprobación y rechazo | Administrador lista pendientes; aprueba una válida excluyendo la solicitud revisada del conflicto; no aprueba espacio inactivo o con otro bloqueo; rechaza una pendiente; decisión duplicada se deniega sin alterar el estado/historial. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |
| Cancelación e historial | Propietario cancela una pendiente o aprobada; no cancela una reserva ajena o terminal; cambios registran estado, actor y fecha; visor autorizado consulta historial cronológico. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |
| Límite de cuatro horas | Se aceptan 3h59 y 4h; se rechaza 4h01; se evalúan cadenas contiguas propias pendientes/aprobadas, total exactamente 4h, reservas de otra persona y estados rechazado/cancelado; la aprobación revalida y excluye el ID candidato. | [COMPLETAR: evidencia en `resultados_pruebas.txt`, no encontrado] |

### Escenarios sin cubrir

Los `tasks.md` iniciales declaran que cada escenario debía tener al menos una prueba prevista y marcan la revisión de esa matriz como completada. Los `tasks.md` de implementación y del cambio de cuatro horas también marcan como completadas las verificaciones correspondientes. Sin el archivo de resultados ni una matriz con referencias a pruebas concretas, **no es posible determinar con evidencia suficiente si existe algún escenario sin cubrir o si las pruebas previstas se ejecutaron y pasaron**.

**Pendiente de completar:** añadir o localizar `resultados_pruebas.txt` con la salida íntegra del comando de pruebas y la relación escenario → prueba concreta.

## 3. Verificación de la secuencia plan → specs → código → cambio

El plan establece una secuencia incremental: definir especificaciones verificables, implementar por etapas, probar y revisar el historial de Git. Los artefactos OpenSpec respaldan documentalmente este orden:

1. `PLAN_INGENIERIA.md` define las etapas, las capacidades y el criterio de trazabilidad.
2. La propuesta y el diseño de `define-reservas-espacios-academicos` declaran la creación de especificaciones antes de implementar el sistema.
3. Su archivo `tasks.md` organiza tareas de especificación, cuentas, espacios, reservas, revisión, interfaz y cierre.
4. La propuesta archivada `2026-10-22-limite-cuatro-horas` declara el cambio de negocio posterior; su diseño y tareas detallan la implementación y regresión.

Las ocho capacidades iniciales están en `openspec/changes/define-reservas-espacios-academicos/specs/`; el único spec encontrado bajo `openspec/specs/` corresponde al límite de duración de cuatro horas. Por tanto, los artefactos documentan propuestas de capacidades iniciales en un cambio activo y una capacidad de duración archivada.

Esta secuencia puede comprobarse a nivel de artefactos, pero no a nivel de commits. `historial_git.txt` no fue encontrado, por lo que no es posible citar hashes, mensajes ni fechas de commits que demuestren el orden real de los cambios.

| Hito | Evidencia documental | Commit |
|---|---|---|
| Plan de ingeniería | [PLAN_INGENIERIA.md](./PLAN_INGENIERIA.md) | [COMPLETAR: historial_git.txt no encontrado] |
| Especificaciones iniciales | [propuesta](./openspec/changes/define-reservas-espacios-academicos/proposal.md), [diseño](./openspec/changes/define-reservas-espacios-academicos/design.md) y `specs/` de ese cambio | [COMPLETAR: historial_git.txt no encontrado] |
| Implementación según tareas | [tareas del cambio inicial](./openspec/changes/define-reservas-espacios-academicos/tasks.md) | [COMPLETAR: historial_git.txt no encontrado] |
| Cambio posterior de cuatro horas | [propuesta archivada](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/proposal.md), [diseño](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/design.md), [spec](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/specs/limite-duracion-reserva/spec.md) y [tareas](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/tasks.md) | [COMPLETAR: historial_git.txt no encontrado] |

## 4. Dificultades

### Evidenciadas en los documentos

- El plan identifica como riesgo las especificaciones ambiguas o contradictorias y establece una revisión previa a la implementación.
- El diseño inicial fija intervalos semiabiertos `[inicio, fin)` y que las solicitudes pendientes y aprobadas bloqueen el horario, para que disponibilidad, creación y aprobación compartan la misma regla.
- El diseño del cambio de cuatro horas identifica cadenas de reservas contiguas como un caso que requiere evaluar el bloque completo, así como solicitudes preexistentes que deben conservarse pero volver a validarse al aprobar.
- El plan y los diseños reconocen que SQLite puede limitar la concurrencia y que el proyecto se orienta a una escala demostrativa.

### Información personal por completar

- Dificultades de implementación o depuración que no estén registradas en los artefactos: **[COMPLETAR]**.
- Problemas de entorno, instalación o coordinación experimentados por el estudiante: **[COMPLETAR]**.
- Ajustes manuales o decisiones tomadas durante la revisión del código generado: **[COMPLETAR]**.

## 5. Decisiones modificadas

### Pendientes que bloquean su propio horario y exclusión por ID al aprobar

La regla general documentada es que las reservas `pending` y `approved` bloquean un periodo. Aplicada sin excepción a la consulta de aprobación, la propia solicitud pendiente podría aparecer como conflicto consigo misma. El diseño inicial aclara el caso operacional: al aprobar se excluye del conflicto la reserva que se está revisando, pero se mantienen como bloqueadoras todas las demás solicitudes pendientes y aprobadas.

El diseño del límite de cuatro horas conserva el mismo principio para la consulta de reservas vecinas: la reserva candidata se evalúa una sola vez como intervalo candidato y se excluye su propio ID del conjunto de vecinas. Así, la exclusión no libera el horario frente a terceros; evita que el registro candidato se cuente dos veces o se bloquee a sí mismo.

### Decisión de que las pendientes bloqueen

El diseño inicial indica explícitamente que las solicitudes pendientes bloquean disponibilidad y que las rechazadas y canceladas liberan el periodo. También dice que esta política fue confirmada por el solicitante. El cambio de cuatro horas la conserva como regla preexistente.

### ¿Cambió `PLAN_INGENIERIA.md`?

El diseño archivado del cambio declara que el plan no debía modificarse: la regla estaba alineada con la capa de servicios y la etapa 7. Esto evidencia la decisión prevista, pero no permite verificar el historial de edición real porque falta `historial_git.txt`. Confirmación mediante commits: **[COMPLETAR]**.

## 6. Gestión del cambio de las cuatro horas

La propuesta OpenSpec añade un máximo de cuatro horas por reserva y por bloque continuo del mismo usuario y espacio. La regla aplica al crear solicitudes y al aprobar pendientes; excederla debe producir HTTP 400 con un mensaje claro. Las reservas existentes no se modifican y no se requiere migración de datos.

El cambio define:

- aceptar una solicitud de 3h59 o exactamente 4h, y rechazar 4h01;
- sumar únicamente intervalos directamente contiguos, pendientes o aprobados, del mismo usuario y espacio;
- no sumar reservas de otra persona ni intervalos rechazados o cancelados;
- volver a validar al aprobar y mantener en pendiente una solicitud que exceda el límite, sin crear un registro de decisión;
- excluir por ID la solicitud que está siendo aprobada de la consulta de vecinas.

La capacidad se documenta en [openspec/specs/limite-duracion-reserva/spec.md](./openspec/specs/limite-duracion-reserva/spec.md) y su cambio archivado en [la propuesta](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/proposal.md), [el diseño](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/design.md), [la especificación](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/specs/limite-duracion-reserva/spec.md) y [las tareas](./openspec/changes/archive/2026-10-22-limite-cuatro-horas/tasks.md).

Las tareas archivadas marcan como completados los casos de 3h59, 4h, 4h01, continuidad por estado/propietario, exclusión del ID candidato, respuesta HTTP y regresión completa. El archivo `resultados_pruebas.txt` no está disponible; por ello, el resultado efectivo de esas pruebas queda **[COMPLETAR]** y no se puede confirmar desde el repositorio indicado.

## 7. Conclusiones sobre SDD con IA

### Ventajas documentadas

- OpenSpec organiza requisitos en capacidades y escenarios Dado/Cuando/Entonces verificables.
- La relación plan → especificaciones → tareas ofrece una estructura para implementar en incrementos.
- La separación entre servicios y API, junto con pruebas unitarias y de integración, facilita revisar reglas de negocio y permisos.
- Un cambio posterior puede documentarse en un artefacto OpenSpec separado, con impacto, decisiones y tareas de regresión explícitos.

### Límites documentados

- El plan identifica como riesgo que el código generado por IA no cumpla la especificación; por eso requiere revisión manual, pruebas por escenario y trazabilidad.
- Los artefactos de planificación por sí solos no demuestran que una prueba haya pasado ni que cada escenario esté cubierto: se requiere salida de pruebas y evidencia trazable.
- SQLite se acepta para la escala de demostración, pero sus limitaciones de concurrencia impiden asumir comportamiento de alta concurrencia propio de un sistema de producción.

### Responsabilidad del estudiante

Según el plan, corresponde al estudiante definir arquitectura y stack, aprobar especificaciones y resolver ambigüedades, analizar impacto, aceptar o rechazar código generado, revisar los cambios y sustentar el sistema y el proceso. La IA se plantea como apoyo para borradores de especificaciones, código, pruebas y documentación, no como sustituto de esa revisión.

## 8. Limitaciones conocidas

- **Concurrencia en SQLite:** el plan acepta esta limitación para una aplicación de demostración y el diseño propone transacciones y pruebas de concurrencia. No se documenta como una solución adecuada para alta concurrencia.
- **Alcance funcional:** no se contemplan notificaciones por correo, SSO/integraciones institucionales, reservas recurrentes, despliegue productivo, aplicación móvil ni pagos.
- **Verificación del cierre:** faltan `resultados_pruebas.txt` e `historial_git.txt`; no es posible corroborar desde esas fuentes el resultado detallado de la suite, la cobertura ejecutada ni la secuencia de commits.
- **Configuración horaria:** el diseño inicial deja abierta la confirmación de la zona horaria institucional; se especifica el uso de fechas con zona horaria.

**Pendiente de cierre documental:** incorporar los registros de pruebas e historial Git y completar los campos `[COMPLETAR]` antes de presentar como verificados los resultados, la cobertura ejecutada y la secuencia de commits.

# Tasks

## 1. Especificaciones y revisión (Etapa 1)

- [ ] 1.1 Revisar y aprobar las ocho capacidades de `specs/`, resolviendo contradicciones; verificar la decisión de que solicitudes pendientes bloquean el horario y que los intervalos son `[inicio, fin)`.
- [ ] 1.2 Crear una matriz requisito → escenario → prueba para todas las capacidades y comprobar que cada escenario tiene al menos una prueba prevista.

## 2. Base del proyecto y cuentas (Etapa 2)

- [ ] 2.1 Crear el proyecto Django 5 con Python 3.12, DRF, SQLite y las apps previstas; verificar que el servidor inicia y que las migraciones iniciales se aplican con éxito.
- [ ] 2.2 Implementar cuentas, autenticación por sesión y roles de solicitante/administrador; verificar inicio y cierre de sesión, gestión de cuentas y permisos mediante pruebas unitarias y de API.
- [ ] 2.3 Documentar en el README la configuración y ejecución local del proyecto y verificar que otra persona pueda seguir esos pasos desde una instalación limpia.

## 3. Gestión de espacios (Etapa 3)

- [ ] 3.1 Implementar alta, consulta, actualización y desactivación de espacios con sus validaciones y permisos; verificar los escenarios de `gestion-espacios` con pruebas de API.
- [ ] 3.2 Documentar los campos y operaciones de gestión de espacios y verificar que la documentación coincida con el comportamiento probado.

## 4. Núcleo de reservas (Etapa 4)

- [ ] 4.1 Implementar solicitudes de reserva y reglas de disponibilidad en la capa de servicios; verificar campos obligatorios, periodos inválidos, espacios inactivos y límites `[inicio, fin)` con pruebas unitarias y de API.
- [ ] 4.2 Hacer atómica la comprobación de conflictos y el registro de solicitudes; verificar que, ante solicitudes simultáneas solapadas, como máximo una quede pendiente y las demás reciban un conflicto explícito.
- [ ] 4.3 Documentar estados, validación de disponibilidad y resultado de conflictos; verificar que los ejemplos coincidan con los escenarios de aceptación y las pruebas.

## 5. Aprobación, rechazo, cancelación e historial (Etapa 5)

- [ ] 5.1 Implementar aprobación y rechazo de solicitudes pendientes con sus restricciones de estado y disponibilidad; verificar transiciones permitidas y denegadas mediante pruebas de servicios y API.
- [ ] 5.2 Implementar cancelación por el propietario y registro consultable de cambios de estado; verificar autorización, liberación de periodos e historial cronológico con pruebas.
- [ ] 5.3 Documentar el flujo y los estados de las reservas y verificar su correspondencia con los escenarios probados.

## 6. Interfaz gráfica (Etapa 6)

- [ ] 6.1 Implementar páginas y flujos web para consultar espacios y disponibilidad, crear solicitudes y gestionar las operaciones permitidas según el rol; verificar el recorrido manual de solicitante y administrador.
- [ ] 6.2 Documentar el recorrido básico de la interfaz y verificar las instrucciones con una ejecución local.

## 7. Gestión de cambios (Etapa 7)

- [ ] 7.1 Aplicar una nueva regla de negocio mediante una propuesta OpenSpec separada, implementar sus escenarios y verificar sus pruebas sin regresiones en los requisitos existentes.

## 8. Cierre (Etapa 8)

- [ ] 8.1 Ejecutar la suite completa de pruebas y verificar que todas las pruebas pasen.
- [ ] 8.2 Completar el README y `INFORME_FINAL.md` con configuración, uso, pruebas y limitaciones; verificar que los comandos documentados funcionen y que se informe la limitación de concurrencia de SQLite.
- [ ] 8.3 Revisar el historial de Git para verificar la secuencia plan → especificaciones → implementación y confirmar que los cambios están descritos por sus artefactos OpenSpec.

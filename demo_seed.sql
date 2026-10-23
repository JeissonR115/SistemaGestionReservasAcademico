PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

DELETE FROM reservations_reservationlog;
DELETE FROM reservations_reservation;
DELETE FROM spaces_space;
DELETE FROM accounts_user;

INSERT INTO accounts_user (
    id,
    password,
    last_login,
    is_superuser,
    username,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined,
    role
) VALUES
    (
        1,
        'pbkdf2_sha256$1000000$SO9dKzqnlA1NBS22vqvOiL$FCP508J+A0AVz+pgxJzvBMoNIsspnjNrH4nV82kQPgs=',
        NULL,
        0,
        'admin',
        '',
        '',
        'admin@academico.local',
        0,
        1,
        '2026-10-23 08:00:00',
        'administrator'
    ),
    (
        2,
        'pbkdf2_sha256$1000000$yZw73CQAnkTpdgiXRIP36K$IAZTARJGbfUWbQyaDpvwDMK52+/3XCPSfH9cttulwPY=',
        NULL,
        0,
        'requester',
        '',
        '',
        'requester@academico.local',
        0,
        1,
        '2026-10-23 08:15:00',
        'requester'
    ),
    (
        3,
        'pbkdf2_sha256$1000000$Hmnck2lCSNzmVypEe1WlHE$HpCaN+5N0f9gdAaG1MYNEzSxHoOIrxJ4wt9/IwAdUwA=',
        NULL,
        1,
        'root',
        '',
        '',
        'root@academico.local',
        1,
        1,
        '2026-10-23 08:30:00',
        'administrator'
    );

INSERT INTO spaces_space (
    id,
    name,
    space_type,
    capacity,
    is_active,
    reservation_version
) VALUES
    (1, 'Auditorio Principal', 'Auditorio', 120, 1, 0),
    (2, 'Sala de Trabajo 2', 'Sala de estudio', 25, 1, 0),
    (3, 'Laboratorio de Redes', 'Laboratorio', 18, 1, 0),
    (4, 'Salon de Graduación', 'Salon', 50, 0, 0);

INSERT INTO reservations_reservation (
    id,
    purpose,
    start_at,
    end_at,
    status,
    created_at,
    requester_id,
    space_id
) VALUES
    (1, 'Reunión de coordinación académica', '2026-11-10 09:00:00', '2026-11-10 10:30:00', 'approved', '2026-10-23 08:40:00', 2, 1),
    (2, 'Taller de programación', '2026-11-12 14:00:00', '2026-11-12 15:00:00', 'pending', '2026-10-23 08:45:00', 2, 2),
    (3, 'Presentación de proyecto', '2026-11-15 09:00:00', '2026-11-15 10:00:00', 'rejected', '2026-10-23 08:50:00', 2, 3),
    (4, 'Prueba de demostración para presentación', '2026-11-18 16:00:00', '2026-11-18 17:30:00', 'cancelled', '2026-10-23 08:55:00', 2, 1);

INSERT INTO reservations_reservationlog (
    id,
    reservation_id,
    status,
    actor_id,
    changed_at
) VALUES
    (1, 1, 'approved', 1, '2026-10-23 09:00:00'),
    (2, 2, 'pending', 2, '2026-10-23 09:05:00'),
    (3, 3, 'rejected', 1, '2026-10-23 09:10:00'),
    (4, 4, 'cancelled', 2, '2026-10-23 09:15:00');

COMMIT;
PRAGMA foreign_keys = ON;

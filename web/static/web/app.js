const feedback = document.querySelector('#feedback');
let csrfToken = '';

async function loadCsrfToken() {
    const response = await fetch('/api/auth/csrf/', {
        credentials: 'same-origin',
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.detail || 'No se pudo iniciar la sesión segura.');
    }
    csrfToken = result.csrfToken;
}

async function api(path, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const headers = new Headers(options.headers || {});
    if (options.body && !(options.body instanceof FormData)) {
        headers.set('Content-Type', 'application/json');
    }
    if (method !== 'GET') {
        headers.set('X-CSRFToken', csrfToken);
    }
    const response = await fetch(path, {
        ...options,
        method,
        headers,
        credentials: 'same-origin',
    });
    const result = response.status === 204 ? null : await response.json();
    if (!response.ok) {
        throw new Error(result?.detail || JSON.stringify(result));
    }
    return result;
}

function showFeedback(message, isError = false) {
    feedback.textContent = message;
    feedback.classList.toggle('error', isError);
}

function element(tag, text, className = '') {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) {
        node.className = className;
    }
    return node;
}

function localDateTime(value) {
    return new Date(value).toLocaleString();
}

function serializeLocalDateTime(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        throw new Error('Indica una fecha y hora válida.');
    }
    return date.toISOString();
}

async function loadSpaces() {
    const spaces = await api('/api/spaces/');
    const list = document.querySelector('#spaces-list');
    const select = document.querySelector('#reservation-space');
    list.replaceChildren();
    select.replaceChildren();

    for (const space of spaces) {
        const card = element('article', '', 'card');
        card.append(
            element('h3', space.name),
            element('p', `Tipo: ${space.space_type}`),
            element('p', `Capacidad: ${space.capacity}`),
        );
        if (!space.is_active) {
            card.append(element('p', 'Inactivo'));
        }
        if (document.body.dataset.role === 'administrator') {
            const actions = element('div', '', 'card-actions');
            if (space.is_active) {
                const deactivate = element('button', 'Desactivar espacio', 'button button-danger');
                deactivate.type = 'button';
                deactivate.addEventListener('click', async () => {
                    try {
                        await api(`/api/spaces/${space.id}/`, { method: 'DELETE' });
                        await loadSpaces();
                    } catch (error) {
                        showFeedback(error.message, true);
                    }
                });
                actions.append(deactivate);
            }
            card.append(actions);
        }
        list.append(card);

        if (space.is_active) {
            select.append(new Option(`${space.name} (${space.capacity})`, space.id));
        }
    }
}

async function loadReservations() {
    const reservations = await api('/api/reservations/');
    const list = document.querySelector('#reservations-list');
    list.replaceChildren();
    for (const reservation of reservations) {
        const card = element('article', '', 'card');
        card.append(
            element('h3', reservation.space_name),
            element('p', `Estado: ${reservation.status}`),
            element('p', `Motivo: ${reservation.purpose}`),
            element('p', `${localDateTime(reservation.start_at)} – ${localDateTime(reservation.end_at)}`),
        );
        const historyButton = element(
            'button',
            'Ver historial',
            'button button-secondary',
        );
        historyButton.type = 'button';
        const historyList = element('div', '', 'card-actions');
        historyList.hidden = true;
        historyButton.addEventListener('click', async () => {
            if (!historyList.hidden) {
                historyList.hidden = true;
                historyButton.textContent = 'Ver historial';
                return;
            }
            try {
                const entries = await api(
                    `/api/reservations/${reservation.id}/history/`,
                );
                historyList.replaceChildren();
                for (const entry of entries) {
                    historyList.append(element(
                        'p',
                        `${entry.status} — ${entry.actor_username} — ${localDateTime(entry.changed_at)}`,
                    ));
                }
                historyList.hidden = false;
                historyButton.textContent = 'Ocultar historial';
            } catch (error) {
                showFeedback(error.message, true);
            }
        });
        card.append(historyButton, historyList);
        if (
            reservation.requester_username === document.body.dataset.username
            && (reservation.status === 'pending' || reservation.status === 'approved')
        ) {
            const cancel = element('button', 'Cancelar', 'button button-danger');
            cancel.type = 'button';
            cancel.addEventListener('click', async () => {
                try {
                    await api(`/api/reservations/${reservation.id}/cancel/`, {
                        method: 'POST',
                    });
                    await loadReservations();
                    await loadPending();
                    showFeedback('La reserva fue cancelada.');
                } catch (error) {
                    showFeedback(error.message, true);
                }
            });
            card.append(cancel);
        }
        list.append(card);
    }
}

async function loadPending() {
    const list = document.querySelector('#pending-list');
    if (!list) {
        return;
    }
    const pending = await api('/api/reservations/pending/');
    list.replaceChildren();
    for (const reservation of pending) {
        const card = element('article', '', 'card');
        card.append(
            element('h3', reservation.space_name),
            element('p', `Solicitante: ${reservation.requester_username}`),
            element('p', `Motivo: ${reservation.purpose}`),
            element('p', `${localDateTime(reservation.start_at)} – ${localDateTime(reservation.end_at)}`),
        );
        const actions = element('div', '', 'card-actions');
        for (const decision of ['approve', 'reject']) {
            const button = element(
                'button',
                decision === 'approve' ? 'Aprobar' : 'Rechazar',
                'button',
            );
            button.type = 'button';
            button.addEventListener('click', async () => {
                try {
                    await api(`/api/reservations/${reservation.id}/${decision}/`, {
                        method: 'POST',
                    });
                    await loadPending();
                    await loadReservations();
                    showFeedback(
                        decision === 'approve'
                            ? 'Solicitud aprobada.'
                            : 'Solicitud rechazada.',
                    );
                } catch (error) {
                    showFeedback(error.message, true);
                }
            });
            actions.append(button);
        }
        card.append(actions);
        list.append(card);
    }
}

async function initializeDashboard() {
    await loadCsrfToken();
    await loadSpaces();
    await loadReservations();
    await loadPending();

    const reservationForm = document.querySelector('#reservation-form');
    reservationForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = new FormData(reservationForm);
        try {
            await api('/api/reservations/', {
                method: 'POST',
                body: JSON.stringify({
                    space: Number(form.get('space')),
                    purpose: form.get('purpose'),
                    start_at: serializeLocalDateTime(form.get('start_at')),
                    end_at: serializeLocalDateTime(form.get('end_at')),
                }),
            });
            reservationForm.reset();
            await loadReservations();
            await loadPending();
            showFeedback('Solicitud enviada. Quedó pendiente de aprobación.');
        } catch (error) {
            showFeedback(error.message, true);
        }
    });

    document.querySelector('#check-availability').addEventListener('click', async () => {
        const form = new FormData(reservationForm);
        const result = document.querySelector('#availability-result');
        result.classList.remove('error');
        try {
            const startAt = serializeLocalDateTime(form.get('start_at'));
            const endAt = serializeLocalDateTime(form.get('end_at'));
            if (startAt >= endAt) {
                throw new Error('La hora de fin debe ser posterior al inicio.');
            }
            const query = new URLSearchParams({
                start_at: startAt,
                end_at: endAt,
            });
            const spaceId = form.get('space');
            const availability = await api(
                `/api/spaces/${spaceId}/availability/?${query}`,
            );
            result.textContent = availability.available
                ? 'El espacio está disponible.'
                : 'El espacio no está disponible en ese horario.';
        } catch (error) {
            result.textContent = error.message;
            result.classList.add('error');
        }
    });

    const spaceForm = document.querySelector('#space-form');
    if (spaceForm) {
        spaceForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const form = new FormData(spaceForm);
            try {
                await api('/api/spaces/', {
                    method: 'POST',
                    body: JSON.stringify({
                        name: form.get('name'),
                        space_type: form.get('space_type'),
                        capacity: Number(form.get('capacity')),
                        is_active: true,
                    }),
                });
                spaceForm.reset();
                await loadSpaces();
                showFeedback('Espacio creado.');
            } catch (error) {
                showFeedback(error.message, true);
            }
        });
    }

    document.querySelector('#logout-button').addEventListener('click', async () => {
        try {
            await api('/api/auth/logout/', { method: 'POST' });
            window.location.reload();
        } catch (error) {
            showFeedback(error.message, true);
        }
    });
}

async function initializeLogin() {
    await loadCsrfToken();
    document.querySelector('#login-form').addEventListener('submit', async (event) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        try {
            await api('/api/auth/login/', {
                method: 'POST',
                body: JSON.stringify({
                    username: form.get('username'),
                    password: form.get('password'),
                }),
            });
            window.location.reload();
        } catch (error) {
            showFeedback(error.message, true);
        }
    });
}

if (document.body.dataset.authenticated === 'true') {
    initializeDashboard().catch((error) => showFeedback(error.message, true));
} else {
    initializeLogin().catch((error) => showFeedback(error.message, true));
}

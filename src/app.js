const OWNER_LABELS = {
  organization: 'Организация',
  person: 'Физическое лицо'
};

export const archiveObjects = [
  {
    id: 'obj-001',
    cadastralNumber: '77:01:0004010:1542',
    address: 'г. Москва, ул. Лесная, д. 12, офис 54',
    type: 'Нежилое помещение',
    area: 186.4,
    currentOwner: 'ООО «Северный Контур»',
    ownerType: 'organization',
    status: 'complete',
    rightsEvents: [
      {
        date: '2018-04-11',
        action: 'Первичная регистрация права собственности',
        owner: 'ООО «Северный Контур»',
        basis: 'Договор купли-продажи № 18/04-НП',
        registrar: 'Росреестр, управление по Москве',
        documentIds: ['doc-001', 'doc-002']
      },
      {
        date: '2023-09-27',
        action: 'Внесение изменений после перепланировки',
        owner: 'ООО «Северный Контур»',
        basis: 'Технический план после перепланировки',
        registrar: 'Кадастровый инженер А. Н. Волков',
        documentIds: ['doc-003']
      }
    ],
    documents: [
      { id: 'doc-001', title: 'Договор купли-продажи № 18/04-НП', type: 'Правоустанавливающий', date: '2018-04-02', scanStatus: 'Оцифрован', fileName: '77-01-0004010-1542-contract.pdf' },
      { id: 'doc-002', title: 'Выписка ЕГРН', type: 'Регистрационный', date: '2018-04-11', scanStatus: 'Проверен OCR', fileName: '77-01-0004010-1542-egrn.pdf' },
      { id: 'doc-003', title: 'Технический план помещения', type: 'Технический', date: '2023-09-20', scanStatus: 'Оцифрован', fileName: '77-01-0004010-1542-tech-plan.pdf' }
    ]
  },
  {
    id: 'obj-002',
    cadastralNumber: '50:21:0050203:88',
    address: 'Московская область, Одинцовский г. о., д. Подушкино, участок 7',
    type: 'Земельный участок',
    area: 1200,
    currentOwner: 'Иванова Мария Петровна',
    ownerType: 'person',
    status: 'attention',
    rightsEvents: [
      {
        date: '2015-06-18',
        action: 'Переход права по наследству',
        owner: 'Иванова Мария Петровна',
        basis: 'Свидетельство о праве на наследство',
        registrar: 'Нотариус Е. С. Павлова',
        documentIds: ['doc-004']
      },
      {
        date: '2021-02-03',
        action: 'Регистрация ограничения: аренда части участка',
        owner: 'Иванова Мария Петровна',
        basis: 'Договор аренды части участка',
        registrar: 'Росреестр, Московская область',
        documentIds: ['doc-005', 'doc-missing']
      }
    ],
    documents: [
      { id: 'doc-004', title: 'Свидетельство о праве на наследство', type: 'Правоустанавливающий', date: '2015-06-10', scanStatus: 'Оцифрован', fileName: '50-21-0050203-88-inheritance.pdf' },
      { id: 'doc-005', title: 'Договор аренды части участка', type: 'Обременение', date: '2021-01-25', scanStatus: 'Требуется проверка OCR', fileName: '50-21-0050203-88-lease.pdf' }
    ]
  },
  {
    id: 'obj-003',
    cadastralNumber: '78:36:0005355:2401',
    address: 'г. Санкт-Петербург, наб. реки Мойки, д. 31',
    type: 'Здание',
    area: 940.7,
    currentOwner: 'АО «Балтийские склады»',
    ownerType: 'organization',
    status: 'complete',
    rightsEvents: [
      {
        date: '2009-11-30',
        action: 'Приватизация здания',
        owner: 'АО «Балтийские склады»',
        basis: 'Решение комитета имущественных отношений',
        registrar: 'КИО Санкт-Петербурга',
        documentIds: ['doc-006']
      },
      {
        date: '2019-07-16',
        action: 'Регистрация ипотеки',
        owner: 'АО «Балтийские склады»',
        basis: 'Договор ипотеки № 44-И',
        registrar: 'Росреестр, Санкт-Петербург',
        documentIds: ['doc-007', 'doc-008']
      }
    ],
    documents: [
      { id: 'doc-006', title: 'Решение о приватизации', type: 'Правоустанавливающий', date: '2009-11-10', scanStatus: 'Проверен OCR', fileName: '78-36-0005355-2401-privatization.pdf' },
      { id: 'doc-007', title: 'Договор ипотеки № 44-И', type: 'Обременение', date: '2019-07-01', scanStatus: 'Оцифрован', fileName: '78-36-0005355-2401-mortgage.pdf' },
      { id: 'doc-008', title: 'Выписка ЕГРН об ипотеке', type: 'Регистрационный', date: '2019-07-16', scanStatus: 'Оцифрован', fileName: '78-36-0005355-2401-egrn-mortgage.pdf' }
    ]
  }
];

export function formatDate(value, locale = 'ru-RU') {
  return new Intl.DateTimeFormat(locale).format(new Date(`${value}T00:00:00`));
}

export function getDocumentIndex(object) {
  return new Map(object.documents.map((document) => [document.id, document]));
}

export function getTraceabilityIssues(object) {
  const documents = getDocumentIndex(object);
  return object.rightsEvents.flatMap((event) =>
    event.documentIds
      .filter((documentId) => !documents.has(documentId))
      .map((documentId) => ({
        eventDate: event.date,
        eventAction: event.action,
        missingDocumentId: documentId
      }))
  );
}

export function sortEventsByDate(events) {
  return [...events].sort((left, right) => new Date(left.date) - new Date(right.date));
}

export function filterObjects(objects, filters) {
  const query = filters.query.trim().toLocaleLowerCase('ru-RU');
  return objects.filter((object) => {
    const matchesQuery = !query || [
      object.cadastralNumber,
      object.address,
      object.currentOwner,
      object.type
    ].some((value) => value.toLocaleLowerCase('ru-RU').includes(query));
    const matchesOwner = filters.ownerType === 'all' || object.ownerType === filters.ownerType;
    const matchesStatus = filters.status === 'all' || object.status === filters.status;
    return matchesQuery && matchesOwner && matchesStatus;
  });
}

function statusLabel(status) {
  return status === 'complete' ? 'Полное досье' : 'Требует внимания';
}

function renderObjectCard(object, isActive) {
  const issues = getTraceabilityIssues(object);
  return `
    <button class="object-card ${isActive ? 'is-active' : ''}" data-object-id="${object.id}" type="button">
      <span class="object-card__type">${object.type}</span>
      <strong>${object.cadastralNumber}</strong>
      <span>${object.address}</span>
      <span class="object-card__footer">
        <span>${OWNER_LABELS[object.ownerType]}</span>
        <span class="badge ${issues.length ? 'badge--warning' : 'badge--success'}">${statusLabel(object.status)}</span>
      </span>
    </button>
  `;
}

function renderTimeline(object) {
  const documents = getDocumentIndex(object);
  return sortEventsByDate(object.rightsEvents).map((event) => {
    const linkedDocuments = event.documentIds.map((documentId) => documents.get(documentId));
    return `
      <article class="timeline__item">
        <time datetime="${event.date}">${formatDate(event.date)}</time>
        <h4>${event.action}</h4>
        <p><strong>Правообладатель:</strong> ${event.owner}</p>
        <p><strong>Основание:</strong> ${event.basis}</p>
        <p><strong>Регистратор / источник:</strong> ${event.registrar}</p>
        <ul class="document-links">
          ${linkedDocuments.map((document, index) => document
            ? `<li>${document.title} <span>${document.scanStatus}</span></li>`
            : `<li class="missing">Не найден документ: ${event.documentIds[index]}</li>`).join('')}
        </ul>
      </article>
    `;
  }).join('');
}

function renderDocuments(object) {
  return object.documents.map((document) => `
    <tr>
      <td>${document.title}</td>
      <td>${document.type}</td>
      <td>${formatDate(document.date)}</td>
      <td>${document.scanStatus}</td>
      <td><code>${document.fileName}</code></td>
    </tr>
  `).join('');
}

function renderDetails(object) {
  const issues = getTraceabilityIssues(object);
  document.querySelector('#details-status').textContent = statusLabel(object.status);
  document.querySelector('#details-status').className = `badge ${issues.length ? 'badge--warning' : 'badge--success'}`;
  document.querySelector('#object-details').className = 'details-content';
  document.querySelector('#object-details').innerHTML = `
    <div class="summary-grid">
      <div><span>Кадастровый номер</span><strong>${object.cadastralNumber}</strong></div>
      <div><span>Текущий правообладатель</span><strong>${object.currentOwner}</strong></div>
      <div><span>Тип владельца</span><strong>${OWNER_LABELS[object.ownerType]}</strong></div>
      <div><span>Площадь</span><strong>${object.area} м²</strong></div>
    </div>

    ${issues.length ? `<div class="alert"><strong>Разрыв прослеживаемости:</strong> ${issues.map((issue) => `для события «${issue.eventAction}» отсутствует ${issue.missingDocumentId}`).join('; ')}.</div>` : '<div class="alert alert--success">Все события прав связаны с подтверждающими документами.</div>'}

    <h3>История прав</h3>
    <div class="timeline">${renderTimeline(object)}</div>

    <h3>Реестр документов</h3>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Документ</th><th>Тип</th><th>Дата</th><th>Статус</th><th>Файл</th></tr></thead>
        <tbody>${renderDocuments(object)}</tbody>
      </table>
    </div>
  `;
}

function initArchiveApp() {
  const state = {
    selectedId: archiveObjects[0]?.id,
    filters: { query: '', ownerType: 'all', status: 'all' }
  };

  const nodes = {
    search: document.querySelector('#search'),
    ownerType: document.querySelector('#owner-type'),
    status: document.querySelector('#status-filter'),
    reset: document.querySelector('#reset-filters'),
    list: document.querySelector('#objects-list'),
    resultCount: document.querySelector('#result-count')
  };

  function render() {
    const filtered = filterObjects(archiveObjects, state.filters);
    if (!filtered.some((object) => object.id === state.selectedId)) {
      state.selectedId = filtered[0]?.id;
    }

    nodes.resultCount.textContent = `${filtered.length} найдено`;
    nodes.list.innerHTML = filtered.length
      ? filtered.map((object) => renderObjectCard(object, object.id === state.selectedId)).join('')
      : '<p class="empty-state">По заданным фильтрам объекты не найдены.</p>';

    const selected = archiveObjects.find((object) => object.id === state.selectedId);
    if (selected) {
      renderDetails(selected);
    }
  }

  document.querySelector('#objects-count').textContent = archiveObjects.length;
  document.querySelector('#documents-count').textContent = archiveObjects.reduce((total, object) => total + object.documents.length, 0);
  document.querySelector('#risk-count').textContent = archiveObjects.filter((object) => getTraceabilityIssues(object).length > 0).length;

  nodes.search.addEventListener('input', (event) => {
    state.filters.query = event.target.value;
    render();
  });
  nodes.ownerType.addEventListener('change', (event) => {
    state.filters.ownerType = event.target.value;
    render();
  });
  nodes.status.addEventListener('change', (event) => {
    state.filters.status = event.target.value;
    render();
  });
  nodes.reset.addEventListener('click', () => {
    state.filters = { query: '', ownerType: 'all', status: 'all' };
    nodes.search.value = '';
    nodes.ownerType.value = 'all';
    nodes.status.value = 'all';
    render();
  });
  nodes.list.addEventListener('click', (event) => {
    const card = event.target.closest('[data-object-id]');
    if (!card) return;
    state.selectedId = card.dataset.objectId;
    render();
  });

  render();
}

if (typeof document !== 'undefined') {
  initArchiveApp();
}

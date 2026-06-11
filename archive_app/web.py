from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from .domain import (
    ARCHIVE_OBJECTS,
    ROADMAP_ITEMS,
    RealEstateObject,
    RoadmapItem,
    filter_objects,
    get_document_index,
    get_traceability_issues,
    sort_events_by_date,
)

OWNER_LABELS = {
    "all": "Все",
    "organization": "Организация",
    "person": "Физическое лицо",
}

STATUS_LABELS = {
    "all": "Все статусы",
    "complete": "Полное досье",
    "attention": "Требует внимания",
}

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
StartResponse = Callable[[str, list[tuple[str, str]]], None]


@dataclass(frozen=True)
class ArchiveFilters:
    query: str = ""
    owner_type: str = "all"
    status: str = "all"
    selected_id: str = ""

    @classmethod
    def from_query_string(cls, query_string: str) -> "ArchiveFilters":
        params = parse_qs(query_string, keep_blank_values=True)
        return cls(
            query=params.get("q", [""])[0],
            owner_type=_allowed_value(params.get("owner_type", ["all"])[0], OWNER_LABELS, "all"),
            status=_allowed_value(params.get("status", ["all"])[0], STATUS_LABELS, "all"),
            selected_id=params.get("selected_id", [""])[0],
        )


def _allowed_value(value: str, allowed: dict[str, str], fallback: str) -> str:
    return value if value in allowed else fallback


def format_date(value) -> str:
    return value.strftime("%d.%m.%Y")


def status_label(real_estate_object: RealEstateObject) -> str:
    return STATUS_LABELS[real_estate_object.status]


def status_badge_class(real_estate_object: RealEstateObject) -> str:
    return "badge--warning" if get_traceability_issues(real_estate_object) else "badge--success"


def render_page(filters: ArchiveFilters) -> str:
    filtered_objects = filter_objects(
        ARCHIVE_OBJECTS,
        query=filters.query,
        owner_type=filters.owner_type,
        status=filters.status,
    )
    selected = select_object(filtered_objects, filters.selected_id)
    total_documents = sum(len(real_estate_object.documents) for real_estate_object in ARCHIVE_OBJECTS)
    risky_objects = sum(1 for real_estate_object in ARCHIVE_OBJECTS if get_traceability_issues(real_estate_object))

    return f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Архив прав на недвижимость</title>
    <link rel="stylesheet" href="/static/styles.css" />
  </head>
  <body>
    <header class="hero">
      <div>
        <p class="eyebrow">Python-прототип цифрового архива</p>
        <h1>Прослеживаемость прав и подтверждающих документов</h1>
        <p class="hero__text">
          Приложение на Python для перевода бумажного архива объектов недвижимости
          в электронный вид: карточки объектов, история правообладателей,
          цепочки документов и контроль полноты досье.
        </p>
      </div>
      <section class="hero__card" aria-label="Ключевые показатели архива">
        <div><strong>{len(ARCHIVE_OBJECTS)}</strong><span>объекта</span></div>
        <div><strong>{total_documents}</strong><span>документов</span></div>
        <div><strong>{risky_objects}</strong><span>требуют внимания</span></div>
      </section>
    </header>

    <main class="layout">
      {render_filters(filters)}
      {render_objects_list(filtered_objects, selected, filters)}
      {render_details(selected)}
    </main>

    <section class="panel workflow" aria-labelledby="workflow-heading">
      <h2 id="workflow-heading">Процесс оцифровки бумажного архива</h2>
      <ol>
        <li><strong>Регистрация объекта:</strong> кадастровый номер, адрес, тип, площадь.</li>
        <li><strong>Сканирование:</strong> загрузка образов документов и OCR-распознавание.</li>
        <li><strong>Связка с событием права:</strong> каждый документ подтверждает регистрацию, переход, ограничение или прекращение права.</li>
        <li><strong>Проверка полноты:</strong> система подсвечивает отсутствующие документы и разрывы в цепочке правообладателей.</li>
      </ol>
    </section>

    {render_roadmap()}
  </body>
</html>"""


def render_roadmap() -> str:
    cards = "".join(render_roadmap_item(item) for item in ROADMAP_ITEMS)
    return f"""<section class="panel roadmap" aria-labelledby="roadmap-heading">
      <div class="section-title">
        <div>
          <p class="eyebrow">План развития</p>
          <h2 id="roadmap-heading">От прототипа к промышленной системе</h2>
        </div>
        <span class="badge">{len(ROADMAP_ITEMS)} направлений</span>
      </div>
      <p class="roadmap__intro">
        Следующие модули закрывают требования полноценной эксплуатации: безопасность,
        надежное хранение сканов, OCR, аудит, интеграции и версионирование.
      </p>
      <div class="roadmap__grid">{cards}</div>
    </section>"""


def render_roadmap_item(item: RoadmapItem) -> str:
    capabilities = "".join(f"<li>{escape(capability)}</li>" for capability in item.capabilities)
    return f"""<article class="roadmap-card" id="roadmap-{escape(item.id)}">
        <span class="roadmap-card__priority">{escape(item.priority)}</span>
        <h3>{escape(item.title)}</h3>
        <p>{escape(item.description)}</p>
        <ul>{capabilities}</ul>
      </article>"""


def select_object(objects: list[RealEstateObject], selected_id: str) -> RealEstateObject | None:
    for real_estate_object in objects:
        if real_estate_object.id == selected_id:
            return real_estate_object
    return objects[0] if objects else None


def render_filters(filters: ArchiveFilters) -> str:
    owner_options = render_options(OWNER_LABELS, filters.owner_type)
    status_options = render_options(STATUS_LABELS, filters.status)
    return f"""<aside class="panel filters" aria-label="Фильтры объектов">
        <h2>Поиск в архиве</h2>
        <form method="get">
          <label>
            Текстовый поиск
            <input name="q" type="search" value="{escape(filters.query)}" placeholder="Кадастровый номер, адрес, владелец" />
          </label>
          <label>
            Тип правообладателя
            <select name="owner_type">{owner_options}</select>
          </label>
          <label>
            Статус досье
            <select name="status">{status_options}</select>
          </label>
          <button type="submit">Применить фильтры</button>
          <a class="reset-link" href="/">Сбросить фильтры</a>
        </form>
      </aside>"""


def render_options(options: dict[str, str], selected: str) -> str:
    return "".join(
        f'<option value="{escape(value)}" {"selected" if value == selected else ""}>{escape(label)}</option>'
        for value, label in options.items()
    )


def render_objects_list(objects: list[RealEstateObject], selected: RealEstateObject | None, filters: ArchiveFilters) -> str:
    cards = "".join(render_object_card(real_estate_object, selected, filters) for real_estate_object in objects)
    if not cards:
        cards = '<p class="empty-state">По заданным фильтрам объекты не найдены.</p>'

    return f"""<section class="panel objects" aria-labelledby="objects-heading">
        <div class="section-title">
          <h2 id="objects-heading">Объекты недвижимости</h2>
          <span class="badge">{len(objects)} найдено</span>
        </div>
        <div class="objects-list">{cards}</div>
      </section>"""


def render_object_card(real_estate_object: RealEstateObject, selected: RealEstateObject | None, filters: ArchiveFilters) -> str:
    active_class = " is-active" if selected and real_estate_object.id == selected.id else ""
    href = build_object_href(filters, real_estate_object.id)
    return f"""<a class="object-card{active_class}" href="{href}">
      <span class="object-card__type">{escape(real_estate_object.type)}</span>
      <strong>{escape(real_estate_object.cadastral_number)}</strong>
      <span>{escape(real_estate_object.address)}</span>
      <span class="object-card__footer">
        <span>{OWNER_LABELS[real_estate_object.owner_type]}</span>
        <span class="badge {status_badge_class(real_estate_object)}">{status_label(real_estate_object)}</span>
      </span>
    </a>"""


def build_object_href(filters: ArchiveFilters, selected_id: str) -> str:
    query = []
    if filters.query:
        query.append(("q", filters.query))
    if filters.owner_type != "all":
        query.append(("owner_type", filters.owner_type))
    if filters.status != "all":
        query.append(("status", filters.status))
    query.append(("selected_id", selected_id))
    return "/?" + "&".join(f"{key}={escape_url(value)}" for key, value in query)


def escape_url(value: str) -> str:
    from urllib.parse import quote_plus

    return quote_plus(value)


def render_details(real_estate_object: RealEstateObject | None) -> str:
    if real_estate_object is None:
        return """<section class="panel details" aria-live="polite" aria-labelledby="details-heading">
        <div class="section-title"><h2 id="details-heading">Карточка объекта</h2></div>
        <div class="details-empty">Выберите объект слева, чтобы увидеть историю прав и документы.</div>
      </section>"""

    issues = get_traceability_issues(real_estate_object)
    alert = render_issues_alert(issues)
    return f"""<section class="panel details" aria-live="polite" aria-labelledby="details-heading">
        <div class="section-title">
          <h2 id="details-heading">Карточка объекта</h2>
          <span class="badge {status_badge_class(real_estate_object)}">{status_label(real_estate_object)}</span>
        </div>
        <div class="details-content">
          <div class="summary-grid">
            <div><span>Кадастровый номер</span><strong>{escape(real_estate_object.cadastral_number)}</strong></div>
            <div><span>Текущий правообладатель</span><strong>{escape(real_estate_object.current_owner)}</strong></div>
            <div><span>Тип владельца</span><strong>{OWNER_LABELS[real_estate_object.owner_type]}</strong></div>
            <div><span>Площадь</span><strong>{real_estate_object.area:g} м²</strong></div>
          </div>
          {alert}
          <h3>История прав</h3>
          <div class="timeline">{render_timeline(real_estate_object)}</div>
          <h3>Реестр документов</h3>
          <div class="table-wrap">{render_documents_table(real_estate_object)}</div>
        </div>
      </section>"""


def render_issues_alert(issues) -> str:
    if not issues:
        return '<div class="alert alert--success">Все события прав связаны с подтверждающими документами.</div>'

    issue_text = "; ".join(
        f"для события «{escape(issue.event_action)}» отсутствует {escape(issue.missing_document_id)}"
        for issue in issues
    )
    return f'<div class="alert"><strong>Разрыв прослеживаемости:</strong> {issue_text}.</div>'


def render_timeline(real_estate_object: RealEstateObject) -> str:
    documents = get_document_index(real_estate_object)
    items = []
    for event in sort_events_by_date(real_estate_object.rights_events):
        document_links = []
        for document_id in event.document_ids:
            document = documents.get(document_id)
            if document:
                document_links.append(
                    f"<li>{escape(document.title)} <span>{escape(document.scan_status)}</span></li>"
                )
            else:
                document_links.append(f'<li class="missing">Не найден документ: {escape(document_id)}</li>')

        items.append(
            f"""<article class="timeline__item">
          <time datetime="{event.date.isoformat()}">{format_date(event.date)}</time>
          <h4>{escape(event.action)}</h4>
          <p><strong>Правообладатель:</strong> {escape(event.owner)}</p>
          <p><strong>Основание:</strong> {escape(event.basis)}</p>
          <p><strong>Регистратор / источник:</strong> {escape(event.registrar)}</p>
          <ul class="document-links">{''.join(document_links)}</ul>
        </article>"""
        )
    return "".join(items)


def render_documents_table(real_estate_object: RealEstateObject) -> str:
    rows = "".join(
        f"""<tr>
          <td>{escape(document.title)}</td>
          <td>{escape(document.type)}</td>
          <td>{format_date(document.date)}</td>
          <td>{escape(document.scan_status)}</td>
          <td><code>{escape(document.file_name)}</code></td>
        </tr>"""
        for document in real_estate_object.documents
    )
    return f"""<table>
        <thead><tr><th>Документ</th><th>Тип</th><th>Дата</th><th>Статус</th><th>Файл</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>"""


def app(environ, start_response: StartResponse):
    path = environ.get("PATH_INFO", "/")
    if path == "/":
        body = render_page(ArchiveFilters.from_query_string(environ.get("QUERY_STRING", ""))).encode("utf-8")
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))])
        return [body]

    if path == "/static/styles.css":
        body = (STATIC_DIR / "styles.css").read_bytes()
        start_response("200 OK", [("Content-Type", "text/css; charset=utf-8"), ("Content-Length", str(len(body)))])
        return [body]

    body = "Страница не найдена".encode("utf-8")
    start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8"), ("Content-Length", str(len(body)))])
    return [body]


def run(host: str = "127.0.0.1", port: int = 4173) -> None:
    with make_server(host, port, app) as server:
        print(f"Архив недвижимости доступен на http://{host}:{port}")
        server.serve_forever()

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

OwnerType = Literal["organization", "person"]
DossierStatus = Literal["complete", "attention"]
RoleCode = Literal["archivist", "registrar", "lawyer", "auditor"]


@dataclass(frozen=True)
class ArchiveDocument:
    id: str
    title: str
    type: str
    date: date
    scan_status: str
    file_name: str


@dataclass(frozen=True)
class RightsEvent:
    date: date
    action: str
    owner: str
    basis: str
    registrar: str
    document_ids: tuple[str, ...]


@dataclass(frozen=True)
class RealEstateObject:
    id: str
    cadastral_number: str
    address: str
    type: str
    area: float
    current_owner: str
    owner_type: OwnerType
    status: DossierStatus
    rights_events: tuple[RightsEvent, ...]
    documents: tuple[ArchiveDocument, ...]


@dataclass(frozen=True)
class TraceabilityIssue:
    event_date: date
    event_action: str
    missing_document_id: str


@dataclass(frozen=True)
class RoadmapItem:
    id: str
    title: str
    priority: str
    description: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class RoleProfile:
    code: RoleCode
    title: str
    description: str
    permissions: tuple[str, ...]
    can_view_personal_data: bool


ROLE_PROFILES: dict[RoleCode, RoleProfile] = {
    "archivist": RoleProfile(
        code="archivist",
        title="Архивариус",
        description="Оцифровывает бумажные дела, загружает сканы и связывает документы с объектами.",
        permissions=(
            "Загрузка и замена сканов до утверждения",
            "Редактирование реквизитов документов",
            "Просмотр персональных данных правообладателей",
        ),
        can_view_personal_data=True,
    ),
    "registrar": RoleProfile(
        code="registrar",
        title="Регистратор",
        description="Ведет события прав, ограничения, основания регистрации и связи с документами.",
        permissions=(
            "Создание и изменение событий прав",
            "Связка правоустанавливающих документов",
            "Просмотр персональных данных правообладателей",
        ),
        can_view_personal_data=True,
    ),
    "lawyer": RoleProfile(
        code="lawyer",
        title="Юрист",
        description="Проверяет юридическую чистоту цепочки прав и готовит заключения по рискам.",
        permissions=(
            "Просмотр полного досье",
            "Юридическая верификация документов",
            "Формирование замечаний по разрывам прослеживаемости",
        ),
        can_view_personal_data=True,
    ),
    "auditor": RoleProfile(
        code="auditor",
        title="Аудитор",
        description="Контролирует полноту досье и действия пользователей без доступа к лишним персональным данным.",
        permissions=(
            "Просмотр статусов и разрывов прослеживаемости",
            "Экспорт контрольных отчетов",
            "Маскирование персональных данных физических лиц",
        ),
        can_view_personal_data=False,
    ),
}


def get_role_profile(role: str) -> RoleProfile:
    return ROLE_PROFILES.get(role, ROLE_PROFILES["archivist"])


def mask_personal_data(value: str) -> str:
    if not value:
        return "Персональные данные скрыты"
    parts = value.split()
    if len(parts) >= 3:
        return f"{parts[0]} {parts[1][0]}. {parts[2][0]}."
    return "Персональные данные скрыты"


def display_owner_name(owner: str, owner_type: OwnerType, role_profile: RoleProfile) -> str:
    if owner_type == "person" and not role_profile.can_view_personal_data:
        return mask_personal_data(owner)
    return owner


ROADMAP_ITEMS: tuple[RoadmapItem, ...] = (
    RoadmapItem(
        id="roles",
        title="Авторизация и роли",
        priority="Базовый контур безопасности",
        description="Разделение доступа для архивариуса, регистратора, юриста и аудитора.",
        capabilities=(
            "вход пользователей и управление сессиями",
            "права на просмотр, загрузку, проверку и утверждение документов",
            "ограничение доступа к персональным данным физических лиц",
        ),
    ),
    RoadmapItem(
        id="storage",
        title="Хранилище сканов",
        priority="Надежность цифрового фонда",
        description="Загрузка файлов в объектное хранилище с контролем целостности каждого образа.",
        capabilities=(
            "карточка файла с размером, MIME-типом и SHA-256 checksum",
            "антивирусная проверка и запрет подмены после утверждения",
            "резервное копирование и политика хранения оригиналов",
        ),
    ),
    RoadmapItem(
        id="ocr",
        title="OCR и верификация реквизитов",
        priority="Ускорение разбора архива",
        description="Пайплайн распознавания сканов и ручная проверка ключевых реквизитов оператором.",
        capabilities=(
            "извлечение дат, номеров договоров, сторон, кадастровых номеров",
            "очередь документов с низкой уверенностью OCR",
            "сравнение распознанных реквизитов с карточкой объекта",
        ),
    ),
    RoadmapItem(
        id="audit",
        title="Неизменяемый журнал действий",
        priority="Юридическая значимость",
        description="Фиксация всех операций пользователей для последующего аудита и расследований.",
        capabilities=(
            "запись события, пользователя, времени, IP-адреса и измененных полей",
            "цепочка хешей для обнаружения удаления или редактирования записей",
            "экспорт журнала для службы безопасности и аудитора",
        ),
    ),
    RoadmapItem(
        id="integrations",
        title="Интеграции с реестрами",
        priority="Снижение ручного ввода",
        description="Сверка данных с ЕГРН, внутренними реестрами организаций и электронным документооборотом.",
        capabilities=(
            "запрос актуальных выписок и статусов регистрации",
            "проверка контрагентов и организационных реквизитов",
            "прикрепление входящих документов из ЭДО к событию права",
        ),
    ),
    RoadmapItem(
        id="versioning",
        title="Версионирование карточек",
        priority="Прослеживаемость изменений",
        description="История версий объектов и документов с возможностью сравнить состояние до и после правки.",
        capabilities=(
            "черновики и утвержденные версии карточек",
            "сравнение изменений по полям объекта, правообладателя и документа",
            "восстановление предыдущей версии по решению ответственного лица",
        ),
    ),
)


ARCHIVE_OBJECTS: tuple[RealEstateObject, ...] = (
    RealEstateObject(
        id="obj-001",
        cadastral_number="77:01:0004010:1542",
        address="г. Москва, ул. Лесная, д. 12, офис 54",
        type="Нежилое помещение",
        area=186.4,
        current_owner="ООО «Северный Контур»",
        owner_type="organization",
        status="complete",
        rights_events=(
            RightsEvent(
                date=date(2018, 4, 11),
                action="Первичная регистрация права собственности",
                owner="ООО «Северный Контур»",
                basis="Договор купли-продажи № 18/04-НП",
                registrar="Росреестр, управление по Москве",
                document_ids=("doc-001", "doc-002"),
            ),
            RightsEvent(
                date=date(2023, 9, 27),
                action="Внесение изменений после перепланировки",
                owner="ООО «Северный Контур»",
                basis="Технический план после перепланировки",
                registrar="Кадастровый инженер А. Н. Волков",
                document_ids=("doc-003",),
            ),
        ),
        documents=(
            ArchiveDocument("doc-001", "Договор купли-продажи № 18/04-НП", "Правоустанавливающий", date(2018, 4, 2), "Оцифрован", "77-01-0004010-1542-contract.pdf"),
            ArchiveDocument("doc-002", "Выписка ЕГРН", "Регистрационный", date(2018, 4, 11), "Проверен OCR", "77-01-0004010-1542-egrn.pdf"),
            ArchiveDocument("doc-003", "Технический план помещения", "Технический", date(2023, 9, 20), "Оцифрован", "77-01-0004010-1542-tech-plan.pdf"),
        ),
    ),
    RealEstateObject(
        id="obj-002",
        cadastral_number="50:21:0050203:88",
        address="Московская область, Одинцовский г. о., д. Подушкино, участок 7",
        type="Земельный участок",
        area=1200,
        current_owner="Иванова Мария Петровна",
        owner_type="person",
        status="attention",
        rights_events=(
            RightsEvent(
                date=date(2015, 6, 18),
                action="Переход права по наследству",
                owner="Иванова Мария Петровна",
                basis="Свидетельство о праве на наследство",
                registrar="Нотариус Е. С. Павлова",
                document_ids=("doc-004",),
            ),
            RightsEvent(
                date=date(2021, 2, 3),
                action="Регистрация ограничения: аренда части участка",
                owner="Иванова Мария Петровна",
                basis="Договор аренды части участка",
                registrar="Росреестр, Московская область",
                document_ids=("doc-005", "doc-missing"),
            ),
        ),
        documents=(
            ArchiveDocument("doc-004", "Свидетельство о праве на наследство", "Правоустанавливающий", date(2015, 6, 10), "Оцифрован", "50-21-0050203-88-inheritance.pdf"),
            ArchiveDocument("doc-005", "Договор аренды части участка", "Обременение", date(2021, 1, 25), "Требуется проверка OCR", "50-21-0050203-88-lease.pdf"),
        ),
    ),
    RealEstateObject(
        id="obj-003",
        cadastral_number="78:36:0005355:2401",
        address="г. Санкт-Петербург, наб. реки Мойки, д. 31",
        type="Здание",
        area=940.7,
        current_owner="АО «Балтийские склады»",
        owner_type="organization",
        status="complete",
        rights_events=(
            RightsEvent(
                date=date(2009, 11, 30),
                action="Приватизация здания",
                owner="АО «Балтийские склады»",
                basis="Решение комитета имущественных отношений",
                registrar="КИО Санкт-Петербурга",
                document_ids=("doc-006",),
            ),
            RightsEvent(
                date=date(2019, 7, 16),
                action="Регистрация ипотеки",
                owner="АО «Балтийские склады»",
                basis="Договор ипотеки № 44-И",
                registrar="Росреестр, Санкт-Петербург",
                document_ids=("doc-007", "doc-008"),
            ),
        ),
        documents=(
            ArchiveDocument("doc-006", "Решение о приватизации", "Правоустанавливающий", date(2009, 11, 10), "Проверен OCR", "78-36-0005355-2401-privatization.pdf"),
            ArchiveDocument("doc-007", "Договор ипотеки № 44-И", "Обременение", date(2019, 7, 1), "Оцифрован", "78-36-0005355-2401-mortgage.pdf"),
            ArchiveDocument("doc-008", "Выписка ЕГРН об ипотеке", "Регистрационный", date(2019, 7, 16), "Оцифрован", "78-36-0005355-2401-egrn-mortgage.pdf"),
        ),
    ),
)


def get_document_index(real_estate_object: RealEstateObject) -> dict[str, ArchiveDocument]:
    return {document.id: document for document in real_estate_object.documents}


def get_traceability_issues(real_estate_object: RealEstateObject) -> list[TraceabilityIssue]:
    documents = get_document_index(real_estate_object)
    issues: list[TraceabilityIssue] = []
    for event in real_estate_object.rights_events:
        for document_id in event.document_ids:
            if document_id not in documents:
                issues.append(
                    TraceabilityIssue(
                        event_date=event.date,
                        event_action=event.action,
                        missing_document_id=document_id,
                    )
                )
    return issues


def sort_events_by_date(events: tuple[RightsEvent, ...] | list[RightsEvent]) -> list[RightsEvent]:
    return sorted(events, key=lambda event: event.date)


def filter_objects(
    objects: tuple[RealEstateObject, ...] | list[RealEstateObject],
    *,
    query: str = "",
    owner_type: str = "all",
    status: str = "all",
) -> list[RealEstateObject]:
    normalized_query = query.strip().casefold()
    filtered: list[RealEstateObject] = []

    for real_estate_object in objects:
        searchable_values = (
            real_estate_object.cadastral_number,
            real_estate_object.address,
            real_estate_object.current_owner,
            real_estate_object.type,
        )
        matches_query = not normalized_query or any(
            normalized_query in value.casefold() for value in searchable_values
        )
        matches_owner_type = owner_type == "all" or real_estate_object.owner_type == owner_type
        matches_status = status == "all" or real_estate_object.status == status

        if matches_query and matches_owner_type and matches_status:
            filtered.append(real_estate_object)

    return filtered

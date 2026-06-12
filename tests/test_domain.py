from datetime import date
import unittest

from archive_app.domain import (
    ARCHIVE_OBJECTS,
    ROADMAP_ITEMS,
    ROLE_PROFILES,
    RightsEvent,
    display_owner_name,
    get_role_profile,
    filter_objects,
    get_traceability_issues,
    sort_events_by_date,
)


class ArchiveDomainTest(unittest.TestCase):
    def test_complete_object_has_no_traceability_issues(self):
        complete_object = ARCHIVE_OBJECTS[0]

        self.assertEqual(get_traceability_issues(complete_object), [])

    def test_missing_document_is_reported_for_rights_event(self):
        attention_object = ARCHIVE_OBJECTS[1]

        self.assertEqual(len(get_traceability_issues(attention_object)), 1)
        issue = get_traceability_issues(attention_object)[0]
        self.assertEqual(issue.event_date, date(2021, 2, 3))
        self.assertEqual(issue.event_action, "Регистрация ограничения: аренда части участка")
        self.assertEqual(issue.missing_document_id, "doc-missing")

    def test_filter_objects_by_owner_type(self):
        organization_objects = filter_objects(ARCHIVE_OBJECTS, owner_type="organization")

        self.assertEqual(len(organization_objects), 2)
        self.assertTrue(all(item.owner_type == "organization" for item in organization_objects))

    def test_filter_objects_combines_query_and_status(self):
        results = filter_objects(ARCHIVE_OBJECTS, query="подушкино", status="attention")

        self.assertEqual([item.id for item in results], ["obj-002"])

    def test_role_profiles_define_personal_data_access(self):
        auditor = get_role_profile("auditor")
        archivist = get_role_profile("archivist")

        self.assertEqual(len(ROLE_PROFILES), 4)
        self.assertFalse(auditor.can_view_personal_data)
        self.assertTrue(archivist.can_view_personal_data)
        self.assertEqual(get_role_profile("unknown").code, "archivist")

    def test_personal_owner_is_masked_for_auditor(self):
        person_object = ARCHIVE_OBJECTS[1]

        self.assertEqual(
            display_owner_name(person_object.current_owner, person_object.owner_type, get_role_profile("auditor")),
            "Иванова М. П.",
        )
        self.assertEqual(
            display_owner_name(person_object.current_owner, person_object.owner_type, get_role_profile("lawyer")),
            "Иванова Мария Петровна",
        )

    def test_roadmap_contains_operational_development_tracks(self):
        titles = {item.title for item in ROADMAP_ITEMS}

        self.assertEqual(len(ROADMAP_ITEMS), 6)
        self.assertIn("Авторизация и роли", titles)
        self.assertIn("Хранилище сканов", titles)
        self.assertIn("OCR и верификация реквизитов", titles)
        self.assertTrue(all(item.capabilities for item in ROADMAP_ITEMS))

    def test_sort_events_by_date(self):
        events = [
            RightsEvent(date(2024, 1, 1), "", "", "", "", ()),
            RightsEvent(date(2020, 1, 1), "", "", "", "", ()),
            RightsEvent(date(2022, 1, 1), "", "", "", "", ()),
        ]

        self.assertEqual(
            [event.date for event in sort_events_by_date(events)],
            [date(2020, 1, 1), date(2022, 1, 1), date(2024, 1, 1)],
        )


if __name__ == "__main__":
    unittest.main()

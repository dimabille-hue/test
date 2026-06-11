import assert from 'node:assert/strict';
import {
  archiveObjects,
  filterObjects,
  getTraceabilityIssues,
  sortEventsByDate
} from '../src/app.js';

const [completeObject, attentionObject] = archiveObjects;

assert.equal(getTraceabilityIssues(completeObject).length, 0, 'complete object has no missing document links');
assert.deepEqual(getTraceabilityIssues(attentionObject), [
  {
    eventDate: '2021-02-03',
    eventAction: 'Регистрация ограничения: аренда части участка',
    missingDocumentId: 'doc-missing'
  }
]);

const organizationObjects = filterObjects(archiveObjects, {
  query: '',
  ownerType: 'organization',
  status: 'all'
});
assert.equal(organizationObjects.length, 2, 'owner type filter returns organizations');

const addressSearch = filterObjects(archiveObjects, {
  query: 'подушкино',
  ownerType: 'all',
  status: 'attention'
});
assert.equal(addressSearch.length, 1, 'query and status filters can be combined');
assert.equal(addressSearch[0].id, 'obj-002');

const sortedDates = sortEventsByDate([
  { date: '2024-01-01' },
  { date: '2020-01-01' },
  { date: '2022-01-01' }
]).map((event) => event.date);
assert.deepEqual(sortedDates, ['2020-01-01', '2022-01-01', '2024-01-01']);

console.log('Archive domain tests passed');

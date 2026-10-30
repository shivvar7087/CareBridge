import test from 'node:test'
import assert from 'node:assert/strict'
import { getNonZeroStatusRows, getProgressPercentage } from '../src/utils/dashboard.js'

test('journey progress is derived safely from backend counts', () => {
  assert.equal(getProgressPercentage(2, 3), 67)
  assert.equal(getProgressPercentage(0, 0), 0)
  assert.equal(getProgressPercentage(8, 4), 100)
  assert.equal(getProgressPercentage(-2, 4), 0)
})

test('empty task status rows are omitted from charts', () => {
  assert.deepEqual(getNonZeroStatusRows([{ name: 'Completed', value: 1 }, { name: 'Pending', value: 0 }]), [{ name: 'Completed', value: 1 }])
})

import { useState } from 'react'
import { Plus, Trash2, Edit3, X, Check, Pill, Clock } from 'lucide-react'
import api, { errorMessage } from '../api'

const TIME_SLOTS = ['Morning', 'Afternoon', 'Evening', 'Bedtime']

export default function MedicationScheduleModal({ isOpen, onClose, schedule, onUpdated }) {
  const [editingId, setEditingId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [isAdding, setIsAdding] = useState(false)
  const [newForm, setNewForm] = useState({
    name: '',
    dosage: '',
    time_slot: 'Morning',
    time_label: '08:00 AM',
    instructions: '',
    indication: '',
  })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  if (!isOpen) return null

  function startEdit(med) {
    setEditingId(med.id)
    setEditForm({
      name: med.name,
      dosage: med.dosage,
      time_slot: med.time_slot,
      time_label: med.time_label,
      instructions: med.instructions,
      indication: med.indication || '',
    })
    setIsAdding(false)
  }

  async function handleSaveEdit(medId) {
    setBusy(true)
    setError('')
    try {
      await api.put(`/copilot/medications/${medId}`, editForm)
      setEditingId(null)
      onUpdated?.()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  async function handleDelete(medId, name) {
    if (!window.confirm(`Are you sure you want to remove '${name}' from your prescription schedule?`)) {
      return
    }
    setBusy(true)
    setError('')
    try {
      await api.delete(`/copilot/medications/${medId}`)
      onUpdated?.()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  async function handleAdd(e) {
    e.preventDefault()
    if (!newForm.name.trim() || !newForm.dosage.trim()) return
    setBusy(true)
    setError('')
    try {
      await api.post('/copilot/medications', newForm)
      setNewForm({
        name: '',
        dosage: '',
        time_slot: 'Morning',
        time_label: '08:00 AM',
        instructions: '',
        indication: '',
      })
      setIsAdding(false)
      onUpdated?.()
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card med-schedule-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <div>
            <div className="eyebrow">CARE COORDINATION</div>
            <h2>Manage Prescription Schedule</h2>
          </div>
          <button className="icon-link" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {error && <div className="form-error">{error}</div>}

        <div className="med-modal-body">
          <div className="med-modal-action-bar">
            <span>Current prescribed doses: <strong>{schedule?.length || 0}</strong></span>
            {!isAdding && (
              <button
                type="button"
                className="button button-small button-primary"
                onClick={() => {
                  setIsAdding(true)
                  setEditingId(null)
                }}
              >
                <Plus size={14} /> Add Medication
              </button>
            )}
          </div>

          {/* Add New Medication Form */}
          {isAdding && (
            <form className="med-edit-card add-card" onSubmit={handleAdd}>
              <div className="edit-card-title">
                <Pill size={16} /> <strong>Add New Prescription</strong>
              </div>
              <div className="med-form-grid">
                <label className="field">
                  <span>Medicine Name</span>
                  <input
                    required
                    placeholder="e.g. Amoxicillin"
                    value={newForm.name}
                    onChange={(e) => setNewForm({ ...newForm, name: e.target.value })}
                  />
                </label>
                <label className="field">
                  <span>Dosage</span>
                  <input
                    required
                    placeholder="e.g. 500 mg, 1 tablet"
                    value={newForm.dosage}
                    onChange={(e) => setNewForm({ ...newForm, dosage: e.target.value })}
                  />
                </label>
                <label className="field">
                  <span>Time Slot</span>
                  <select
                    value={newForm.time_slot}
                    onChange={(e) => setNewForm({ ...newForm, time_slot: e.target.value })}
                  >
                    {TIME_SLOTS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </label>
                <label className="field">
                  <span>Time (Clock)</span>
                  <input
                    placeholder="e.g. 08:00 AM"
                    value={newForm.time_label}
                    onChange={(e) => setNewForm({ ...newForm, time_label: e.target.value })}
                  />
                </label>
                <label className="field span-two">
                  <span>Instructions</span>
                  <input
                    placeholder="e.g. Take after breakfast with a full glass of water"
                    value={newForm.instructions}
                    onChange={(e) => setNewForm({ ...newForm, instructions: e.target.value })}
                  />
                </label>
              </div>
              <div className="edit-actions">
                <button
                  type="button"
                  className="button button-quiet button-small"
                  onClick={() => setIsAdding(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="button button-primary button-small"
                  disabled={busy}
                >
                  {busy ? 'Adding…' : 'Save Prescription'}
                </button>
              </div>
            </form>
          )}

          {/* List of Current Prescriptions */}
          <div className="med-schedule-list">
            {schedule?.map((med) => (
              <div className="med-item-card" key={med.id}>
                {editingId === med.id ? (
                  <div className="med-edit-card">
                    <div className="edit-card-title">
                      <Edit3 size={15} /> <strong>Edit {med.name}</strong>
                    </div>
                    <div className="med-form-grid">
                      <label className="field">
                        <span>Medicine Name</span>
                        <input
                          value={editForm.name}
                          onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                        />
                      </label>
                      <label className="field">
                        <span>Dosage</span>
                        <input
                          value={editForm.dosage}
                          onChange={(e) => setEditForm({ ...editForm, dosage: e.target.value })}
                        />
                      </label>
                      <label className="field">
                        <span>Time Slot</span>
                        <select
                          value={editForm.time_slot}
                          onChange={(e) => setEditForm({ ...editForm, time_slot: e.target.value })}
                        >
                          {TIME_SLOTS.map((s) => (
                            <option key={s} value={s}>{s}</option>
                          ))}
                        </select>
                      </label>
                      <label className="field">
                        <span>Time Label</span>
                        <input
                          value={editForm.time_label}
                          onChange={(e) => setEditForm({ ...editForm, time_label: e.target.value })}
                        />
                      </label>
                      <label className="field span-two">
                        <span>Instructions</span>
                        <input
                          value={editForm.instructions}
                          onChange={(e) => setEditForm({ ...editForm, instructions: e.target.value })}
                        />
                      </label>
                    </div>
                    <div className="edit-actions">
                      <button
                        type="button"
                        className="button button-quiet button-small"
                        onClick={() => setEditingId(null)}
                      >
                        Cancel
                      </button>
                      <button
                        type="button"
                        className="button button-primary button-small"
                        onClick={() => handleSaveEdit(med.id)}
                        disabled={busy}
                      >
                        {busy ? 'Saving…' : 'Update'}
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="med-item-display">
                    <div className="med-item-left">
                      <span className={`med-slot-badge slot-${med.time_slot.toLowerCase()}`}>
                        {med.time_slot} ({med.time_label})
                      </span>
                      <div className="med-name-lockup">
                        <strong>{med.name}</strong>
                        <span className="med-dosage-text">{med.dosage}</span>
                      </div>
                      <small className="med-inst-text">{med.instructions || 'No specific food instructions'}</small>
                    </div>
                    <div className="med-item-actions">
                      <button
                        type="button"
                        className="icon-btn-subtle"
                        onClick={() => startEdit(med)}
                        title="Edit prescription dosage or time"
                        aria-label={`Edit ${med.name}`}
                      >
                        <Edit3 size={15} />
                      </button>
                      <button
                        type="button"
                        className="icon-btn-subtle btn-danger-icon"
                        onClick={() => handleDelete(med.id, med.name)}
                        title="Delete from schedule"
                        aria-label={`Delete ${med.name}`}
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="modal-footnote">
            Prescriptions should match clinician discharge instructions. Verify any modifications with your doctor.
          </div>
        </div>
      </div>
    </div>
  )
}

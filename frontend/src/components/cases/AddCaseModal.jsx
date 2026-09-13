import React, { useState } from 'react';
import { Modal } from '../common/Modal';
import { Button } from '../common/Button';

export const AddCaseModal = ({ isOpen, onClose, onCaseAdded }) => {
  const [formData, setFormData] = useState({
    title: '',
    caseNumber: '',
    client: '',
    opposingParty: '',
    court: 'High Court of Commercial Jurisdiction, Bench IV',
    caseType: 'Commercial Contracts & Maritime Liens',
    status: 'Active',
    priority: 'normal',
    nextHearing: '',
    description: '',
    notes: ''
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validate = () => {
    const errs = {};
    if (!formData.title.trim()) errs.title = "Matter title is required";
    if (!formData.client.trim()) errs.client = "Client name is required";
    if (!formData.court.trim()) errs.court = "Court / Forum is required";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      onCaseAdded(formData);
      onClose();
    }, 350);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Add New Matter"
      subtitle="Register a new case or contentious matter in the chambers database"
      maxWidth="640px"
    >
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
        
        {/* Row 1: Title */}
        <div>
          <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Matter / Case Title <span style={{ color: 'var(--color-error-text)' }}>*</span>
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="e.g. Apex Holdings v. Meridian Logistics"
            className="input-base"
            style={{ borderColor: errors.title ? 'var(--color-error-text)' : undefined }}
          />
          {errors.title && <span style={{ fontSize: '11px', color: 'var(--color-error-text)', marginTop: '2px', display: 'block' }}>{errors.title}</span>}
        </div>

        {/* Row 2: Case Number & Client */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Docket / Case Number
            </label>
            <input
              type="text"
              name="caseNumber"
              value={formData.caseNumber}
              onChange={handleChange}
              placeholder="e.g. 2026-CV-4102 (Leave blank to auto-generate)"
              className="input-base"
              style={{ fontFamily: 'var(--font-mono)' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Client Name <span style={{ color: 'var(--color-error-text)' }}>*</span>
            </label>
            <input
              type="text"
              name="client"
              value={formData.client}
              onChange={handleChange}
              placeholder="e.g. Julian Martinez"
              className="input-base"
              style={{ borderColor: errors.client ? 'var(--color-error-text)' : undefined }}
            />
            {errors.client && <span style={{ fontSize: '11px', color: 'var(--color-error-text)', marginTop: '2px', display: 'block' }}>{errors.client}</span>}
          </div>
        </div>

        {/* Row 3: Opposing Party & Court */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Opposing Party
            </label>
            <input
              type="text"
              name="opposingParty"
              value={formData.opposingParty}
              onChange={handleChange}
              placeholder="e.g. State Prosecutor / Opposing Corp"
              className="input-base"
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Court / Tribunal <span style={{ color: 'var(--color-error-text)' }}>*</span>
            </label>
            <input
              type="text"
              name="court"
              value={formData.court}
              onChange={handleChange}
              placeholder="e.g. High Court Commercial Division"
              className="input-base"
              style={{ borderColor: errors.court ? 'var(--color-error-text)' : undefined }}
            />
            {errors.court && <span style={{ fontSize: '11px', color: 'var(--color-error-text)', marginTop: '2px', display: 'block' }}>{errors.court}</span>}
          </div>
        </div>

        {/* Row 4: Case Type, Status & Priority */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 'var(--space-md)' }}>
          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Case Type
            </label>
            <select
              name="caseType"
              value={formData.caseType}
              onChange={handleChange}
              className="input-base"
            >
              <option>Commercial Contracts & Liens</option>
              <option>Substantive Criminal Law (BNS/BNSS)</option>
              <option>Succession & Probate</option>
              <option>Arbitration & Enforcement</option>
              <option>Tort & Public Liability</option>
              <option>Constitutional & Writ</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Initial Status
            </label>
            <select
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="input-base"
            >
              <option>Active</option>
              <option>Urgent</option>
              <option>Pending</option>
              <option>Upcoming</option>
              <option>Closed</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
              Priority Level
            </label>
            <select
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              className="input-base"
            >
              <option value="normal">Standard Priority</option>
              <option value="urgent">Urgent Priority</option>
            </select>
          </div>
        </div>

        {/* Row 5: Next Hearing Date */}
        <div>
          <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Next Hearing / Filing Deadline
          </label>
          <input
            type="text"
            name="nextHearing"
            value={formData.nextHearing}
            onChange={handleChange}
            placeholder="e.g. 2026-09-28 10:30 AM"
            className="input-base"
          />
        </div>

        {/* Row 6: Description */}
        <div>
          <label style={{ display: 'block', fontSize: 'var(--text-label)', fontWeight: 500, color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
            Matter Synopsis & Objectives
          </label>
          <textarea
            name="description"
            rows={3}
            value={formData.description}
            onChange={handleChange}
            placeholder="Brief procedural background, key relief sought, or initial instructions…"
            className="input-base"
            style={{ resize: 'vertical' }}
          />
        </div>

        {/* Form Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 'var(--space-sm)', marginTop: 'var(--space-xs)' }}>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" type="submit" loading={loading}>
            Create Matter
          </Button>
        </div>
      </form>
    </Modal>
  );
};

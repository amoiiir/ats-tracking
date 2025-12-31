import React from "react";
import type { JobStatus } from "../routes/home";

type JobFormProps = {
  form: {
    company: string;
    position: string;
    status: JobStatus;
    dateApplied: string;
    salary: string;
    jobUrl: string;
    remarks: string;
  };

  editingJobId?: string | null;

  onChange: (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) => void;

  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
};

export default function JobForm({
  form,
  editingJobId,
  onChange,
  onSubmit,
}: JobFormProps) {
  return (
    <form
      onSubmit={onSubmit}
      className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
    >
      <input
        name="company"
        placeholder="Company"
        value={form.company}
        onChange={onChange}
        className="border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        required
      />

      <input
        name="position"
        placeholder="Position"
        value={form.position}
        onChange={onChange}
        className="border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        required
      />

      <select
        name="status"
        value={form.status}
        onChange={onChange}
        className="border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="Applied">Applied</option>
        <option value="Interviewing">Interviewing</option>
        <option value="Offered">Offered</option>
        <option value="Rejected">Rejected</option>
      </select>

      <input
        name="dateApplied"
        type="date"
        value={form.dateApplied}
        onChange={onChange}
        className="border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        required
      />

      <input
        name="salary"
        type="number"
        min="0"
        step="0.01"
        placeholder="Salary (optional)"
        value={form.salary}
        onChange={onChange}
        title="Please enter a positive number"
        className="border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <input
        name="jobUrl"
        type="url"
        placeholder="Job URL (e.g., https://example.com)"
        value={form.jobUrl}
        onChange={onChange}
        pattern="https?://.+"
        title="Please enter a valid URL starting with http:// or https://"
        className="border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <textarea
        name="remarks"
        placeholder="Remarks (optional)"
        value={form.remarks}
        onChange={onChange}
        className="border border-gray-300 dark:border-gray-700 rounded-lg px-3 py-2 bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-100 col-span-1 md:col-span-2"
      />

      <button
        type="submit"
        className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition col-span-1 md:col-span-2"
      >
        {editingJobId ? "Update Job" : "Add Job"}
      </button>
    </form>
  );
}

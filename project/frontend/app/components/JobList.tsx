import React, { useState } from "react";
import type { Job } from "../routes/home";
import { Pen, Trash2, Link, Info } from "lucide-react";

type JobListProps = {
  jobs: Job[];
  onDelete: (id: string) => void;
  onEdit: (id: string) => void;
};

export default function JobList({ jobs, onDelete, onEdit }: JobListProps) {
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  const handlePopupClose = () => {
    setSelectedJob(null);
  };

  if (jobs.length === 0) {
    return (
      <p className="text-center text-gray-500 dark:text-gray-400 mt-6">
        No jobs added yet.
      </p>
    );
  }

  return (
    <div className="mt-6 overflow-x-auto">
      <table className="min-w-full border border-gray-200 dark:border-gray-700 table-auto">
        <thead className="bg-violet-200 dark:bg-violet-700">
          <tr>
            <th className="px-4 py-2 text-left text-sm font-bold">Company</th>
            <th className="px-4 py-2 text-left text-sm font-bold">Position</th>
            <th className="px-4 py-2 text-left text-sm font-bold">Status</th>
            <th className="px-4 py-2 text-left text-sm font-bold">
              Date Applied
            </th>
            <th className="px-4 py-2 text-left text-sm font-bold">Job Link</th>
            <th className="px-4 py-2 text-left text-sm font-bold">Actions</th>
          </tr>
        </thead>

        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {jobs.map((job) => (
            <tr
              key={job.id}
              className="hover:bg-gray-50 dark:hover:bg-gray-700 transition"
            >
              <td className="px-4 py-2">{job.company}</td>
              <td className="px-4 py-2">{job.position}</td>
              <td className="px-4 py-2">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium
                    ${
                      job.status === "applied"
                        ? "bg-blue-100 text-blue-700"
                        : job.status === "interviewing"
                          ? "bg-yellow-100 text-yellow-700"
                          : job.status === "offered"
                            ? "bg-green-100 text-green-700"
                            : "bg-red-100 text-red-700"
                    }`}
                >
                  {job.status}
                </span>
              </td>
              <td className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400">
                {new Date(job.date_applied).toLocaleDateString()}
              </td>
              <td className="px-4 py-2 text-sm text-gray-600 dark:text-gray-400">
                {job.job_url ? (
                  <a
                    href={job.job_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline"
                  >
                    Link<Link size={14} />
                  </a>
                ) : (
                  "N/A"
                )}
              </td>
              <td className="px-4 py-2">
                <div className="flex gap-2">
                  <button
                    onClick={() => onEdit(job.id)}
                    className="px-3 py-1 text-sm rounded
                               bg-yellow-400 text-black
                               hover:bg-yellow-500 transition"
                  >
                    <Pen size={16} />
                  </button>
                  <button
                    onClick={() => onDelete(job.id)}
                    className="px-3 py-1 text-sm rounded
                               bg-red-500 text-white
                               hover:bg-red-600 transition"
                  >
                    <Trash2 size={16} />
                  </button>
                  <button
                    onClick={() => setSelectedJob(job)}
                    className="px-3 py-1 text-sm rounded
                               bg-blue-500 text-white
                               hover:bg-blue-600 transition"
                  >
                    <Info size={16} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selectedJob && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={handlePopupClose}
        >
          <div
            className="bg-white dark:bg-gray-800 p-6 rounded shadow-lg"
            onClick={(e) => e.stopPropagation()}
          >
            <h2 className="text-lg font-bold mb-4">Job Details</h2>
            <p>
              <strong>Company:</strong> {selectedJob.company}
            </p>
            <p>
              <strong>Position:</strong> {selectedJob.position}
            </p>
            <p>
              <strong>Status:</strong> {selectedJob.status}
            </p>
            <p>
              <strong>Salary:</strong>{" "}
              {selectedJob.salary
                ? `RM${selectedJob.salary.toLocaleString()}`
                : "N/A"}
            </p>
            <p>
              <strong>Date Applied:</strong>{" "}
              {new Date(selectedJob.date_applied).toLocaleDateString()}
            </p>
            <p>
              <strong>Remarks:</strong> {selectedJob.remarks || "N/A"}
            </p>
            <div className="mt-4 flex justify-end">
              <button
                onClick={handlePopupClose}
                className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

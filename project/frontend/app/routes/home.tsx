import { useEffect, useState } from "react";
import JobForm from "../components/JobForm";
import JobList from "../components/JobList";

export type JobStatus = "applied" | "interviewing" | "rejected" | "offered";

export type Job = {
  id: string;
  company: string;
  position: string;
  status: JobStatus;
  date_applied: string;
  salary?: number;
  job_url?: string;
  remarks?: string;
};

type JobCreatePayload = {
  company: string;
  position: string;
  status: JobStatus;
  date_applied: string;
  salary?: number;
  job_url?: string;
  remarks?: string;
};

type JobFormState = {
  company: string;
  position: string;
  status: JobStatus;
  dateApplied: string;
  salary: string;
  jobUrl: string;
  remarks: string;
};

export default function Home() {
  //popup card
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  
  const [jobs, setJobs] = useState<Job[]>([]);

  const [form, setForm] = useState<JobFormState>({
    company: "",
    position: "",
    status: "applied",
    dateApplied: "",
    salary: "",
    jobUrl: "",
    remarks: "",
  });

  const [editingJobId, setEditingJobId] = useState<string | null>(null);

  // functions

  function handleChange(
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement
    >
  ) {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));
  }

  function handleEdit(jobId: string) {
    const job = jobs.find((j) => j.id === jobId);

    if (!job) return;

    setForm({
      company: job.company,
      position: job.position,
      status: job.status,
      dateApplied: job.date_applied.split("T")[0],
      salary: job.salary ? String(job.salary) : "",
      jobUrl: job.job_url ? job.job_url : "",
      remarks: job.remarks ? job.remarks : "",
    });
    setEditingJobId(jobId);
  }

  useEffect(() => {
    fetch("http://localhost:8000/jobs/")
      .then((res) => res.json())
      .then((data) => {
        console.log("Fetched jobs:", data);
        setJobs(data);
      })
      .catch(console.error);
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    const payload: JobCreatePayload = {
      company: form.company,
      position: form.position,
      status: form.status,
      date_applied: new Date(form.dateApplied).toISOString(),
      salary: form.salary ? Number(form.salary) : undefined,
      job_url: form.jobUrl || undefined,
      remarks: form.remarks || undefined,
    };

    console.log("Submitting payload:", payload); // Log the payload for debugging

    try {
      if (editingJobId) {
        const res = await fetch(`http://localhost:8000/jobs/${editingJobId}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!res.ok) {
          const errorText = await res.text();
          console.error("Error response:", errorText); // Log the error response
          throw new Error(errorText);
        }

        const updatedJob = await res.json();

        setJobs((prev) =>
          prev.map((job) => (job.id === editingJobId ? updatedJob : job))
        );
      } else {
        const res = await fetch("http://localhost:8000/jobs/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (!res.ok) {
          const errorText = await res.text();
          console.error("Error response:", errorText); // Log the error response
          throw new Error(errorText);
        }

        const createdJob = await res.json();
        setJobs((prev) => [...prev, createdJob]);
      }

      resetForm();
      setEditingJobId(null);
    } catch (err) {
      console.error("Submit failed:", err);
    }
  }

  function resetForm() {
    setForm({
      company: "",
      position: "",
      status: "applied",
      dateApplied: "",
      salary: "",
      jobUrl: "",
      remarks: "",
    });
  }

  async function handleDelete(id: string) {
    //alert user before deleting
    if (!confirm("Are you sure you want to delete this job application?")) {
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/jobs/${id}`, {
        method: "DELETE",
      });

      if (!res.ok) {
        const errorText = await res.text();
        console.error("Error response:", errorText); // Log the error response
        throw new Error(errorText);
      }

      setJobs((prev) => prev.filter((job) => job.id !== id));
    } catch (err) {
      console.error("Delete failed:", err);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-10">
      <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 p-6 rounded shadow">
        <h1 className="text-2xl font-bold mb-6 text-gray-800 dark:text-gray-100">
          Job Application Tracker
        </h1>

        <JobForm form={form} editingJobId={editingJobId} onChange={handleChange} onSubmit={handleSubmit} />

        <JobList jobs={jobs} onDelete={handleDelete} onEdit={handleEdit} />
      </div>
    </div>
  );
}

"use client";
import { useState } from "react";
import axios from "axios";

export default function Home() {
  const [files, setFiles] = useState<FileList | null>(null);
  const [job, setJob] = useState<any>(null);

  const upload = async () => {
    if (!files) return;
    const fd = new FormData();
    Array.from(files).forEach((f) => fd.append("files", f));
    const res = await axios.post("http://localhost:8000/jobs", fd);
    setJob(res.data);
    poll(res.data.job_id);
  };

  const poll = async (id: string) => {
    const t = setInterval(async () => {
      const { data } = await axios.get(`http://localhost:8000/jobs/${id}`);
      setJob(data);
      if (data.status !== "RUNNING") clearInterval(t);
    }, 1000);
  };

  return (
    <main style={{ padding: 32 }}>
      <h1>Redeem Image Uploader</h1>
      <input type="file" multiple onChange={(e) => setFiles(e.target.files)} />
      <button onClick={upload} style={{ marginLeft: 8 }}>Upload & Process</button>
      {job && (
        <div style={{ marginTop: 16 }}>
          <p>Job ID: {job.job_id}</p>
          <p>Status: {job.status}</p>
          <progress value={job.progress} max="100" />
        </div>
      )}
    </main>
  );
}
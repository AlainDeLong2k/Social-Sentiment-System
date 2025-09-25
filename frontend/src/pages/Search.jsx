import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import { BootstrapLoader } from "../components/BootstrapLoader";
import { startOnDemandAnalysis, getJobStatus } from "../services/apiService";

export const SearchPage = () => {
  /**
   * A page for users to input a keyword for on-demand analysis.
   * Manages the state for the keyword input, job submission, and polling for results.
   */
  const [keyword, setKeyword] = useState("");
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | loading | processing | found | failed
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // This effect handles the polling logic
  useEffect(() => {
    if (status !== "processing" || !jobId) {
      return;
    }

    const intervalId = setInterval(() => {
      getJobStatus(jobId)
        .then((response) => {
          if (response.status === "completed") {
            clearInterval(intervalId);
            setStatus("completed");

            const resultEntityId = response.result?._id;
            if (resultEntityId) {
              // Navigate to the detail page with the result's entity ID
              navigate(`/analysis/on-demand/${resultEntityId}`);
            } else {
              setError("Analysis completed, but result ID was not found.");
              setStatus("failed");
            }
          } else if (response.status === "failed") {
            clearInterval(intervalId);
            setStatus("failed");
            setError("The analysis job failed. Please try again.");
          }
        })
        .catch((err) => {
          clearInterval(intervalId);
          setStatus("failed");
          setError(
            err.message || "An error occurred while checking job status."
          );
        });
    }, 5000);

    return () => clearInterval(intervalId);
  }, [status, jobId, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!keyword.trim()) {
      setError("Keyword cannot be empty.");
      return;
    }

    setStatus("loading");
    setError(null);

    try {
      const response = await startOnDemandAnalysis(keyword);

      // Handle the two possible responses from the API
      if (response.status === "found") {
        // If found, navigate immediately to the detail page
        setStatus("found");
        navigate(`/analysis/weekly/${response.entity_id}`);
      } else if (response.status === "queued") {
        // If queued, start the polling process
        setJobId(response.job_id);
        setStatus("processing");
      }
    } catch (err) {
      setStatus("failed");
      setError(err.message || "Failed to start the analysis job.");
    }
  };

  const isBusy = status === "loading" || status === "processing";

  return (
    <div>
      <Navbar />
      <div className="container mt-5">
        <div className="row justify-content-center">
          <div className="col-md-10 text-center">
            <h1>Analyze any Topic</h1>
            <p className="lead text-muted">
              Enter a keyword, name, or topic to start a new sentiment analysis.
            </p>

            <form onSubmit={handleSubmit} className="input-group my-4">
              <input
                type="text"
                className="form-control"
                placeholder="e.g., 'iPhone 17'"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                disabled={isBusy}
              />
              <button
                className="btn btn-primary"
                type="submit"
                disabled={isBusy}
              >
                {isBusy ? "Analyzing..." : "Analyze"}
              </button>
            </form>

            {/* Display feedback to the user */}
            {status === "loading" && <BootstrapLoader />}
            {status === "processing" && (
              <div className="alert alert-info">
                New topic detected! Your request is being processed. This may
                take a few minutes. We will redirect you when it's complete.
              </div>
            )}
            {error && <div className="alert alert-danger">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

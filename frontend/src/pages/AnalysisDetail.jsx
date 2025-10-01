import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import { BootstrapLoader } from "../components/BootstrapLoader";
import { BootstrapProgress } from "../components/BootstrapProgress";
import { CommentList } from "../components/CommentList";
import { Chart } from "../components/Chart";
import ReactPlayer from "react-player";
import { AiOutlineArrowDown } from "react-icons/ai";
import { getTrendDetail } from "../services/apiService";

export const AnalysisDetail = () => {
  // Use useParams to get both 'type' and 'entityId' from the URL
  const { type, entityId } = useParams();

  const [details, setDetails] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const divRef = useRef(null);

  useEffect(() => {
    /**
     * Fetches detailed analysis data for the entityId from the URL.
     */
    if (!entityId) return;

    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getTrendDetail(entityId, type);
        setDetails(data);
      } catch (err) {
        setError(err.message || "Failed to fetch details.");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [entityId, type]); // Re-run this effect if either entityId or type changes

  const handleClick = () => {
    divRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  if (isLoading) {
    return (
      <div className="text-center p-5">
        <BootstrapLoader />
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert alert-danger text-center m-5">Error: {error}</div>
    );
  }

  if (!details) {
    return (
      <div className="alert alert-info text-center m-5">
        No details found for this entity.
      </div>
    );
  }

  // Calculate percentages for the progress bar
  const total = details.analysis.total_comments;
  const positive =
    total > 0
      ? ((details.analysis.positive_count / total) * 100).toFixed(2) + "%"
      : "0%";
  const negative =
    total > 0
      ? ((details.analysis.negative_count / total) * 100).toFixed(2) + "%"
      : "0%";
  const neutral =
    total > 0
      ? ((details.analysis.neutral_count / total) * 100).toFixed(2) + "%"
      : "0%";

  // NEW: Construct the Google Trends URL for the link button
  const trendsUrl = `https://trends.google.com/trends/explore?date=now%207-d&gprop=youtube&q=${encodeURIComponent(
    details.keyword
  )}`;

  return (
    <div>
      <Navbar />
      <div className="analysis-person">
        <ReactPlayer
          url={details.representative_video_url}
          controls={true}
          playing={true}
          width="100%"
          height="100%"
          // volume={0.5}
          muted={true}
          loop={true}
        />
        <button className="play-button" onClick={handleClick}>
          Analysis <AiOutlineArrowDown />
        </button>

        <div ref={divRef} className="result">
          <h1>{details.keyword} Analysis</h1>
          <BootstrapProgress
            positive={positive}
            negative={negative}
            neutral={neutral}
          />

          <h1>Interest Over Last 7 Days</h1>
          <div className="carousel">
            {/* Conditional rendering for the chart */}
            {details.interest_over_time &&
            details.interest_over_time.length > 0 ? (
              <Chart chartData={details.interest_over_time} />
            ) : (
              <div className="text-center p-4">
                <p>
                  Live interest data is not available for on-demand analysis.
                </p>
                <a
                  href={trendsUrl}
                  className="btn btn-primary"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  View on Google Trends (YouTube Search)
                </a>
              </div>
            )}
          </div>

          <h1>Newest Comments</h1>
          <div className="container mt-5">
            <div className="row">
              <div className="col-md-4">
                <CommentList
                  title="Newest Positive Comments"
                  comments={details.representative_comments.positive}
                  sentimentType="success" // Bootstrap class for green
                />
              </div>
              <div className="col-md-4">
                <CommentList
                  title="Newest Neutral Comments"
                  comments={details.representative_comments.neutral}
                  sentimentType="secondary" // Bootstrap class for grey
                />
              </div>
              <div className="col-md-4">
                <CommentList
                  title="Newest Negative Comments"
                  comments={details.representative_comments.negative}
                  sentimentType="danger" // Bootstrap class for red
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

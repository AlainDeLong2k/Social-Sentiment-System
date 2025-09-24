import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { Navbar } from "../components/Navbar";
import { BootstrapLoader } from "../components/BootstrapLoader";
import { BootstrapProgress } from "../components/BootstrapProgress";
import { Chart } from "../components/chart";
import ReactPlayer from "react-player";
import { AiOutlineArrowDown } from "react-icons/ai";
import { getTrendDetail } from "../services/apiService";

export const AnalysisDetail = () => {
  // Get the dynamic 'entityId' from the URL
  const { entityId } = useParams();

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
        const data = await getTrendDetail(entityId);
        setDetails(data);
      } catch (err) {
        setError(err.message || "Failed to fetch details.");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [entityId]); // Re-run this effect if the entityId changes

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
            {/* <Chart jsonData={JSON.stringify(details.interest_over_time)} /> */}
            <Chart chartData={details.interest_over_time} />
          </div>

          <h1>Newest Comments</h1>
          {/* You would add components here to display representative_comments */}
        </div>
      </div>
    </div>
  );
};

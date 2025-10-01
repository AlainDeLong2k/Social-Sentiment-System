export const BootstrapProgress = ({ positive, negative, neutral }) => {
  return (
    <div className="pro">
      <div
        className="progress"
        role="progressbar"
        aria-label="Success example 40px high"
        aria-valuenow="25"
        aria-valuemin="0"
        aria-valuemax="100"
        style={{ height: "40px" }}
      >
        <div className="progress-bar bg-success" style={{ width: positive }}>
          POSITIVE: {positive}
        </div>
      </div>
      <div
        className="progress"
        role="progressbar"
        aria-label="Warning example 50px high"
        aria-valuenow="75"
        aria-valuemin="0"
        aria-valuemax="100"
        style={{ height: "40px" }}
      >
        <div
          className="progress-bar bg-secondary text-white"
          style={{ width: neutral }}
        >
          NEUTRAL: {neutral}
        </div>
      </div>
      <div
        className="progress"
        role="progressbar"
        aria-label="Warning example 50px high"
        aria-valuenow="75"
        aria-valuemin="0"
        aria-valuemax="100"
        style={{ height: "40px" }}
      >
        <div className="progress-bar bg-danger" style={{ width: negative }}>
          NEGATIVE: {negative}
        </div>
      </div>
      <br />
    </div>
  );
};

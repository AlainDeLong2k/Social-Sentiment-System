export const CommentList = ({ title, comments, sentimentType }) => {
  /**
   * A component to display a list of comments for a specific sentiment.
   */
  if (!comments || comments.length === 0) {
    return null; // Don't render anything if there are no comments
  }

  // Assign a specific CSS class based on the sentiment for styling
  const cardHeaderClass = `card-header text-white bg-${sentimentType} d-flex justify-content-between align-items-center gap-2`;

  return (
    <div className="mb-4">
      <h3 className="mb-3">{title}</h3>
      {comments.map((comment, index) => (
        <div className="card mb-2" key={index}>
          <div className={cardHeaderClass}>
            <strong>{comment.author || "Anonymous"}</strong>

            <small>
              {new Date(comment.publish_date).toLocaleDateString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </small>
          </div>
          <div className="card-body">
            <p className="card-text">{comment.text}</p>
          </div>
        </div>
      ))}
    </div>
  );
};

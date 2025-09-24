import { useRef } from "react";
import { Navbar } from "../components/Navbar";
import { Person } from "./Person";
import { BootstrapLoader } from "../components/BootstrapLoader";
import { useData } from "../contexts/DataContext";
import { AiOutlineArrowDown } from "react-icons/ai";
import socialSentiment from "../assets/social-sentiment.jpg";

export const Home = () => {
  const { entities, isLoading, error } = useData();
  const ref = useRef(null);

  const handleClick = () => {
    ref.current?.scrollIntoView({ behavior: "smooth" });
  };

  const renderContent = () => {
    /**
     * Renders the main content based on the current loading and error state.
     */
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

    if (entities.length === 0) {
      return (
        <div className="alert alert-info text-center m-5">
          No trending entities found.
        </div>
      );
    }

    return <Person persons={entities} />;
  };

  return (
    <div className="Home">
      <Navbar />
      <div className="video">
        <img src={socialSentiment} width="100%" height="100%" />
        <button className="play-button" onClick={handleClick}>
          Scroll-down <AiOutlineArrowDown />
        </button>
      </div>

      <div ref={ref}>
        <h2 className="text-center my-4">Latest Weekly Trends</h2>
        {renderContent()}
      </div>
    </div>
  );
};

import { useEffect, useRef, useState, lazy, Suspense } from "react";
import { Navbar } from "../components/Navbar";
import { AiOutlineArrowDown } from "react-icons/ai";
import ReactPlayer from "react-player";
import { Chart } from "../components/Chart";
import { BootstrapProgress } from "../components/BootstrapProgress";

export const AnalysisDetail = () => {
  const selected = JSON.parse(localStorage.getItem("data"));
  console.log(selected.video);
  const [currData, setCurrData] = useState([]);
  const divRef = useRef(null);
  const configJSON = import.meta.env.VITE_CONFIG_JSON;

  const handleClick = () => {
    divRef.current.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    fetch(configJSON)
      .then((response) => response.json())
      .then((data) => {
        var name = selected.name + "";
        console.log(name);
        const Data = data[name];
        setCurrData(Data);
        console.log(Data);
      })
      .catch((error) => console.error(error));
  }, []);

  const positive = currData.positive + "%";
  const negative = currData.negative + "%";
  const neutral = currData.neutral + "%";

  return (
    <div>
      <Navbar />
      <div className="analysisperson">
        <ReactPlayer
          url={selected.video}
          controls={false}
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
          <h1>{selected.name} Youtube Analysis</h1>
          <BootstrapProgress
            positive={positive}
            negative={negative}
            neutral={neutral}
          />

          <h1>{selected.name} Google Trend Analysis</h1>
          <div className="carousel">
            <Chart jsonData={JSON.stringify(currData["count of tweets"])} />
          </div>
        </div>
      </div>
    </div>
  );
};

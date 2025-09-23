import { useEffect, useRef, useState, lazy, Suspense } from "react";
import { Navbar } from "../components/Navbar";
import { AiOutlineArrowDown } from "react-icons/ai";
import ReactPlayer from "react-player";
import { Chart } from "../components/Chart";
import { BootstrapProgress } from "../components/BootstrapProgress";

export const AnalysisDetail = () => {
  const selected = JSON.parse(localStorage.getItem("data"));
  console.log(selected.video);
  const [cur_data, setcurrdata] = useState([]);
  const divRef = useRef(null);
  const config_json = import.meta.env.VITE_CONFIG_JSON;

  const handleClick = () => {
    divRef.current.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    fetch(config_json)
      .then((response) => response.json())
      .then((data) => {
        var name = selected.name + "";
        console.log(name);
        const Data = data[name];
        setcurrdata(Data);
        console.log(Data);
      })
      .catch((error) => console.error(error));
  }, []);

  const positive = cur_data.positive + "%";
  const negative = cur_data.negative + "%";
  const neutral = cur_data.neutral + "%";

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
            <Chart jsonData={JSON.stringify(cur_data["count of tweets"])} />
          </div>
        </div>
      </div>
    </div>
  );
};

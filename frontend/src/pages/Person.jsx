import { BootstrapCard } from "../components/BootstrapCard";
import { useNavigate } from "react-router-dom";

export const Person = ({ persons }) => {
  var navigate = useNavigate();
  return (
    <div className="persons">
      {persons.map((item, index) => {
        return (
          <div
            key={item.id || index}
            onClick={() => {
              localStorage.setItem("data", JSON.stringify(item));
              navigate("/analysis");
            }}
          >
            <BootstrapCard img={item.image} name={item.name} desc={item.desc} />
          </div>
        );
      })}
    </div>
  );
};

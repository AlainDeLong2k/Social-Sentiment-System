import { BootstrapCard } from "../components/BootstrapCard";
import { useNavigate } from "react-router-dom";

export const Person = ({ persons }) => {
  var navigate = useNavigate();
  return (
    <div className="persons">
      {persons.map((item, index) => {
        return (
          <div
            key={item.entity_id || index}
            onClick={() => {
              navigate(`/analysis/${item._id}`);
            }}
          >
            <BootstrapCard img={item.thumbnail_url} name={item.keyword} />
          </div>
        );
      })}
    </div>
  );
};

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

export const BootstrapCard = ({ img, name }) => {
  return (
    <div>
      <div className="card" style={{ width: "18rem", height: "20rem" }}>
        <img src={img} className="card-img-top" alt=" " />
        <div className="card-body">
          <h5 className="card-title">{name}</h5>
        </div>
      </div>
    </div>
  );
};

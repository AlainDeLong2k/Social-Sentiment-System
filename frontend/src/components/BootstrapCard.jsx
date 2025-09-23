import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";

export const BootstrapCard = ({ img, name, desc }) => {
  return (
    <div>
      <div class="card" style={{ width: "18rem", height: "20rem" }}>
        <img src={img} class="card-img-top" alt=" " />
        <div class="card-body">
          <h5 class="card-title">{name}</h5>
          <p class="card-text"> {desc}</p>
        </div>
      </div>
    </div>
  );
};

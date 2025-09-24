import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import logoBKU from "../assets/bku.png";

export const Navbar = () => {
  return (
    <nav className="navbar navbar-expand-lg bg-dark-subtle">
      <div className="container-fluid">
        <a className="navbar-brand eye" href="/">
          <img src={logoBKU} width="70px" />
        </a>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav">
            <li className="nav-item">
              <a className="nav-link active" aria-current="page" href="/home">
                Home
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="/#/Testapi">
                Want to test API
              </a>
            </li>
            <li className="nav-item">
              <a
                className="nav-link"
                href="https://github.com/Caffeine-Coders/Sentiment-Analysis-Project/blob/main/backend/personanalysis.ipynb"
              >
                View Code
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link" href="https://huggingface.co/AK776161">
                Want to look at the model?
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import logoBKU from "../assets/bku.png";

export const Navbar = () => {
  /**
   * The main navigation bar for the application.
   * Uses the Link component from react-router-dom for client-side navigation.
   */
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
              <Link className="nav-link active" aria-current="page" to="/home">
                Home
              </Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/search">
                Analyze Topic
              </Link>
            </li>
            {/* <li className="nav-item">
              <a
                className="nav-link"
                href={import.meta.env.VITE_GIHUB}
                target="_blank"
                rel="noopener noreferrer"
              >
                View Code
              </a>
            </li> */}
            <li className="nav-item">
              <a
                className="nav-link"
                href={import.meta.env.VITE_HUGGINGFACE}
                target="_blank"
                rel="noopener noreferrer"
              >
                Look at the model
              </a>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

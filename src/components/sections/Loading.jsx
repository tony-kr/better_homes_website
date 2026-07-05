import React, { useEffect, useState } from "react";
import { useLoading } from "../../context/LoadingContext";
import "./Loading.css";

const Loading = ({ percent }) => {
  const { setIsLoading } = useLoading();
  const [loaded, setLoaded] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [clicked, setClicked] = useState(false);

  useEffect(() => {
    if (percent >= 100 && !loaded) {
      const timer1 = setTimeout(() => {
        setLoaded(true);
        const timer2 = setTimeout(() => {
          setIsLoaded(true);
        }, 1000);
        return () => clearTimeout(timer2);
      }, 600);
      return () => clearTimeout(timer1);
    }
  }, [percent, loaded]);

  useEffect(() => {
    if (isLoaded) {
      setClicked(true);
      const timer = setTimeout(() => {
        setIsLoading(false);
      }, 900);
      return () => clearTimeout(timer);
    }
  }, [isLoaded, setIsLoading]);

  const handleMouseMove = (e) => {
    const target = e.currentTarget;
    const rect = target.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    target.style.setProperty("--mouse-x", `${x}px`);
    target.style.setProperty("--mouse-y", `${y}px`);
  };

  return (
    <div className="loading-master-container">
      <div className="loading-header">
        <a href="/#" className="loader-title">Better Homes</a>
        <div className={`loaderGame ${clicked ? "loader-out" : ""}`}>
          <div className="loaderGame-container">
            <div className="loaderGame-in">
              {[...Array(27)].map((_, index) => (
                <div className="loaderGame-line" key={index}></div>
              ))}
            </div>
            <div className="loaderGame-ball"></div>
          </div>
        </div>
      </div>
      <div className="loading-screen">
        <div className="loading-title-text">BETTER</div>
        <div
          className={`loading-wrap ${clicked ? "loading-clicked" : ""}`}
          onMouseMove={handleMouseMove}
        >
          <div className="loading-hover"></div>
          <div className={`loading-button ${loaded ? "loading-complete" : ""}`}>
            <div className="loading-container">
              <div className="loading-content">
                <div className="loading-content-in">
                  Loading <span>{percent}%</span>
                </div>
              </div>
              <div className="loading-box"></div>
            </div>
            <div className="loading-content2">
              <span>Welcome</span>
            </div>
          </div>
        </div>
        <div className="loading-title-text">HOMES</div>
      </div>
    </div>
  );
};

export default Loading;
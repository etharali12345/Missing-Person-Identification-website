import { useState, useEffect } from "react";
import "./circularProgress.css";

export const CircularProgress = ({ value = 0.7, color = "green" }) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  const [displayPercentage, setDisplayPercentage] = useState(0);
  const size = 85;
  const trackWidth = 10;

  const clampedValue = Math.min(Math.max(Number(value) || 0, 0), 1);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setAnimatedValue(clampedValue);

      let current = 0;
      const target = Math.round(clampedValue * 100);
      const interval = setInterval(() => {
        current += 1;
        setDisplayPercentage(current);
        if (current >= target) clearInterval(interval);
      }, 1000 / target);

      return () => clearInterval(interval);
    }, 100);

    return () => clearTimeout(timeout);
  }, [clampedValue]);

  const colorStyles = {
    green: "#00cc66",
    yellow: "#d4c114",
  };

  const currentColor = colorStyles[color] || colorStyles.green;
  const innerSize = size - trackWidth * 2;
  const radius = (size - trackWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - animatedValue * circumference;

  return (
    <>
      <div className="cp-outer" style={{ width: size, height: size }}>
        <div
          className="cp-inner"
          style={{ width: innerSize, height: innerSize }}
        >
          <span className="cp-text" style={{ color: currentColor }}>
            %{displayPercentage}
          </span>
        </div>

        <svg
          className="cp-svg"
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
        >
          <circle
            className="cp-circle"
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={currentColor}
            strokeWidth={trackWidth}
            strokeLinecap="butt"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: "stroke-dashoffset 1s ease-out" }}
          />
        </svg>
      </div>
    </>
  );
};

import "./linearProgress.css";
export const LinearProgress = ({ value = 0.7, color = "green" }) => {
  const clamped = Math.min(Math.max(value, 0), 1);
  const colorMap = { green: "#00cc66", yellow: "#d4c114" };
  const activeColor = colorMap[color] || colorMap.green;

  return (
    <div className="lp-container">
      <div className="lp-track">
        <div
          className="lp-bar"
          style={{
            width: `${clamped * 100}%`,
            backgroundColor: activeColor,
          }}
        />
      </div>
    </div>
  );
};

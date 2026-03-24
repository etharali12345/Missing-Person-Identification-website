import "./confirmButtons.css";

export const ConfirmButtons = ({ matchId, onDecision }) => {
  return (
    <div className="decision-container">
      <button
        className="btn-confirm primary"
        onClick={() => onDecision(matchId, "confirmed")}
      >
        نعم، نفس الشخص
      </button>

      <button
        className="btn-confirm secondary"
        onClick={() => onDecision(matchId, "rejected")}
      >
        لا، شخص مختلف
      </button>
    </div>
  );
};

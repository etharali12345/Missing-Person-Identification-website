import "./confirmButtons.css";

export const ConfirmButtons = ({ matchId, percentage, onDecision }) => {
  return (
    <div className="decision-container">
      <button
        className="btn-confirm primary"
        onClick={() => onDecision(matchId, percentage, "confirmed")}
      >
        نعم، نفس الشخص
      </button>

      <button
        className="btn-confirm secondary"
        onClick={() => onDecision(matchId, percentage, "rejected")}
      >
        لا، شخص مختلف
      </button>
    </div>
  );
};

import "./confirmButtons.css";

export const ConfirmButtons = ({ matchId, foundId, similarity, onDecision }) => {
  return (
    <div className="decision-container">
      <button
        className="btn-confirm primary"
        onClick={() => onDecision(matchId, "confirmed", foundId, similarity)}
      >
        نعم، نفس الشخص
      </button>
      <button
        className="btn-confirm secondary"
        onClick={() => onDecision(matchId, "rejected", foundId, similarity)}
      >
        لا، شخص مختلف
      </button>
    </div>
  );
};
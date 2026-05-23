import { StatusBadge } from "./StatusBadge.jsx";

export function CardImage({ src, alt, status }) {
  return (
    <div className="image-outer-box">
      <div className="image-container">
        <img src={src} alt={alt} className="profile-img" />
      </div>
      <StatusBadge status={status} />
    </div>
  );
}

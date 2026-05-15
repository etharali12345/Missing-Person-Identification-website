import { UserRound, MapPin, Phone, Calendar } from "lucide-react";

export function FoundDetails({ details }) {
  return (
    <>
      {details.full_name && (
        <div className="info-group">
          <div className="label-row">
            <UserRound size={18} className="icon" />
            <span className="label-text">الاسم</span>
          </div>
          <div className="value-text">{details.full_name}</div>
        </div>
      )}

      {(details.age || details.gender) && (
        <div className="info-row-split">
          {details.age && (
            <div className="info-group">
              <span className="label-text">العمر</span>
              <div className="value-text">{details.age}</div>
            </div>
          )}
          {details.gender && (
            <div className="info-group">
              <span className="label-text">الجنس</span>
              <div className="value-text">
                {details.gender === "male" ? "ذكر" : "انثى"}
              </div>
            </div>
          )}
        </div>
      )}

      {details.last_seen_date && (
        <div className="info-group">
          <div className="label-row">
            <Calendar size={18} className="icon" />
            <span className="label-text">تاريخ آخر مشاهدة</span>
          </div>
          <div className="value-text">{details.last_seen_date}</div>
        </div>
      )}

      {details.last_seen_location && (
        <div className="info-group">
          <div className="label-row">
            <MapPin size={18} className="icon" />
            <span className="label-text">آخر مكان شوهد فيه</span>
          </div>
          <div className="value-text faded">{details.last_seen_location}</div>
        </div>
      )}

      {(details.phone_number1 || details.phone_number2) && (
        <div className="info-group">
          <div className="label-row">
            <Phone size={18} className="icon" />
            <span className="label-text"> للتواصل مع ذويه</span>
          </div>
          <div className="value-text contact-row">
            {details.phone_number1 && <span>{details.phone_number1}</span>}
            {details.phone_number1 && details.phone_number2 && <span>أو</span>}
            {details.phone_number2 && <span>{details.phone_number2}</span>}
          </div>
        </div>
      )}
    </>
  );
}

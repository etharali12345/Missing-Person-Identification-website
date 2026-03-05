import { UserRound, MapPin, Phone, Building2 } from "lucide-react";
import "./missingResultFields.css";

export function MissingResultFields({ details }) {
  return (
    <>
      {details.name && (
        <div className="info-group">
          <div className="label-row">
            <UserRound size={18} className="icon" />
            <span className="label-text">الاسم</span>
          </div>
          <div className="value-text">{details.name}</div>
        </div>
      )}

      {(details.approximate_age || details.gender) && (
        <div className="info-row-split">
          {details.approximate_age && (
            <div className="info-group">
              <span className="label-text">العمر التقريبي</span>
              <div className="value-text">{details.approximate_age}</div>
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

      {(details.health_status || details.found_date) && (
        <div className="info-row-split">
          {details.health_status && (
            <div className="info-group">
              <span className="label-text">الحالة</span>
              <div className="value-text">{details.health_status}</div>
            </div>
          )}
          {details.found_date && (
            <div className="info-group">
              <span className="label-text">تاريخ العثور</span>
              <div className="value-text">{details.found_date}</div>
            </div>
          )}
        </div>
      )}

      {details.found_location && (
        <div className="info-group">
          <div className="label-row">
            <MapPin size={18} className="icon" />
            <span className="label-text">مكان العثور</span>
          </div>
          <div className="value-text faded">{details.found_location}</div>
        </div>
      )}

      {details.authority_name && (
        <div className="info-group">
          <div className="label-row">
            <Building2 size={18} className="icon" />
            <span className="label-text">جهة العثور</span>
          </div>
          <div className="value-text faded">{details.authority_name}</div>
        </div>
      )}

      {(details.phone_number1 || details.phone_number2) && (
        <div className="info-group">
          <div className="label-row">
            <Phone size={18} className="icon" />
            <span className="label-text">للتواصل مع الجهة</span>
          </div>
          <div className="value-text contact-row">
            {details.phone_number1 && <span>{details.phone_number1}</span>}
            {details.phone_number1 && details.phone_number2 && <span>او</span>}
            {details.phone_number2 && <span>{details.phone_number2}</span>}
          </div>
        </div>
      )}
    </>
  );
}

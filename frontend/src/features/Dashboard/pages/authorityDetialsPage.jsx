import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Landmark, ArrowRight, FileText, BadgeCheck } from "lucide-react";
import { updateAuthorityStatus } from "../services/AuthorityRegisterService";
import { formatDate } from "../../../utils/formatDate";
import "./authorityDetailsPage.css";

export function AuthorityDetailsPage() {
  const location = useLocation();
  const authority = location.state;

  const navigate = useNavigate();

  const [successMessage, setSuccessMessage] = useState("");
  const [currentStatus, setCurrentStatus] = useState(authority.status);

  if (!authority) {
    return <h2>الجهة غير موجودة</h2>;
  }

  const getStatusText = (status) => {
    switch (status) {
      case "pending":
        return "قيد المراجعة";
      case "approved":
        return "مقبول";
      case "rejected":
        return "مرفوض";
      default:
        return status;
    }
  };

  const handleAction = async (status) => {
    try {
      await updateAuthorityStatus(authority.authority_id, status);
      setCurrentStatus(status);
      setSuccessMessage(
        status === "approved" ? "تم قبول الطلب بنجاح" : "تم رفض الطلب بنجاح",
      );

      setTimeout(() => {
        setSuccessMessage("");
      }, 5000);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container d-flex justify-content-center ">
      <div className="details-card">
        <div className="header-icon-container">
          <div className="header-icon-circle">
            <Landmark size={38} strokeWidth={2.4} />
          </div>
        </div>

        <button
          className="back-button"
          onClick={() => navigate(-1, { state: { refreshNeeded: true } })}
        >
          <ArrowRight size={22} />
        </button>

        <div className="card-header">
          <h2 className="card-title">تفاصيل الجهة الرسمية</h2>
          <div className="id-number">رقم الطلب: {authority.authority_id}</div>
        </div>

        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">اسم الجهة</span>
            <span className="info-value">{authority.authority_name}</span>
          </div>

          <div className="info-item">
            <span className="info-label">حالة الطلب</span>
            <span className="info-value">{getStatusText(currentStatus)}</span>
          </div>

          <div className="info-item">
            <span className="info-label">تصنيف الجهة</span>
            <span className="info-value">
              {authority.authority_type === "service" ? "جهة حكومية" : "منظمة"}
            </span>
          </div>

          <div className="info-item">
            <span className="info-label">تاريخ الطلب</span>
            <span className="info-value">
              {formatDate(authority.created_at)}
            </span>
          </div>

          <div className="info-item">
            <span className="info-label">موقع المقر</span>
            <span className="info-value">{authority.location}</span>
          </div>

          {authority.license_number && (
            <div className="info-item">
              <span className="info-label">رقم تسجيل المنظمة</span>
              <span className="info-value">{authority.license_number}</span>
            </div>
          )}

          <div
            className={`${authority.license_number ? "full-width-item" : "info-item"}`}
          >
            <span className="info-label">البريد الإلكتروني أو الهاتف</span>
            <span className="info-value">{authority.email_or_phone}</span>
          </div>
        </div>

        <div className="doc-section">
          <span className="doc-label">الوثيقة الثبوتية</span>
          <a
            href={authority.document}
            className="btn btn-secondary doc-button"
            target="_blank"
          >
            <FileText size={23} strokeWidth={1.3} /> &nbsp; اضغط لفتح الملف
          </a>
        </div>
        {currentStatus === "pending" && (
          <div className="actions">
            <button
              className="btn btn-success"
              onClick={() => handleAction("approved")}
            >
              قبول
            </button>

            <button
              className="btn btn-reject"
              onClick={() => handleAction("rejected")}
            >
              رفض
            </button>
          </div>
        )}

        {currentStatus === "approved" && (
          <div className="actions">
            <button
              className="btn btn-secondary"
              onClick={() => handleAction("rejected")}
            >
              إلغاء الموافقة
            </button>
          </div>
        )}

        {currentStatus === "rejected" && (
          <div className="actions">
            <button
              className="btn btn-secondary"
              onClick={() => handleAction("approved")}
            >
              التراجع عن الرفض
            </button>
          </div>
        )}

        {successMessage && (
          <div className={`success-message text-success`}>
            {successMessage}
            <BadgeCheck size={25} strokeWidth={2.5} color="#198754" />
          </div>
        )}
      </div>
    </div>
  );
}

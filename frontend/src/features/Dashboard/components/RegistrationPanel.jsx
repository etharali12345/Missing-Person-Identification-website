import "./registrationPanel.css";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { ArrowLeft } from "lucide-react";

export function RegistrationPanel({ authorities, handleStatusChange }) {
  const [filter, setFilter] = useState("all");
  const navigate = useNavigate();

  const filteredData =
    filter === "all"
      ? authorities
      : authorities.filter((item) => item.status === "pending");

  const getStatusDisplay = (status) => {
    switch (status) {
      case "pending":
        return { text: "قيد المراجعة", dot: "#d1d5db" };
      case "approved":
        return { text: "مقبول", dot: "#10b981" };
      case "rejected":
        return { text: "مرفوض", dot: "#b91c1c" };
      default:
        return { text: status, dot: "#000" };
    }
  };

  return (
    <div className="dashboard-container">
      <div className="main-card">
        {/* Header Section */}
        <div className="card-header-custom">
          <h2 className="title-text">لوحة إدارة طلبات تسجيل الجهات الرسمية</h2>
          <div className="filter-group">
            <button
              onClick={() => setFilter("all")}
              className={`filter-btn ${filter === "all" ? "active" : ""}`}
            >
              كل الطلبات
            </button>
            <button
              onClick={() => setFilter("pending")}
              className={`filter-btn ${filter === "pending" ? "active" : ""}`}
            >
              طلبات قيد المراجعة
            </button>
          </div>
        </div>

        <div className="table-scroll-area">
          <table className="custom-table">
            <thead>
              <tr>
                <th>رقم طلب التسجيل</th>
                <th>اسم الجهة</th>
                <th>تصنيف الجهة</th>
                <th>تاريخ الطلب</th>
                <th>حالة الطلب</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((item) => {
                const statusInfo = getStatusDisplay(item.status);
                return (
                  <tr key={item.authority_id}>
                    <td>
                      <div className="id-cell">
                        <span
                          className="status-dot"
                          style={{ backgroundColor: statusInfo.dot }}
                        ></span>
                        <span className="id-text">{item.authority_id}</span>
                      </div>
                    </td>
                    <td className="name-text">{item.authority_name}</td>
                    <td className="type-text">
                      {item.authority_type === "service"
                        ? "جهة حكومية"
                        : item.authority_type === "organization"
                          ? "منظمة"
                          : item.authority_type}
                    </td>
                    <td className="date-text">{item.created_at}</td>
                    <td className="status-text">{statusInfo.text}</td>
                    <td className="action-cell">
                      <button
                        className="more-btn"
                        onClick={() =>
                          navigate("/authorityDetails", {
                            state: item,
                          })
                        }
                      >
                        المزيد <ArrowLeft size={12} />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

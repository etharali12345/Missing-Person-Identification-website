import "./registrationPanel.css";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { ArrowLeft } from "lucide-react";
import { formatDate } from "../../../utils/formatDate";

export function RegistrationPanel({ authorities, getAuthorityById }) {
  const [filter, setFilter] = useState("all");
  const [idInput, setIdInput] = useState("");
  const [idFilter, setIdFilter] = useState("");
  const navigate = useNavigate();

  const filteredData = authorities
    .filter((item) => filter === "all" || item.status === "pending")
    .filter((item) =>
      idFilter === "" ? true : String(item.authority_id).includes(idFilter),
    );

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

  const handleMoreClick = async (item) => {
    try {
      const fullAuthority = await getAuthorityById(item.authority_id);
      navigate("/authorityDetails", { state: fullAuthority });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="dashboard-container">
      <div className="main-card">
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
                    <td className="date-text">{formatDate(item.created_at)}</td>
                    <td className="status-text">{statusInfo.text}</td>
                    <td className="action-cell">
                      <button
                        className="more-btn"
                        onClick={() => handleMoreClick(item)}
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

      <div className="id-filter-box">
        <span className="id-filter-label">رقم الطلب</span>
        <input
          type="text"
          className="id-filter-input"
          value={idInput}
          onChange={(e) => setIdInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") setIdFilter(idInput);
          }}
          placeholder=""
        />
      </div>
    </div>
  );
}

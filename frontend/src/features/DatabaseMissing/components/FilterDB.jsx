import "./filterDB.css";
import { Search, ChevronDown } from "lucide-react";

export function FilterDB({
  nameInput,
  setNameInput,
  statusInput,
  setStatusInput,
  handleFilter,
  isMissing = true,
}) {
  return (
    <div className="filter-wrapper">
      <div className="custom-filter-card">
        <div className="filter-container">
          <div className="filter-search">
            <div className="custom-search-container">
              <input
                type="text"
                className="custom-search-input"
                placeholder={
                  isMissing
                    ? "البحث باستخدام اسم المفقود"
                    : "البحث باستخدام اسم المعثور"
                }
                value={nameInput}
                onChange={(e) => setNameInput(e.target.value)}
              />

              <span className="custom-search-icon">
                <Search size={20} color="#8c8c8c" />
              </span>
            </div>
          </div>

          <div className="filter-status">
            <div className="custom-select-container">
              <select
                className="custom-select-input"
                value={statusInput}
                onChange={(e) => setStatusInput(e.target.value)}
              >
                <option value="">الحالة</option>
                <option value="match">لديه تطابق</option>
                <option value="nomatch">لا يوجد تطابق</option>
              </select>

              <span className="custom-select-chevron">
                <ChevronDown size={25} color="#718096" />
              </span>
            </div>
          </div>

          <div className="filter-button">
            <button onClick={handleFilter} className="custom-submit-btn">
              بحث
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

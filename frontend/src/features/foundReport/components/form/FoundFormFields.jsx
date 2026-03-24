import { UserRound, MapPin, Phone } from "lucide-react";

export function FoundFormFields({ handleInputChange, validated, submitted }) {
  return (
    <div className="row g-2 mb-3">
      <div className="col-8">
        <div className="mb-1">
          <label className="form-label">الاسم</label>
          <div className="input-icon-wrapper">
            {!validated && (
              <span className="input-icon">
                <UserRound size={15} />
              </span>
            )}
            <input
              type="text"
              name="full_name"
              className="form-control"
              placeholder="مثال:احمد محمد احمد"
              onChange={handleInputChange}
              disabled={submitted}
            />
          </div>
        </div>
      </div>

      <div className="col-4">
        <div className="mb-1">
          <label className="form-label">العمر التقريبي</label>
          <input
            type="number"
            name="approximate_age"
            className="form-control"
            placeholder="30"
            onChange={handleInputChange}
            disabled={submitted}
          />
        </div>
      </div>

      <div className="col-12">
        <div className="mb-1">
          <label className="form-label">الحالة الصحية</label>
          <input
            type="text"
            name="health_status"
            className="form-control"
            placeholder="مثال: سليم"
            onChange={handleInputChange}
            disabled={submitted}
          />
        </div>
      </div>

      <div className="col-6">
        <div className="mb-1">
          <label className="form-label">الجنس</label>
          <select
            name="gender"
            className="form-select"
            onChange={handleInputChange}
            defaultValue=""
            disabled={submitted}
          >
            <option value="" disabled>
              اختر الجنس
            </option>
            <option value="male">ذكر</option>
            <option value="female">أنثى</option>
          </select>
        </div>
      </div>

      <div className="col-6">
        <div className="mb-1">
          <label className="form-label">تاريخ العثور</label>
          <input
            type="date"
            name="found_date"
            className="form-control"
            onChange={handleInputChange}
            disabled={submitted}
          />
        </div>
      </div>

      <div className="col-12">
        <div className="mb-1">
          <label className="form-label">مكان العثور</label>
          <div className="input-icon-wrapper">
            {!validated && (
              <span className="input-icon" style={{ top: "14px" }}>
                <MapPin size={15} />
              </span>
            )}
            <textarea
              name="found_location"
              className="form-control"
              rows={2}
              placeholder="مثال: تم العثور عليه في امدرمان - الواحة"
              onChange={handleInputChange}
              disabled={submitted}
            />
          </div>
        </div>
      </div>

      <div className="col-6">
        <div className="mb-1">
          <label className="form-label">
            رقم هاتفك للتواصل<span className="text-danger">*</span>
          </label>
          <div className="input-icon-wrapper">
            {!validated && (
              <span className="input-icon">
                <Phone size={15} />
              </span>
            )}
            <input
              type="tel"
              name="phone_number1"
              className="form-control"
              placeholder="249xxxxxxxxx+"
              onChange={handleInputChange}
              disabled={submitted}
              required
              pattern="^\+?[0-9]{7,15}$"
            />
            <div className="invalid-feedback">يرجى إدخال رقم هاتف صحيح</div>
          </div>
        </div>
      </div>

      <div className="col-6">
        <div className="mb-1">
          <label className="form-label">
            رقم آخر للطوارئ<span className="text-danger">*</span>
          </label>
          <div className="input-icon-wrapper">
            {!validated && (
              <span className="input-icon">
                <Phone size={15} />
              </span>
            )}
            <input
              type="tel"
              name="phone_number2"
              className="form-control"
              placeholder="249xxxxxxxxx+"
              onChange={handleInputChange}
              disabled={submitted}
              pattern="^\+?[0-9]{7,15}$"
              required
            />
            <div className="invalid-feedback">يرجى إدخال رقم هاتف صحيح</div>
          </div>
        </div>
      </div>
    </div>
  );
}

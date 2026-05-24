import { UserRound, MapPin, Phone } from "lucide-react";

export function MissingFormFields({ handleInputChange, validated, submitted }) {
  return (
    <div className="row g-2 mb-3">
      <div className="col-9">
        <div className="mb-1">
          <label className="form-label">
            الاسم<span className="text-danger">*</span>
          </label>
          <div className="input-icon-wrapper">
            {!validated && (
              <span className="input-icon">
                <UserRound size={15} />
              </span>
            )}
            <input
              type="text"
              name="name"
              className="form-control"
              placeholder="مثال:احمد محمد احمد"
              onChange={handleInputChange}
              disabled={submitted}
              required
            />
            <div className="invalid-feedback">يرجى إدخال الاسم</div>
          </div>
        </div>
      </div>

      <div className="col-3">
        <div className="mb-1">
          <label className="form-label">
            العمر<span className="text-danger">*</span>
          </label>
          <input
            type="number"
            name="age"
            className="form-control"
            placeholder="30"
            onChange={handleInputChange}
            disabled={submitted}
            required
          />
          <div className="invalid-feedback">ادخل العمر</div>
        </div>
      </div>

      <div className="col-6">
        <div className="mb-1">
          <label className="form-label">
            الجنس<span className="text-danger">*</span>
          </label>
          <select
            name="gender"
            className="form-select"
            onChange={handleInputChange}
            defaultValue=""
            disabled={submitted}
            required
          >
            <option value="" disabled>
              اختر الجنس
            </option>
            <option value="male">ذكر</option>
            <option value="female">أنثى</option>
          </select>
          <div className="invalid-feedback">يرجى اختيار الجنس</div>
        </div>
      </div>

      <div className="col-6">
        <div className="mb-1">
          <label className="form-label">تاريخ آخر ظهور</label>
          <input
            type="date"
            name="last_seen_date"
            className="form-control"
            onChange={handleInputChange}
            disabled={submitted}
          />
        </div>
      </div>

      <div className="col-12">
        <div className="mb-1">
          <label className="form-label">مكان آخر ظهور</label>
          <div className="input-icon-wrapper">
            {!validated && (
              <span className="input-icon" style={{ top: "14px" }}>
                <MapPin size={15} />
              </span>
            )}
            <textarea
              name="last_seen_location"
              className="form-control"
              rows={2}
              placeholder="مثال: شوهد في امدرمان - الواحة"
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
            رقم اخر للطوارئ<span className="text-danger">*</span>
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

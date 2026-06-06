import { Link } from "react-router";

export function Unauthorized() {
  return (
    <div className="d-flex flex-column align-items-center mt-5 p-5">
      <h1>403 - غير مصرح</h1>
      <p>ليس لديك صلاحية للوصول إلى هذه الصفحة</p>
      <Link to="/">العودة للرئيسية</Link>
    </div>
  );
}

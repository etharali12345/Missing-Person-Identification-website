import { Link } from "react-router";

export function Unauthorized() {
  return (
    <div>
      <h1>403 - غير مصرح</h1>
      <p>ليس لديك صلاحية للوصول إلى هذه الصفحة</p>
      <Link to="/">العودة للرئيسية</Link>
    </div>
  );
}

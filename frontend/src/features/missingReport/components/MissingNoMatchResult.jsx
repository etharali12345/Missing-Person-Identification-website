import { Frown } from "lucide-react";
import "./missingNoMatch.css";
export function MissingNoMatchResult() {
  return (
    <div>
      <div className="noMatch">
        <div className="title">لا يوجد تطابق</div>
        <Frown size={180} strokeWidth={1.7} />
        <div className=" p-3 fw-semibold">
          <p className="m-0">
            لم يتم العثور على أي شخص مطابق للصورة التي رفعتها
          </p>
          <p>
            إذا تم العثور على تطابق لاحقا، سيتم تحديث الحالة وستقوم الجهة
            المختصة بالتواصل معك
          </p>
        </div>
      </div>
    </div>
  );
}

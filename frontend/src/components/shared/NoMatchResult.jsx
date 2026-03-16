import { Frown } from "lucide-react";
import "./NoMatchResult.css";

export function NoMatchResult({ message }) {
  return (
    <div>
      <div className="noMatch">
        <div className="title">لا يوجد تطابق</div>
        <Frown size={180} strokeWidth={1.7} />
        <div className="p-3 fw-semibold">
          <p className="m-0">
            لم يتم العثور على أي شخص مطابق للصورة التي رفعتها
          </p>
          <p>{message}</p>
        </div>
      </div>
    </div>
  );
}

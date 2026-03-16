import { ReportPage } from "../../../components/shared/ReportPage";
import { useMissingReport } from "../hooks/useMissingReport";
import { MissingReportForm } from "../components/form/MissingReportForm";
import { MissingDetails } from "../components/result/MissingDetails";

export function MissingReportPage() {
  return (
    <ReportPage
      useReport={useMissingReport}
      FormComponent={MissingReportForm}
      DetailsComponent={MissingDetails}
      noMatchMessage="إذا تم العثور على تطابق لاحقا، سيتم تحديث الحالة وستقوم الجهة المختصة بالتواصل معك"
    />
  );
}

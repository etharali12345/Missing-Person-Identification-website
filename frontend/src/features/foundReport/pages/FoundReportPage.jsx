import { ReportPage } from "../../../components/shared/ReportPage";
import { useFoundReport } from "../hooks/useFoundReport";
import { FoundReportForm } from "../components/form/FoundReportForm";
import { FoundDetails } from "../components/result/FoundDetails";

export function FoundReportPage() {
  return (
    <ReportPage
      useReport={useFoundReport}
      FormComponent={FoundReportForm}
      DetailsComponent={FoundDetails}
      noMatchMessage="إذا تم العثور على تطابق لاحقا، سيتم تحديث الحالة"
    />
  );
}

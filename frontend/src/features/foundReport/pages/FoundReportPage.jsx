import { ReportPage } from "../../../components/shared/ReportPage";
import { useFoundReport } from "../hooks/useFoundReport";
import { FoundReportForm } from "../components/form/FoundReportForm";
import { FoundMatchDetails } from "../components/result/FoundMatchDetails";

export function FoundReportPage() {
  return (
    <ReportPage
      useReport={useFoundReport}
      FormComponent={FoundReportForm}
      DetailsComponent={FoundMatchDetails}
      noMatchMessage="إذا تم العثور على تطابق لاحقا، سيتم تحديث الحالة"
    />
  );
}

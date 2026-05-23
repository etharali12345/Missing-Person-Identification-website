import React, { useEffect } from "react";
import { Upload, Scan, Search, FileCheck } from "lucide-react";
import "./howWeHelp.css";

export function HowWeHelp() {
  return (
    <div dir="rtl" className="app-container py-5 px-3 px-md-5">
      <header className="hero-section container-fluid px-2">
        <h1 className="main-title">
          جسر بين أهالي المفقودين
          <br />
          <span className="main-title-green">والجهات المسؤولة</span>
        </h1>
      </header>

      <main className="container-lg">
        <div className="section-header">
          <h2 className="section-title">كيف يعمل النظام</h2>
          <p className="section-subtitle">
            أربع خطوات بسيطة للبدء في عملية البحث
          </p>
        </div>

        <div className="single-line-row row g-4">
          <div className="single-line-col col">
            <article className="step-card">
              <div className="icon-container">
                <Upload size={24} strokeWidth={2.2} />
              </div>
              <h3 className="card-step-title">رفع صورة واضحة</h3>
              <p className="card-step-desc">
                سجل دخولك أولاً للوصول إلى صفحة رفع الصور ثم قم برفع صورة واضحة
                للشخص الذي تبحث عنه.
              </p>
            </article>
          </div>

          <div className="single-line-col col">
            <article className="step-card">
              <div className="icon-container">
                <Scan size={24} strokeWidth={2.2} />
              </div>
              <h3 className="card-step-title">تحليل الصورة</h3>
              <p className="card-step-desc">
                يقوم النظام بتحليل ملامح الوجه باستخدام تقنيات متقدمة للتعرف على
                الوجه.
              </p>
            </article>
          </div>

          <div className="single-line-col col">
            <article className="step-card">
              <div className="icon-container">
                <Search size={24} strokeWidth={2.2} />
              </div>
              <h3 className="card-step-title">مقارنة البيانات</h3>
              <p className="card-step-desc">
                تتم مقارنة الصورة مع صور الأشخاص الذين تم العثور عليهم والمسجلين
                من قبل الجهات المختصة.
              </p>
            </article>
          </div>

          <div className="single-line-col col">
            <article className="step-card">
              <div className="icon-container">
                <FileCheck size={24} strokeWidth={2.2} />
              </div>
              <h3 className="card-step-title">عرض النتائج والتواصل</h3>
              <p className="card-step-desc">
                في حال وجود تطابق محتمل، يتم عرض بيانات الشخص ومعلومات الجهة
                المسؤولة للتواصل والمتابعة.
              </p>
            </article>
          </div>
        </div>
      </main>
    </div>
  );
}

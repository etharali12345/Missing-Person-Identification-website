import { Users } from "lucide-react";
import "./howWeHelp.css";

export function WhoAreWe() {
  return (
    <div className="app-container py-5 px-3 px-md-5">
      <header className="hero-section container-fluid px-2">
        <h1 className="main-title">
          نعمل معًا لإعادة <span className="main-title-green">لمّ الشمل</span>
        </h1>
      </header>

      <section className="container-lg pt-4">
        <div className="section-header">
          <h2 className="section-title">فريق تطوير الموقع</h2>
          <p className="section-subtitle">يتكون الفريق من ثلاث اعضاء </p>
        </div>

        <div className="team-line-row row g-4 justify-content-center">
          <div className="team-line-col col-12 col-md-6 col-lg-4">
            <article className="team-card">
              <div className="team-image-area">
                <div className="team-avatar-placeholder">
                  <Users size={35} strokeWidth={2} />
                </div>
              </div>
              <div className="team-info-area">
                <h3 className="team-member-name">نمارق الصادق</h3>
                <p className="team-member-role">مطور</p>
              </div>
            </article>
          </div>

          <div className="team-line-col col-12 col-md-6 col-lg-4">
            <article className="team-card">
              <div className="team-image-area">
                <div className="team-avatar-placeholder">
                  <Users size={35} strokeWidth={2} />
                </div>
              </div>
              <div className="team-info-area">
                <h3 className="team-member-name">إيثار علي محمد</h3>
                <p className="team-member-role">مطور</p>
              </div>
            </article>
          </div>

          <div className="team-line-col col-12 col-md-6 col-lg-4">
            <article className="team-card">
              <div className="team-image-area">
                <div className="team-avatar-placeholder">
                  <Users size={35} strokeWidth={2} />
                </div>
              </div>
              <div className="team-info-area">
                <h3 className="team-member-name">روان حسين</h3>
                <p className="team-member-role">مطور</p>
              </div>
            </article>
          </div>
        </div>

        <h5 className="text-center mt-5 text-muted">
          للتواصل معنا يرجى الارسال على البريد الالكتروني:
          <br />
          <span style={{ color: "#08a06d", fontSize: "inherit" }}>
            hopeplatform26@gmail.com
          </span>
        </h5>
      </section>
    </div>
  );
}

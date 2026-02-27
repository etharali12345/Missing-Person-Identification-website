import { useAuth } from "../../context/AuthContext";
import { MainLinks } from "./MainLinks";
import { LoginButton } from "./LoginButton";
import { UserLinks } from "./UserLinks";
import { UserDropdown } from "./UserDropdown";
import { AuthorityLinks } from "./AuthorityLinks";
import { AuthorityDropdown } from "./AuthorityDropdown";
import { AdminLinks } from "./AdminLinks";
import { AdminDropdown } from "./AdminDropdown";
import "./NavBar.css";

export function NavBar() {
  const { loading, user } = useAuth();
  if (loading) return null;

  return (
    <nav className="navbar navbar-expand-lg bg-white custom-navbar py-2 px-2">
      <div className="container-fluid ">
        {/* Right */}
        <div className="logo-width">
          <a className="navbar-brand d-flex align-items-center m-0" href="/">
            <img src="/images/logo.png" alt="الشعار" className="ps-1" />
            <img src="/images/hope.png" alt="الامل" />
          </a>
        </div>

        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="offcanvas"
          data-bs-target="#offcanvasID"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Rest */}
        <div
          className="sidebar offcanvas offcanvas-start"
          id="offcanvasID"
          tabIndex="-1"
        >
          <div className="offcanvas-header border-bottom">
            <h5 className="offcanvas-title">القائمة</h5>
            <button
              type="button"
              className="btn-close ps-4"
              data-bs-dismiss="offcanvas"
              aria-label="Close"
            ></button>
          </div>

          <div className="offcanvas-body d-lg-flex align-items-center w-100">
            {/* Central Pages Coponent*/}
            <ul className="navbar-nav nav-pill-container mx-auto">
              {user?.role === "admin" ? (
                <AdminLinks />
              ) : (
                <>
                  <MainLinks />
                  {user?.role === "user" && <UserLinks />}
                  {user?.role === "authority" && <AuthorityLinks />}
                </>
              )}
            </ul>

            {/*Left side Component*/}
            <div className="logo-width d-flex justify-content-end">
              {!user && <LoginButton />}
              {user?.role === "user" && <UserDropdown />}
              {user?.role === "authority" && <AuthorityDropdown />}
              {user?.role === "admin" && <AdminDropdown />}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

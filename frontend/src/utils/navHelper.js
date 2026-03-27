import { useLocation } from "react-router";

export const activeClass =
  (base) =>
  ({ isActive }) =>
    `${base} ${isActive ? "active-pill" : ""}`;

export const useActiveClass = (base, paths) => {
  const { pathname } = useLocation();
  const isActive = paths.some((path) => pathname.startsWith(path));
  return `${base} ${isActive ? "active-pill" : ""}`;
};

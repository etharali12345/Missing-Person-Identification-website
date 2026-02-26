export const activeClass =
  (base) =>
  ({ isActive }) =>
    `${base} ${isActive ? "active-pill" : ""}`;

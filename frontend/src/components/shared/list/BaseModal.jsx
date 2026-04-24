export function BaseModal({
  show,
  title,
  onCancel,
  children,
  footer,
  direction = "center",
  customClass = "",
}) {
  if (!show) return null;

  return (
    <div
      className="modal fade show d-block"
      style={{ backgroundColor: "rgba(0,0,0,0.6)" }}
      onClick={onCancel}
    >
      <div
        className={`modal-dialog modal-dialog-centered ${customClass}`}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-content text-end">
          <div className="modal-header">
            <h5 className="modal-title w-100">{title}</h5>
          </div>
          <div className="modal-body d-flex flex-column gap-2">{children}</div>
          <div className={`modal-footer justify-content-${direction}`}>
            {footer}
          </div>
        </div>
      </div>
    </div>
  );
}

import "./imagePreview.css";
export function ImageShow({ image }) {
  return (
    <>
      <div className={"imagePreview-container state-has-image"}>
        <div className="w-100 h-100 position-relative">
          <img src={image} alt="Preview" className="preview-image" />
        </div>
      </div>
    </>
  );
}
